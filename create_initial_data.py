#!/usr/bin/env python3
"""Create initial data for the application."""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Tag, Collection, Bookmark, Base

def create_initial_data():
    """Create some initial data for testing."""
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://smart_bookmark_db_user:ZKhFRlrOd3vA5yDVsUdupKPQ9iRHlRUn@dpg-d4m420ogjchc73b1hlg0-a.oregon-postgres.render.com/smart_bookmark_db"
    )
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        db = SessionLocal()
        
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"ℹ️ Database already has {existing_users} users. Skipping data creation.")
            return
        
        # Create a test user
        user = User(
            username="demo",
            email="demo@example.com",
            gender="male"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created user: {user.username}")
        
        # Create some tags
        tags_data = [
            {"name": "Development", "color": "#3b82f6"},
            {"name": "Tutorial", "color": "#10b981"},
            {"name": "Documentation", "color": "#f59e0b"},
            {"name": "React", "color": "#06b6d4"},
            {"name": "Python", "color": "#8b5cf6"}
        ]
        
        created_tags = []
        for tag_data in tags_data:
            tag = Tag(**tag_data)
            db.add(tag)
            created_tags.append(tag)
        
        db.commit()
        print(f"✅ Created {len(created_tags)} tags")
        
        # Create a collection
        collection = Collection(
            name="Learning Resources",
            description="Useful learning materials and tutorials",
            color="#ef4444",
            user_id=user.id
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        print(f"✅ Created collection: {collection.name}")
        
        # Create some bookmarks
        bookmarks_data = [
            {
                "title": "React Documentation",
                "url": "https://react.dev",
                "description": "Official React documentation and guides",
                "summary": "Complete guide to React library with examples and API reference",
                "user_id": user.id,
                "collection_id": collection.id,
                "tags": [created_tags[0], created_tags[2], created_tags[3]]  # Development, Documentation, React
            },
            {
                "title": "FastAPI Tutorial",
                "url": "https://fastapi.tiangolo.com",
                "description": "Learn how to build APIs with FastAPI",
                "summary": "Comprehensive tutorial for building modern APIs with Python FastAPI framework",
                "user_id": user.id,
                "collection_id": collection.id,
                "tags": [created_tags[0], created_tags[1], created_tags[4]]  # Development, Tutorial, Python
            },
            {
                "title": "GitHub",
                "url": "https://github.com",
                "description": "Code hosting and collaboration platform",
                "summary": "The world's leading platform for version control and collaborative software development",
                "user_id": user.id,
                "tags": [created_tags[0]]  # Development
            }
        ]
        
        created_bookmarks = []
        for bookmark_data in bookmarks_data:
            tags = bookmark_data.pop('tags', [])
            bookmark = Bookmark(**bookmark_data)
            bookmark.tags = tags
            db.add(bookmark)
            created_bookmarks.append(bookmark)
        
        db.commit()
        print(f"✅ Created {len(created_bookmarks)} bookmarks")
        
        print("🎉 Initial data creation completed successfully!")
        print(f"👤 Demo user created with username: {user.username}")
        print(f"📁 Collection: {collection.name}")
        print(f"🔖 {len(created_bookmarks)} bookmarks added")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_initial_data()