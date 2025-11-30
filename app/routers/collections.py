"""Collection management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Collection, User
from app.schemas import CollectionCreate, Collection as CollectionSchema

router = APIRouter()

@router.get("/", response_model=List[CollectionSchema])
async def get_collections(
    user_id: int = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all collections or collections for a specific user."""
    query = db.query(Collection)
    if user_id:
        query = query.filter(Collection.user_id == user_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{collection_id}", response_model=CollectionSchema)
async def get_collection(collection_id: int, db: Session = Depends(get_db)):
    """Get a specific collection by ID."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Collection not found"
        )
    return collection

@router.post("/", response_model=CollectionSchema, status_code=status.HTTP_201_CREATED)
async def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    """Create a new collection."""
    # Verify user exists
    user = db.query(User).filter(User.id == collection.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check for duplicate collection name for this user
    existing_collection = db.query(Collection).filter(
        (Collection.name == collection.name) & (Collection.user_id == collection.user_id)
    ).first()
    if existing_collection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection with this name already exists for this user"
        )
    
    db_collection = Collection(
        name=collection.name,
        description=collection.description,
        color=collection.color,
        user_id=collection.user_id
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

@router.put("/{collection_id}", response_model=CollectionSchema)
async def update_collection(
    collection_id: int, 
    collection: CollectionCreate, 
    db: Session = Depends(get_db)
):
    """Update an existing collection."""
    db_collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Collection not found"
        )
    
    # Check for duplicate collection name for this user (excluding current collection)
    existing_collection = db.query(Collection).filter(
        (Collection.name == collection.name) & 
        (Collection.user_id == collection.user_id) &
        (Collection.id != collection_id)
    ).first()
    if existing_collection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection with this name already exists for this user"
        )
    
    db_collection.name = collection.name
    db_collection.description = collection.description
    db_collection.color = collection.color
    db.commit()
    db.refresh(db_collection)
    return db_collection

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """Delete a collection. Bookmarks in the collection will have their collection_id set to null."""
    db_collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Collection not found"
        )
    
    # Update bookmarks to remove collection reference
    from app.models import Bookmark
    db.query(Bookmark).filter(Bookmark.collection_id == collection_id).update(
        {"collection_id": None}
    )
    
    db.delete(db_collection)
    db.commit()
    return None