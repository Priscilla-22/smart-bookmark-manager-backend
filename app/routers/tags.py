"""Tag management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tag
from app.schemas import TagCreate, Tag as TagSchema

router = APIRouter()

@router.get("/", response_model=List[TagSchema])
async def get_tags(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all tags."""
    return db.query(Tag).offset(skip).limit(limit).all()

@router.get("/{tag_id}", response_model=TagSchema)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a specific tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tag not found"
        )
    return tag

@router.get("/{tag_id}/usage")
async def get_tag_usage(tag_id: int, db: Session = Depends(get_db)):
    """Get information about tag usage."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tag not found"
        )
    
    bookmark_count = len(tag.bookmarks)
    return {
        "tag_id": tag.id,
        "tag_name": tag.name,
        "bookmark_count": bookmark_count,
        "can_delete": bookmark_count == 0
    }

@router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    
    db_tag = Tag(name=tag.name, color=tag.color)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.put("/{tag_id}", response_model=TagSchema)
async def update_tag(tag_id: int, tag: TagCreate, db: Session = Depends(get_db)):
    """Update an existing tag."""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tag not found"
        )
    
    existing_tag = db.query(Tag).filter(
        Tag.name == tag.name, 
        Tag.id != tag_id
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    
    db_tag.name = tag.name
    db_tag.color = tag.color
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag."""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tag not found"
        )
    
    # Check if tag is being used by any bookmarks
    if db_tag.bookmarks:
        bookmark_count = len(db_tag.bookmarks)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag '{db_tag.name}' as it is used by {bookmark_count} bookmark(s). Remove the tag from all bookmarks first."
        )
    
    db.delete(db_tag)
    db.commit()
    return None