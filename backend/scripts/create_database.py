"""
Database creation and initialization script
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.database import Base, engine
from app.models import user, project  # Import all models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create database and tables"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Create initial superuser if needed
        create_initial_user()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise

def create_initial_user():
    """Create initial superuser"""
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User
    from passlib.context import CryptContext
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if any users exist
        existing_user = db.query(User).first()
        if existing_user:
            logger.info("Users already exist, skipping initial user creation")
            return
        
        # Create password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Create initial superuser
        initial_user = User(
            email="admin@strumind.com",
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            full_name="System Administrator",
            is_superuser=True,
            is_verified=True
        )
        
        db.add(initial_user)
        db.commit()
        
        logger.info("Initial superuser created: admin@strumind.com / admin123")
        
    except Exception as e:
        logger.error(f"Failed to create initial user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
