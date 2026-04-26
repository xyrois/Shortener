from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class URLBase(BaseModel):
    target_url: str
    expires_at: Optional[datetime] = None


class URL(BaseModel):
    target_url: str
    is_active: bool
    clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class URLInfo(URL):
    url: str
    admin_url: str


class VisitInfo(BaseModel):
    visited_at: datetime
    country: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class URLAnalytics(URLInfo):
    visits: List[VisitInfo]