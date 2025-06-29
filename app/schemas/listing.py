from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ListingBase(BaseModel):
    original_title: str
    original_description: str
    images: List[str] = []

class ListingCreate(ListingBase):
    pass

class ListingUpdate(BaseModel):
    original_title: Optional[str] = None
    original_description: Optional[str] = None
    images: Optional[List[str]] = None
    generated_title: Optional[str] = None
    generated_description: Optional[str] = None
    generated_bullets: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    optimized_title: Optional[str] = None
    optimized_description: Optional[str] = None
    optimized_bullets: Optional[List[str]] = None
    additional_images: Optional[List[str]] = None
    status: Optional[str] = None

class Listing(ListingBase):
    id: int
    generated_title: Optional[str] = None
    generated_description: Optional[str] = None
    generated_bullets: List[str] = []
    keywords: List[str] = []
    optimized_title: Optional[str] = None
    optimized_description: Optional[str] = None
    optimized_bullets: List[str] = []
    additional_images: List[str] = []
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentRequest(BaseModel):
    listing_id: int

class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None