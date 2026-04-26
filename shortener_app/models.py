from sqlalchemy import Boolean, Column, DateTime, Integer, String
from datetime import datetime

from .database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, index=True)
    visited_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)