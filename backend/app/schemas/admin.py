from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    novel_count: int
    user_count: int
    api_request_count: int


class DailyRequestLimit(BaseModel):
    limit: int = Field(..., ge=0, description="匿名用户每日可用次数")


class UpdateLogRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    created_by: Optional[str] = None
    is_pinned: bool

    class Config:
        from_attributes = True


class UpdateLogBase(BaseModel):
    content: Optional[str] = None
    is_pinned: Optional[bool] = None


class UpdateLogCreate(UpdateLogBase):
    content: str


class UpdateLogUpdate(UpdateLogBase):
    pass


class AdminNovelSummary(BaseModel):
    id: str
    title: str
    project_type: str = "novel"
    owner_id: int
    owner_username: str
    genre: str
    last_edited: str
    completed_chapters: int
    total_chapters: int
