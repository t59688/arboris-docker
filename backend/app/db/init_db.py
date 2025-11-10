import logging

from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from ..core.config import settings
from ..core.security import hash_password
from ..models import Prompt, SystemConfig, User
from .base import Base
from .system_config_defaults import SYSTEM_CONFIG_DEFAULTS
from .session import AsyncSessionLocal, engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """初始化数据库结构并确保默认管理员存在。"""

    await _ensure_database_exists()

    # ---- 第一步：创建所有表结构 ----
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_project_type_column(conn)
    logger.info("数据库表结构已初始化")

    # ---- 第二步：确保管理员账号至少存在一个 ----
    async with AsyncSessionLocal() as session:
        admin_exists = await session.execute(select(User).where(User.is_admin.is_(True)))
        if not admin_exists.scalars().first():
            logger.warning("未检测到管理员账号，正在创建默认管理员 ...")
            admin_user = User(
                username=settings.admin_default_username,
                email=settings.admin_default_email,
                hashed_password=hash_password(settings.admin_default_password),
                is_admin=True,
            )

            session.add(admin_user)
            try:
                await session.commit()
                logger.info("默认管理员创建完成：%s", settings.admin_default_username)
            except IntegrityError:
                await session.rollback()
                logger.exception("默认管理员创建失败，可能是并发启动导致，请检查数据库状态")

        # ---- 第三步：同步系统配置到数据库 ----
        for entry in SYSTEM_CONFIG_DEFAULTS:
            value = entry.value_getter(settings)
            if value is None:
                continue
            existing = await session.get(SystemConfig, entry.key)
            if existing:
                if entry.description and existing.description != entry.description:
                    existing.description = entry.description
                continue
            session.add(
                SystemConfig(
                    key=entry.key,
                    value=value,
                    description=entry.description,
                )
            )

        await _ensure_default_prompts(session)

        await session.commit()


async def _ensure_database_exists() -> None:
    """在首次连接前确认数据库存在，针对不同驱动做最小化准备工作。"""
    url = make_url(settings.sqlalchemy_database_uri)

    if url.get_backend_name() == "sqlite":
        # SQLite 采用文件数据库，确保父目录存在即可，无需额外建库语句
        db_path = Path(url.database or "").expanduser()
        if not db_path.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            db_path = (project_root / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return

    database = (url.database or "").strip("/")
    if not database:
        return

    admin_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database=None,
        query=url.query,
    )

    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
    )
    async with admin_engine.begin() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database}`"))
    await admin_engine.dispose()


async def _ensure_project_type_column(conn) -> None:
    """确保 novel_projects 表拥有 project_type 列，兼容旧版本数据库。"""
    dialect = conn.engine.dialect.name
    alter_sql = ""
    if dialect == "sqlite":
        alter_sql = "ALTER TABLE novel_projects ADD COLUMN project_type VARCHAR(32) NOT NULL DEFAULT 'novel'"
    elif dialect in {"mysql", "mariadb"}:
        alter_sql = (
            "ALTER TABLE novel_projects "
            "ADD COLUMN IF NOT EXISTS project_type VARCHAR(32) NOT NULL DEFAULT 'novel'"
        )
    else:
        alter_sql = (
            "ALTER TABLE novel_projects "
            "ADD COLUMN project_type VARCHAR(32) NOT NULL DEFAULT 'novel'"
        )

    try:
        await conn.execute(text(alter_sql))
        logger.info("已为 novel_projects 添加 project_type 列")
    except SQLAlchemyError as exc:
        message = str(exc).lower()
        if "duplicate column" in message or "exists" in message or "already exists" in message:
            return
        logger.debug("添加 project_type 列时忽略的异常: %s", exc)


async def _ensure_default_prompts(session: AsyncSession) -> None:
    prompts_dir = Path(__file__).resolve().parents[2] / "prompts"
    if not prompts_dir.is_dir():
        return

    result = await session.execute(select(Prompt.name))
    existing_names = set(result.scalars().all())

    for prompt_file in sorted(prompts_dir.glob("*.md")):
        name = prompt_file.stem
        if name in existing_names:
            continue
        content = prompt_file.read_text(encoding="utf-8")
        session.add(Prompt(name=name, content=content))
