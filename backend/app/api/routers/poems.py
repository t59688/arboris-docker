import json
import logging
from typing import Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.dependencies import get_current_user
from ...db.session import get_session
from ...schemas.novel import (
    Blueprint,
    BlueprintGenerationResponse,
    ConverseRequest,
    ConverseResponse,
    NovelProject as NovelProjectSchema,
    NovelProjectSummary,
)
from ...schemas.user import UserInDB
from ...services.llm_service import LLMService
from ...services.novel_service import NovelService
from ...services.prompt_service import PromptService
from ...utils.json_utils import remove_think_tags, sanitize_json_like_text, unwrap_markdown_json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/poems", tags=["Poems"])

POEM_JSON_RESPONSE_INSTRUCTION = """
IMPORTANT: 你的回复必须是合法的 JSON 对象，并严格包含以下字段：
{
  "ai_message": "string",
  "ui_control": {
    "type": "single_choice | text_input | info_display",
    "options": [
      {"id": "option_1", "label": "string"}
    ],
    "placeholder": "string"
  },
  "conversation_state": {},
  "is_complete": false
}
不要输出额外的文本或解释。
"""

POEM_CONCEPT_PROMPT = "poem_concept"
POEM_BLUEPRINT_PROMPT = "poem_blueprint"


def _ensure_prompt(prompt: str | None, name: str) -> str:
    if not prompt:
        raise HTTPException(status_code=500, detail=f"未配置名为 {name} 的提示词，请联系管理员")
    return prompt


@router.post("", response_model=NovelProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_poem_project(
    title: str = Body(...),
    initial_prompt: str = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> NovelProjectSchema:
    novel_service = NovelService(session)
    project = await novel_service.create_project(
        current_user.id,
        title,
        initial_prompt,
        project_type="poem",
    )
    logger.info("用户 %s 创建古诗词项目 %s", current_user.id, project.id)
    return await novel_service.get_project_schema(project.id, current_user.id, project_type="poem")


@router.get("", response_model=List[NovelProjectSummary])
async def list_poem_projects(
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> List[NovelProjectSummary]:
    novel_service = NovelService(session)
    projects = await novel_service.list_projects_for_user(current_user.id, project_type="poem")
    logger.info("用户 %s 获取古诗词项目列表，共 %s 个", current_user.id, len(projects))
    return projects


@router.get("/{project_id}", response_model=NovelProjectSchema)
async def get_poem_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> NovelProjectSchema:
    novel_service = NovelService(session)
    logger.info("用户 %s 查询古诗词项目 %s", current_user.id, project_id)
    return await novel_service.get_project_schema(project_id, current_user.id, project_type="poem")


@router.post("/{project_id}/concept/converse", response_model=ConverseResponse)
async def converse_with_poem_designer(
    project_id: str,
    request: ConverseRequest,
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> ConverseResponse:
    novel_service = NovelService(session)
    prompt_service = PromptService(session)
    llm_service = LLMService(session)

    await novel_service.ensure_project_owner(project_id, current_user.id, project_type="poem")
    history_records = await novel_service.list_conversations(project_id)
    conversation_history = [
        {"role": record.role, "content": record.content}
        for record in history_records
    ]

    user_content = json.dumps(request.user_input, ensure_ascii=False)
    conversation_history.append({"role": "user", "content": user_content})

    system_prompt = _ensure_prompt(
        await prompt_service.get_prompt(POEM_CONCEPT_PROMPT),
        POEM_CONCEPT_PROMPT,
    )
    system_prompt = f"{system_prompt}\n{POEM_JSON_RESPONSE_INSTRUCTION}"

    llm_response = await llm_service.get_llm_response(
        system_prompt=system_prompt,
        conversation_history=conversation_history,
        temperature=0.7,
        user_id=current_user.id,
        timeout=240.0,
    )
    llm_response = remove_think_tags(llm_response)

    try:
        normalized = unwrap_markdown_json(llm_response)
        sanitized = sanitize_json_like_text(normalized)
        parsed = json.loads(sanitized)
    except json.JSONDecodeError as exc:
        logger.exception(
            "Failed to parse poem concept response: project_id=%s user_id=%s error=%s\nOriginal response: %s",
            project_id,
            current_user.id,
            exc,
            llm_response[:1000],
        )
        raise HTTPException(
            status_code=500,
            detail=f"古诗词灵感对话失败，AI 返回内容无法解析。错误详情: {str(exc)}",
        ) from exc

    await novel_service.append_conversation(project_id, "user", user_content)
    await novel_service.append_conversation(project_id, "assistant", normalized)

    if parsed.get("is_complete"):
        parsed["ready_for_blueprint"] = True

    parsed.setdefault("conversation_state", parsed.get("conversation_state", {}))
    return ConverseResponse(**parsed)


@router.post("/{project_id}/blueprint/generate", response_model=BlueprintGenerationResponse)
async def generate_poem_blueprint(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> BlueprintGenerationResponse:
    novel_service = NovelService(session)
    prompt_service = PromptService(session)
    llm_service = LLMService(session)

    project = await novel_service.ensure_project_owner(project_id, current_user.id, project_type="poem")
    history_records = await novel_service.list_conversations(project_id)
    if not history_records:
        raise HTTPException(status_code=400, detail="缺少对话历史，请先完成灵感对话")

    formatted_history: List[Dict[str, str]] = []
    for record in history_records:
        role = record.role
        content = record.content
        if not role or not content:
            continue
        try:
            normalized = unwrap_markdown_json(content)
            data = json.loads(normalized)
            if role == "user":
                user_value = data.get("value", data)
                if isinstance(user_value, str):
                    formatted_history.append({"role": "user", "content": user_value})
            elif role == "assistant":
                ai_message = data.get("ai_message") if isinstance(data, dict) else None
                if ai_message:
                    formatted_history.append({"role": "assistant", "content": ai_message})
        except (json.JSONDecodeError, AttributeError):
            continue

    if not formatted_history:
        raise HTTPException(status_code=400, detail="无法提取有效的对话内容，请重新进行灵感对话")

    system_prompt = _ensure_prompt(
        await prompt_service.get_prompt(POEM_BLUEPRINT_PROMPT),
        POEM_BLUEPRINT_PROMPT,
    )
    blueprint_raw = await llm_service.get_llm_response(
        system_prompt=system_prompt,
        conversation_history=formatted_history,
        temperature=0.35,
        user_id=current_user.id,
        timeout=360.0,
    )
    blueprint_raw = remove_think_tags(blueprint_raw)
    blueprint_normalized = unwrap_markdown_json(blueprint_raw)
    blueprint_sanitized = sanitize_json_like_text(blueprint_normalized)

    try:
        blueprint_data = json.loads(blueprint_sanitized)
    except json.JSONDecodeError as exc:
        logger.error(
            "Poem blueprint generation JSON decode failed: project=%s error=%s",
            project_id,
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail=f"古诗词蓝图生成失败，AI 返回内容无法解析。错误详情: {str(exc)}",
        ) from exc

    blueprint = Blueprint(**blueprint_data)
    await novel_service.replace_blueprint(project_id, blueprint)
    if blueprint.title:
        project.title = blueprint.title
        project.status = "blueprint_ready"
        await session.commit()

    ai_message = "古诗词的创作骨架已经完成。请确认是否满意，或提出新的调整方向。"
    return BlueprintGenerationResponse(blueprint=blueprint, ai_message=ai_message)


@router.post("/{project_id}/blueprint/save", response_model=NovelProjectSchema)
async def save_poem_blueprint(
    project_id: str,
    blueprint_data: Blueprint | None = Body(None),
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> NovelProjectSchema:
    novel_service = NovelService(session)
    project = await novel_service.ensure_project_owner(project_id, current_user.id, project_type="poem")

    if not blueprint_data:
        raise HTTPException(status_code=400, detail="缺少蓝图数据，请提供有效内容")

    await novel_service.replace_blueprint(project_id, blueprint_data)
    if blueprint_data.title:
        project.title = blueprint_data.title
        await session.commit()

    return await novel_service.get_project_schema(project_id, current_user.id, project_type="poem")


@router.post("/{project_id}/generate", response_model=Dict)
async def generate_poem_content(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> Dict:
    """
    根据蓝图生成3个不同版本的诗词作品
    """
    novel_service = NovelService(session)
    prompt_service = PromptService(session)
    llm_service = LLMService(session)

    project = await novel_service.ensure_project_owner(project_id, current_user.id, project_type="poem")
    
    # 检查是否有蓝图
    if not project.blueprint:
        raise HTTPException(status_code=400, detail="项目尚未生成蓝图，请先完成灵感对话并生成蓝图")

    # 获取蓝图数据
    project_schema = await novel_service.get_project_schema(project_id, current_user.id, project_type="poem")
    blueprint_dict = project_schema.blueprint.model_dump()

    # 获取诗词创作提示词
    writing_prompt = await prompt_service.get_prompt("poem_writing")
    if not writing_prompt:
        raise HTTPException(status_code=500, detail="缺少诗词创作提示词，请联系管理员配置 'poem_writing' 提示词")

    # 准备输入数据
    blueprint_json = json.dumps(blueprint_dict, ensure_ascii=False, indent=2)
    user_prompt = f"请根据以下蓝图创作诗词：\n\n{blueprint_json}"

    logger.info("用户 %s 开始为古诗词项目 %s 生成作品", current_user.id, project_id)

    # 生成诗词作品（一次调用生成3个版本）
    try:
        response = await llm_service.get_llm_response(
            system_prompt=writing_prompt,
            conversation_history=[{"role": "user", "content": user_prompt}],
            temperature=0.85,
            user_id=current_user.id,
            timeout=480.0,
        )
        cleaned = remove_think_tags(response)
        normalized = unwrap_markdown_json(cleaned)
        
        try:
            result = json.loads(normalized)
        except json.JSONDecodeError as parse_err:
            logger.warning(
                "项目 %s 诗词生成 JSON 解析失败: %s\n原始内容: %s",
                project_id,
                parse_err,
                normalized[:500],
            )
            raise HTTPException(
                status_code=500,
                detail=f"诗词生成失败，AI返回格式错误: {str(parse_err)}"
            )

        # 验证返回格式
        if not isinstance(result, dict) or "versions" not in result:
            raise HTTPException(
                status_code=500,
                detail="诗词生成失败，返回数据格式不正确"
            )

        versions = result.get("versions", [])
        if not versions or len(versions) < 1:
            raise HTTPException(
                status_code=500,
                detail="诗词生成失败，未返回有效版本"
            )

        logger.info(
            "项目 %s 生成完成，已生成 %s 个版本",
            project_id,
            len(versions),
        )

        # 更新项目状态
        project.status = "poem_generated"
        await session.commit()

        return {
            "status": "success",
            "versions": versions,
            "message": f"成功生成 {len(versions)} 个诗词版本"
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "项目 %s 生成诗词时发生异常: %s",
            project_id,
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail=f"生成诗词失败: {str(exc)[:200]}"
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_poem_projects(
    project_ids: List[str] = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: UserInDB = Depends(get_current_user),
) -> Dict[str, str]:
    novel_service = NovelService(session)
    await novel_service.delete_projects(project_ids, current_user.id, project_type="poem")
    logger.info("用户 %s 删除古诗词项目 %s", current_user.id, project_ids)
    return {"status": "success", "message": f"成功删除 {len(project_ids)} 个古诗词项目"}
