from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

_PREFERRED_CONTENT_KEYS: tuple[str, ...] = (
    "content",
    "chapter_content",
    "chapter_text",
    "full_content",
    "text",
    "body",
    "story",
    "chapter",
    "real_summary",
    "summary",
)


def _normalize_version_content(raw_content: Any, metadata: Any) -> str:
    text = _coerce_text(metadata)
    if not text:
        text = _coerce_text(raw_content)
    return text or ""


def _coerce_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return _clean_string(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in _PREFERRED_CONTENT_KEYS:
            if key in value and value[key]:
                nested = _coerce_text(value[key])
                if nested:
                    return nested
        return _clean_string(json.dumps(value, ensure_ascii=False))
    if isinstance(value, (list, tuple, set)):
        parts = [text for text in (_coerce_text(item) for item in value) if text]
        if parts:
            return "\n".join(parts)
        return None
    return _clean_string(str(value))


def _clean_string(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            parsed = json.loads(stripped)
            coerced = _coerce_text(parsed)
            if coerced:
                return coerced
        except json.JSONDecodeError:
            pass
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2:
        stripped = stripped[1:-1]
    return (
        stripped.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    BlueprintCharacter,
    BlueprintRelationship,
    Chapter,
    ChapterEvaluation,
    ChapterOutline,
    ChapterVersion,
    NovelBlueprint,
    NovelConversation,
    NovelProject,
)
from ..repositories.novel_repository import NovelRepository
from ..schemas.admin import AdminNovelSummary
from ..schemas.novel import (
    Blueprint,
    Chapter as ChapterSchema,
    ChapterGenerationStatus,
    ChapterOutline as ChapterOutlineSchema,
    NovelProject as NovelProjectSchema,
    NovelProjectSummary,
    NovelSectionResponse,
    NovelSectionType,
)


class NovelService:
    """小说项目服务，基于拆表后的结构提供聚合与业务操作。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NovelRepository(session)

    # ------------------------------------------------------------------
    # 项目与摘要
    # ------------------------------------------------------------------
    async def create_project(
        self,
        user_id: int,
        title: str,
        initial_prompt: str,
        project_type: str = "novel",
    ) -> NovelProject:
        project = NovelProject(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            initial_prompt=initial_prompt,
            project_type=project_type,
        )
        blueprint = NovelBlueprint(project=project)
        self.session.add_all([project, blueprint])
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def ensure_project_owner(
        self,
        project_id: str,
        user_id: int,
        project_type: str | None = None,
    ) -> NovelProject:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
        if project_type and project.project_type != project_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目类型不匹配")
        return project

    async def get_project_schema(
        self,
        project_id: str,
        user_id: int,
        project_type: str | None = None,
    ) -> NovelProjectSchema:
        project = await self.ensure_project_owner(project_id, user_id, project_type=project_type)
        return await self._serialize_project(project)

    async def get_section_data(
        self,
        project_id: str,
        user_id: int,
        section: NovelSectionType,
        project_type: str | None = None,
    ) -> NovelSectionResponse:
        project = await self.ensure_project_owner(project_id, user_id, project_type=project_type)
        return self._build_section_response(project, section)

    async def get_chapter_schema(
        self,
        project_id: str,
        user_id: int,
        chapter_number: int,
        project_type: str | None = None,
    ) -> ChapterSchema:
        project = await self.ensure_project_owner(project_id, user_id, project_type=project_type)
        return self._build_chapter_schema(project, chapter_number)

    async def list_projects_for_user(
        self,
        user_id: int,
        project_type: str | None = None,
    ) -> List[NovelProjectSummary]:
        projects = await self.repo.list_by_user(user_id, project_type=project_type)
        summaries: List[NovelProjectSummary] = []
        for project in projects:
            blueprint = project.blueprint
            genre = blueprint.genre if blueprint and blueprint.genre else "未知"
            outlines = project.outlines
            chapters = project.chapters
            total = len(outlines) or len(chapters)
            completed = sum(1 for chapter in chapters if chapter.selected_version_id)
            summaries.append(
                NovelProjectSummary(
                    id=project.id,
                    title=project.title,
                    project_type=project.project_type,
                    genre=genre,
                    last_edited=project.updated_at.isoformat() if project.updated_at else "未知",
                    completed_chapters=completed,
                    total_chapters=total,
                )
            )
        return summaries

    async def list_projects_for_admin(self, project_type: str | None = None) -> List[AdminNovelSummary]:
        projects = await self.repo.list_all(project_type=project_type)
        summaries: List[AdminNovelSummary] = []
        for project in projects:
            blueprint = project.blueprint
            genre = blueprint.genre if blueprint and blueprint.genre else "未知"
            outlines = project.outlines
            chapters = project.chapters
            total = len(outlines) or len(chapters)
            completed = sum(1 for chapter in chapters if chapter.selected_version_id)
            owner = project.owner
            summaries.append(
                AdminNovelSummary(
                    id=project.id,
                    title=project.title,
                    project_type=project.project_type,
                    owner_id=owner.id if owner else 0,
                    owner_username=owner.username if owner else "未知",
                    genre=genre,
                    last_edited=project.updated_at.isoformat() if project.updated_at else "",
                    completed_chapters=completed,
                    total_chapters=total,
                )
            )
        return summaries

    async def delete_projects(
        self,
        project_ids: List[str],
        user_id: int,
        project_type: str | None = None,
    ) -> None:
        for pid in project_ids:
            project = await self.ensure_project_owner(pid, user_id, project_type=project_type)
            await self.repo.delete(project)
        await self.session.commit()

    async def count_projects(self) -> int:
        result = await self.session.execute(select(func.count(NovelProject.id)))
        return result.scalar_one()

    # ------------------------------------------------------------------
    # 对话管理
    # ------------------------------------------------------------------
    async def list_conversations(self, project_id: str) -> List[NovelConversation]:
        stmt = (
            select(NovelConversation)
            .where(NovelConversation.project_id == project_id)
            .order_by(NovelConversation.seq.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def append_conversation(self, project_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        result = await self.session.execute(
            select(func.max(NovelConversation.seq)).where(NovelConversation.project_id == project_id)
        )
        current_max = result.scalar()
        next_seq = (current_max or 0) + 1
        convo = NovelConversation(
            project_id=project_id,
            seq=next_seq,
            role=role,
            content=content,
            metadata=metadata,
        )
        self.session.add(convo)
        await self.session.commit()
        await self._touch_project(project_id)

    # ------------------------------------------------------------------
    # 蓝图管理
    # ------------------------------------------------------------------
    async def replace_blueprint(self, project_id: str, blueprint: Blueprint) -> None:
        record = await self.session.get(NovelBlueprint, project_id)
        if not record:
            record = NovelBlueprint(project_id=project_id)
            self.session.add(record)
        record.title = blueprint.title
        record.target_audience = blueprint.target_audience
        record.genre = blueprint.genre
        record.style = blueprint.style
        record.tone = blueprint.tone
        record.one_sentence_summary = blueprint.one_sentence_summary
        record.full_synopsis = blueprint.full_synopsis
        record.world_setting = blueprint.world_setting

        await self.session.execute(delete(BlueprintCharacter).where(BlueprintCharacter.project_id == project_id))
        for index, data in enumerate(blueprint.characters):
            self.session.add(
                BlueprintCharacter(
                    project_id=project_id,
                    name=data.get("name", ""),
                    identity=data.get("identity"),
                    personality=data.get("personality"),
                    goals=data.get("goals"),
                    abilities=data.get("abilities"),
                    relationship_to_protagonist=data.get("relationship_to_protagonist"),
                    extra={k: v for k, v in data.items() if k not in {
                        "name",
                        "identity",
                        "personality",
                        "goals",
                        "abilities",
                        "relationship_to_protagonist",
                    }},
                    position=index,
                )
            )

        await self.session.execute(delete(BlueprintRelationship).where(BlueprintRelationship.project_id == project_id))
        for index, relation in enumerate(blueprint.relationships):
            self.session.add(
                BlueprintRelationship(
                    project_id=project_id,
                    character_from=relation.character_from,
                    character_to=relation.character_to,
                    description=relation.description,
                    position=index,
                )
            )

        await self.session.execute(delete(ChapterOutline).where(ChapterOutline.project_id == project_id))
        for outline in blueprint.chapter_outline:
            self.session.add(
                ChapterOutline(
                    project_id=project_id,
                    chapter_number=outline.chapter_number,
                    title=outline.title,
                    summary=outline.summary,
                )
            )

        await self.session.commit()
        await self._touch_project(project_id)

    async def patch_blueprint(self, project_id: str, patch: Dict) -> None:
        blueprint = await self.session.get(NovelBlueprint, project_id)
        if not blueprint:
            blueprint = NovelBlueprint(project_id=project_id)
            self.session.add(blueprint)

        if "one_sentence_summary" in patch:
            blueprint.one_sentence_summary = patch["one_sentence_summary"]
        if "full_synopsis" in patch:
            blueprint.full_synopsis = patch["full_synopsis"]
        if "world_setting" in patch and patch["world_setting"] is not None:
            # 创建新字典对象以触发 SQLAlchemy 的变更检测
            existing = blueprint.world_setting or {}
            blueprint.world_setting = {**existing, **patch["world_setting"]}
        if "characters" in patch and patch["characters"] is not None:
            await self.session.execute(delete(BlueprintCharacter).where(BlueprintCharacter.project_id == project_id))
            for index, data in enumerate(patch["characters"]):
                self.session.add(
                    BlueprintCharacter(
                        project_id=project_id,
                        name=data.get("name", ""),
                        identity=data.get("identity"),
                        personality=data.get("personality"),
                        goals=data.get("goals"),
                        abilities=data.get("abilities"),
                        relationship_to_protagonist=data.get("relationship_to_protagonist"),
                        extra={k: v for k, v in data.items() if k not in {
                            "name",
                            "identity",
                            "personality",
                            "goals",
                            "abilities",
                            "relationship_to_protagonist",
                        }},
                        position=index,
                    )
                )
        if "relationships" in patch and patch["relationships"] is not None:
            await self.session.execute(delete(BlueprintRelationship).where(BlueprintRelationship.project_id == project_id))
            for index, relation in enumerate(patch["relationships"]):
                self.session.add(
                    BlueprintRelationship(
                        project_id=project_id,
                        character_from=relation.get("character_from"),
                        character_to=relation.get("character_to"),
                        description=relation.get("description"),
                        position=index,
                    )
                )
        if "chapter_outline" in patch and patch["chapter_outline"] is not None:
            await self.session.execute(delete(ChapterOutline).where(ChapterOutline.project_id == project_id))
            for outline in patch["chapter_outline"]:
                self.session.add(
                    ChapterOutline(
                        project_id=project_id,
                        chapter_number=outline.get("chapter_number"),
                        title=outline.get("title", ""),
                        summary=outline.get("summary"),
                    )
                )
        await self.session.commit()
        await self._touch_project(project_id)

    # ------------------------------------------------------------------
    # 章节与版本
    # ------------------------------------------------------------------
    async def get_outline(self, project_id: str, chapter_number: int) -> Optional[ChapterOutline]:
        stmt = (
            select(ChapterOutline)
            .where(
                ChapterOutline.project_id == project_id,
                ChapterOutline.chapter_number == chapter_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_chapter(self, project_id: str, chapter_number: int) -> Chapter:
        stmt = (
            select(Chapter)
            .where(
                Chapter.project_id == project_id,
                Chapter.chapter_number == chapter_number,
            )
        )
        result = await self.session.execute(stmt)
        chapter = result.scalars().first()
        if chapter:
            return chapter
        chapter = Chapter(project_id=project_id, chapter_number=chapter_number)
        self.session.add(chapter)
        await self.session.commit()
        await self.session.refresh(chapter)
        return chapter

    async def replace_chapter_versions(self, chapter: Chapter, contents: List[str], metadata: Optional[List[Dict]] = None) -> List[ChapterVersion]:
        await self.session.execute(delete(ChapterVersion).where(ChapterVersion.chapter_id == chapter.id))
        versions: List[ChapterVersion] = []
        for index, content in enumerate(contents):
            extra = metadata[index] if metadata and index < len(metadata) else None
            text_content = _normalize_version_content(content, extra)
            version = ChapterVersion(
                chapter_id=chapter.id,
                content=text_content,
                metadata=None,
                version_label=f"v{index+1}",
            )
            self.session.add(version)
            versions.append(version)
        chapter.status = ChapterGenerationStatus.WAITING_FOR_CONFIRM.value
        await self.session.commit()
        await self.session.refresh(chapter)
        await self._touch_project(chapter.project_id)
        return versions

    async def select_chapter_version(self, chapter: Chapter, version_index: int) -> ChapterVersion:
        versions = sorted(chapter.versions, key=lambda item: item.created_at)
        if not versions or version_index < 0 or version_index >= len(versions):
            raise HTTPException(status_code=400, detail="版本索引无效")
        selected = versions[version_index]
        chapter.selected_version_id = selected.id
        chapter.status = ChapterGenerationStatus.SUCCESSFUL.value
        chapter.word_count = len(selected.content or "")
        await self.session.commit()
        await self.session.refresh(chapter)
        await self._touch_project(chapter.project_id)
        return selected

    async def add_chapter_evaluation(self, chapter: Chapter, version: Optional[ChapterVersion], feedback: str, decision: Optional[str] = None) -> None:
        evaluation = ChapterEvaluation(
            chapter_id=chapter.id,
            version_id=version.id if version else None,
            feedback=feedback,
            decision=decision,
        )
        self.session.add(evaluation)
        chapter.status = ChapterGenerationStatus.WAITING_FOR_CONFIRM.value
        await self.session.commit()
        await self.session.refresh(chapter)
        await self._touch_project(chapter.project_id)

    async def delete_chapters(self, project_id: str, chapter_numbers: Iterable[int]) -> None:
        await self.session.execute(
            delete(Chapter).where(
                Chapter.project_id == project_id,
                Chapter.chapter_number.in_(list(chapter_numbers)),
            )
        )
        await self.session.execute(
            delete(ChapterOutline).where(
                ChapterOutline.project_id == project_id,
                ChapterOutline.chapter_number.in_(list(chapter_numbers)),
            )
        )
        await self.session.commit()
        await self._touch_project(project_id)

    # ------------------------------------------------------------------
    # 序列化辅助
    # ------------------------------------------------------------------
    async def get_project_schema_for_admin(self, project_id: str) -> NovelProjectSchema:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return await self._serialize_project(project)

    async def get_section_data_for_admin(
        self,
        project_id: str,
        section: NovelSectionType,
    ) -> NovelSectionResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return self._build_section_response(project, section)

    async def get_chapter_schema_for_admin(
        self,
        project_id: str,
        chapter_number: int,
    ) -> ChapterSchema:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        return self._build_chapter_schema(project, chapter_number)

    async def _serialize_project(self, project: NovelProject) -> NovelProjectSchema:
        conversations = [
            {"role": convo.role, "content": convo.content}
            for convo in sorted(project.conversations, key=lambda c: c.seq)
        ]

        blueprint_schema = self._build_blueprint_schema(project)

        outlines_map = {outline.chapter_number: outline for outline in project.outlines}
        chapters_map = {chapter.chapter_number: chapter for chapter in project.chapters}
        chapter_numbers = sorted(set(outlines_map.keys()) | set(chapters_map.keys()))
        chapters_schema: List[ChapterSchema] = [
            self._build_chapter_schema(
                project,
                number,
                outlines_map=outlines_map,
                chapters_map=chapters_map,
            )
            for number in chapter_numbers
        ]

        return NovelProjectSchema(
            id=project.id,
            user_id=project.user_id,
            title=project.title,
            initial_prompt=project.initial_prompt or "",
            project_type=project.project_type,
            conversation_history=conversations,
            blueprint=blueprint_schema,
            chapters=chapters_schema,
        )

    async def _touch_project(self, project_id: str) -> None:
        await self.session.execute(
            update(NovelProject)
            .where(NovelProject.id == project_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
        await self.session.commit()

    def _build_blueprint_schema(self, project: NovelProject) -> Blueprint:
        blueprint_obj = project.blueprint
        if blueprint_obj:
            return Blueprint(
                title=blueprint_obj.title or "",
                target_audience=blueprint_obj.target_audience or "",
                genre=blueprint_obj.genre or "",
                style=blueprint_obj.style or "",
                tone=blueprint_obj.tone or "",
                one_sentence_summary=blueprint_obj.one_sentence_summary or "",
                full_synopsis=blueprint_obj.full_synopsis or "",
                world_setting=blueprint_obj.world_setting or {},
                characters=[
                    {
                        "name": character.name,
                        "identity": character.identity,
                        "personality": character.personality,
                        "goals": character.goals,
                        "abilities": character.abilities,
                        "relationship_to_protagonist": character.relationship_to_protagonist,
                        **(character.extra or {}),
                    }
                    for character in sorted(project.characters, key=lambda c: c.position)
                ],
                relationships=[
                    {
                        "character_from": relation.character_from,
                        "character_to": relation.character_to,
                        "description": relation.description or "",
                        "relationship_type": getattr(relation, "relationship_type", None),
                    }
                    for relation in sorted(project.relationships_, key=lambda r: r.position)
                ],
                chapter_outline=[
                    ChapterOutlineSchema(
                        chapter_number=outline.chapter_number,
                        title=outline.title,
                        summary=outline.summary or "",
                    )
                    for outline in sorted(project.outlines, key=lambda o: o.chapter_number)
                ],
            )
        return Blueprint(
            title="",
            target_audience="",
            genre="",
            style="",
            tone="",
            one_sentence_summary="",
            full_synopsis="",
            world_setting={},
            characters=[],
            relationships=[],
            chapter_outline=[],
        )

    def _build_section_response(
        self,
        project: NovelProject,
        section: NovelSectionType,
    ) -> NovelSectionResponse:
        blueprint = self._build_blueprint_schema(project)

        if section == NovelSectionType.OVERVIEW:
            data = {
                "title": project.title,
                "initial_prompt": project.initial_prompt or "",
                "status": project.status,
                "one_sentence_summary": blueprint.one_sentence_summary,
                "target_audience": blueprint.target_audience,
                "genre": blueprint.genre,
                "style": blueprint.style,
                "tone": blueprint.tone,
                "full_synopsis": blueprint.full_synopsis,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            }
        elif section == NovelSectionType.WORLD_SETTING:
            data = {
                "world_setting": blueprint.world_setting or {},
            }
        elif section == NovelSectionType.CHARACTERS:
            data = {
                "characters": blueprint.characters,
            }
        elif section == NovelSectionType.RELATIONSHIPS:
            data = {
                "relationships": blueprint.relationships,
            }
        elif section == NovelSectionType.CHAPTER_OUTLINE:
            data = {
                "chapter_outline": [outline.model_dump() for outline in blueprint.chapter_outline],
            }
        elif section == NovelSectionType.CHAPTERS:
            outlines_map = {outline.chapter_number: outline for outline in project.outlines}
            chapters_map = {chapter.chapter_number: chapter for chapter in project.chapters}
            chapter_numbers = sorted(set(outlines_map.keys()) | set(chapters_map.keys()))
            # 章节列表只返回元数据，不包含完整内容
            chapters = [
                self._build_chapter_schema(
                    project,
                    number,
                    outlines_map=outlines_map,
                    chapters_map=chapters_map,
                    include_content=False,
                ).model_dump()
                for number in chapter_numbers
            ]
            data = {
                "chapters": chapters,
                "total": len(chapters),
            }
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未知的章节类型")

        return NovelSectionResponse(section=section, data=data)

    def _build_chapter_schema(
        self,
        project: NovelProject,
        chapter_number: int,
        *,
        outlines_map: Optional[Dict[int, ChapterOutline]] = None,
        chapters_map: Optional[Dict[int, Chapter]] = None,
        include_content: bool = True,
    ) -> ChapterSchema:
        outlines = outlines_map or {outline.chapter_number: outline for outline in project.outlines}
        chapters = chapters_map or {chapter.chapter_number: chapter for chapter in project.chapters}
        outline = outlines.get(chapter_number)
        chapter = chapters.get(chapter_number)

        if not outline and not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")

        title = outline.title if outline else f"第{chapter_number}章"
        summary = outline.summary if outline else ""
        real_summary = chapter.real_summary if chapter else None
        content = None
        versions: Optional[List[str]] = None
        evaluation_text: Optional[str] = None
        status_value = ChapterGenerationStatus.NOT_GENERATED.value
        word_count = 0

        if chapter:
            status_value = chapter.status or ChapterGenerationStatus.NOT_GENERATED.value
            word_count = chapter.word_count or 0

            # 只有在 include_content=True 时才包含完整内容
            if include_content:
                if chapter.selected_version:
                    content = chapter.selected_version.content
                if chapter.versions:
                    versions = [
                        v.content
                        for v in sorted(chapter.versions, key=lambda item: item.created_at)
                    ]
                if chapter.evaluations:
                    latest = sorted(chapter.evaluations, key=lambda item: item.created_at)[-1]
                    evaluation_text = latest.feedback or latest.decision

        return ChapterSchema(
            chapter_number=chapter_number,
            title=title,
            summary=summary,
            real_summary=real_summary,
            content=content,
            versions=versions,
            evaluation=evaluation_text,
            generation_status=ChapterGenerationStatus(status_value),
            word_count=word_count,
        )
