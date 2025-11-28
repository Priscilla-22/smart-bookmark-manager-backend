"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, EmailStr

class TagBase(BaseModel):
    """Base schema for tag data."""
    name: str
    color: Optional[str] = "#3B82F6"

class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass

class Tag(TagBase):
    """Schema for tag response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Base schema for user data."""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass

class User(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BookmarkBase(BaseModel):
    """Base schema for bookmark data."""
    url: HttpUrl
    title: str
    description: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    """Schema for creating a new bookmark."""
    user_id: int
    tag_ids: Optional[List[int]] = []

class BookmarkUpdate(BaseModel):
    """Schema for updating a bookmark."""
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class Bookmark(BookmarkBase):
    """Schema for bookmark response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []

    class Config:
        from_attributes = True