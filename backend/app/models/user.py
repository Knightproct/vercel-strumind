"""
User and authentication models
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    
    def __repr__(self):
        return f"<User(email={self.email})>"
