"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import List, Optional, Literal
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
    gender: Optional[Literal["male", "female"]] = "male"

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
    summary: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    """Schema for creating a new bookmark."""
    user_id: int
    collection_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []

class BookmarkUpdate(BaseModel):
    """Schema for updating a bookmark."""
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    collection_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class Bookmark(BookmarkBase):
    """Schema for bookmark response."""
    id: int
    user_id: int
    collection_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []

    class Config:
        from_attributes = True

class CollectionBase(BaseModel):
    """Base schema for collection data."""
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3B82F6"

class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    user_id: int

class Collection(CollectionBase):
    """Schema for collection response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True