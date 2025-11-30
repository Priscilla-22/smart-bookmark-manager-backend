"""Setup and data initialization endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Tag, Collection, Bookmark, Base
from app.database import engine

router = APIRouter()

@router.post("/create-initial-data")
def create_initial_data(db: Session = Depends(get_db)):
    """Create initial data for the application."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            return {"message": f"Database already has {existing_users} users. Skipping data creation."}
        
        # Create a test user
        user = User(
            username="demo",
            email="demo@example.com",
            gender="male"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
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
        
        # Refresh tags to get IDs
        for tag in created_tags:
            db.refresh(tag)
        
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
        
        # Create some bookmarks
        bookmarks_data = [
            {
                "title": "React Documentation",
                "url": "https://react.dev",
                "description": "Official React documentation and guides",
                "summary": "Complete guide to React library with examples and API reference",
                "user_id": user.id,
                "collection_id": collection.id,
            },
            {
                "title": "FastAPI Tutorial",
                "url": "https://fastapi.tiangolo.com",
                "description": "Learn how to build APIs with FastAPI",
                "summary": "Comprehensive tutorial for building modern APIs with Python FastAPI framework",
                "user_id": user.id,
                "collection_id": collection.id,
            },
            {
                "title": "GitHub",
                "url": "https://github.com",
                "description": "Code hosting and collaboration platform",
                "summary": "The world's leading platform for version control and collaborative software development",
                "user_id": user.id,
            }
        ]
        
        created_bookmarks = []
        for bookmark_data in bookmarks_data:
            bookmark = Bookmark(**bookmark_data)
            # Add some tags to bookmarks
            if len(created_tags) > 0:
                bookmark.tags = [created_tags[0]]  # Add Development tag
            db.add(bookmark)
            created_bookmarks.append(bookmark)
        
        db.commit()
        
        return {
            "message": "Initial data created successfully!",
            "user": user.username,
            "tags": len(created_tags),
            "collections": 1,
            "bookmarks": len(created_bookmarks)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating initial data: {str(e)}")

@router.get("/database-status")
def get_database_status(db: Session = Depends(get_db)):
    """Check database status and contents."""
    try:
        users_count = db.query(User).count()
        tags_count = db.query(Tag).count()
        collections_count = db.query(Collection).count()
        bookmarks_count = db.query(Bookmark).count()
        
        return {
            "status": "connected",
            "counts": {
                "users": users_count,
                "tags": tags_count,
                "collections": collections_count,
                "bookmarks": bookmarks_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")