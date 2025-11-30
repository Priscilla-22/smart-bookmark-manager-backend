"""Database configuration and connection setup."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://smart_bookmark_db_user:ZKhFRlrOd3vA5yDVsUdupKPQ9iRHlRUn@dpg-d4m420ogjchc73b1hlg0-a/smart_bookmark_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()