"""Bookmark management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Bookmark, Tag, User, Collection
from app.schemas import BookmarkCreate, BookmarkUpdate, Bookmark as BookmarkSchema
from app.services.smart_tags import SmartTagService
from app.services.content_summarizer import ContentSummarizer
from app.services.smart_summarizer import SmartSummarizer
from app.services.bookmark_recommender import BookmarkRecommender

router = APIRouter()

@router.get("/", response_model=List[BookmarkSchema])
async def get_bookmarks(
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None,
    collection_id: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get all bookmarks with optional filtering."""
    query = db.query(Bookmark)
    if user_id:
        query = query.filter(Bookmark.user_id == user_id)
    if collection_id is not None:
        if collection_id == "null":
            query = query.filter(Bookmark.collection_id.is_(None))
        else:
            try:
                collection_id_int = int(collection_id)
                query = query.filter(Bookmark.collection_id == collection_id_int)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid collection_id format"
                )
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Bookmark.title.ilike(search_filter)) | 
            (Bookmark.description.ilike(search_filter))
        )
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
    user = db.query(User).filter(User.id == bookmark.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate collection if provided
    if bookmark.collection_id:
        collection = db.query(Collection).filter(
            Collection.id == bookmark.collection_id,
            Collection.user_id == bookmark.user_id
        ).first()
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or does not belong to user"
            )
    
    # Generate smart summary automatically
    smart_summary = None
    try:
        smart_summarizer = SmartSummarizer()
        result = smart_summarizer.get_smart_summary(str(bookmark.url))
        if 'error' not in result:
            smart_summary = result.get('ml_summary')
    except Exception:
        pass  # Continue without summary if generation fails
    
    db_bookmark = Bookmark(
        url=str(bookmark.url),
        title=bookmark.title,
        description=bookmark.description,
        summary=smart_summary or bookmark.summary,  # Use AI summary or fallback to user summary
        user_id=bookmark.user_id,
        collection_id=bookmark.collection_id
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
    return

class TagSuggestionRequest(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    existing_tags: Optional[List[str]] = None

@router.post("/suggest-tags")
async def suggest_tags_for_url(request: TagSuggestionRequest):
    """Generate smart tag suggestions for a URL."""
    tag_service = SmartTagService()
    suggestions = tag_service.suggest_tags(
        url=request.url,
        title=request.title,
        description=request.description,
        existing_tags=request.existing_tags or []
    )
    
    return {"suggestions": suggestions}

@router.post("/recommend-similar")
async def recommend_similar_bookmarks(
    url: str,
    title: str = None,
    description: str = None,
    user_id: int = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Find similar bookmarks based on content analysis."""
    recommender = BookmarkRecommender()
    recommendations = recommender.get_similar_bookmarks(
        db=db,
        url=url,
        title=title,
        description=description,
        user_id=user_id,
        limit=limit
    )
    
    return {"recommendations": recommendations}

@router.post("/analyze-url")
async def analyze_url(url: str, use_ml: bool = True):
    """Analyze URL and extract title, description, and AI-powered summary."""
    
    if use_ml:
        # Use smart summarization
        smart_summarizer = SmartSummarizer()
        result = smart_summarizer.get_smart_summary(url)
        
        # If ML summarizer encounters an error, try basic summarizer as fallback
        if 'error' in result:
            basic_summarizer = ContentSummarizer()
            fallback_result = basic_summarizer.get_page_info(url)
            if 'error' not in fallback_result:
                return {
                    "url": url,
                    "title": fallback_result.get('title'),
                    "description": fallback_result.get('description'),
                    "summary": fallback_result.get('summary'),
                    "content_length": fallback_result.get('content_length', 0),
                    "summary_method": "basic_fallback"
                }
            else:
                return {
                    "url": url,
                    "title": None,
                    "description": None,
                    "summary": None,
                    "content_length": 0,
                    "summary_method": "error",
                    "error": result.get('error', 'Unknown error')
                }
        
        # Return ML summarizer result
        return {
            "url": url,
            "title": result.get('title'),
            "description": result.get('description'),
            "summary": result.get('ml_summary'),
            "content_length": result.get('content_length', 0),
            "summary_method": result.get('summary_method', 'smart')
        }
    else:
        # Use basic content extraction
        summarizer = ContentSummarizer()
        result = summarizer.get_page_info(url)
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        return {
            "url": url,
            "title": result.get('title'),
            "description": result.get('description'),
            "summary": result.get('summary'),
            "content_length": result.get('content_length', 0),
            "summary_method": "basic"
        }