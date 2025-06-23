"""
Base model classes and mixins
"""

from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UUIDMixin:
    """Mixin for UUID primary key"""
    @declared_attr
    def id(cls):
        return Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

class BaseModel(Base, TimestampMixin, UUIDMixin):
    """Base model class"""
    __abstract__ = True
    
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
