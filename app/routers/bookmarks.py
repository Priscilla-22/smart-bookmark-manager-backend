"""Bookmark management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bookmark, Tag
from app.schemas import BookmarkCreate, BookmarkUpdate, Bookmark as BookmarkSchema

router = APIRouter()

@router.get("/", response_model=List[BookmarkSchema])
async def get_bookmarks(
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all bookmarks with optional filtering."""
    query = db.query(Bookmark)
    if user_id:
        query = query.filter(Bookmark.user_id == user_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{bookmark_id}", response_model=BookmarkSchema)
async def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """Get a specific bookmark by ID."""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Bookmark not found"
        )
    return bookmark

@router.post("/", response_model=BookmarkSchema, status_code=status.HTTP_201_CREATED)
async def create_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    """Create a new bookmark."""
    db_bookmark = Bookmark(
        url=str(bookmark.url),
        title=bookmark.title,
        description=bookmark.description,
        user_id=bookmark.user_id
    )
    
    if bookmark.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(bookmark.tag_ids)).all()
        db_bookmark.tags = tags
    
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.put("/{bookmark_id}", response_model=BookmarkSchema)
async def update_bookmark(
    bookmark_id: int, 
    bookmark_update: BookmarkUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing bookmark."""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Bookmark not found"
        )
    
    update_data = bookmark_update.dict(exclude_unset=True)
    
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_bookmark.tags = tags
    
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])
    
    for field, value in update_data.items():
        setattr(db_bookmark, field, value)
    
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """Delete a bookmark."""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Bookmark not found"
        )
    
    db.delete(db_bookmark)
    db.commit()
    return None