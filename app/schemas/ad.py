# app/schemas/ad.py
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    short_url: Optional[str] = None
   

class AdCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_url: Optional[str] = None


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_url: Optional[str] = None
   


class AdResponse(AdBase):
    id: int

    class Config:
        from_attributes = True  # SQLAlchemy ORM 객체 -> Pydantic 변환 허용


class AdPageResponse(BaseModel):
    content: List[AdResponse]
    page: int
    size: int
    total_elements: int
    total_pages: int


class PublicAdResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    short_url: Optional[str] = None
    target_url: Optional[str] = None

class Config:
        from_attributes = True