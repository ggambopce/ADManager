# app/schemas/ad.py
from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel

AdType = Literal["IMAGE", "IFRAME"]

class AdBase(BaseModel):
    ad_type: AdType = "IMAGE"
    title: str
    description: Optional[str] = None

    image_url: Optional[str] = None
    target_url: Optional[str] = None
    short_url: Optional[str] = None

    embed_src: Optional[str] = None
    embed_width: Optional[int] = None
    embed_height: Optional[int] = None
   

class AdCreate(BaseModel):
    ad_type: Literal["IMAGE", "IFRAME"] = "IMAGE"
    title: str
    description: Optional[str] = None

    # IMAGE일 때 사용
    target_url: Optional[str] = None

    # IFRAME일 때 사용
    embed_src: Optional[str] = None
    embed_width: Optional[int] = 300
    embed_height: Optional[int] = 250

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
    ad_type: AdType
    title: str
    description: Optional[str] = None

    image_url: Optional[str] = None
    short_url: Optional[str] = None
    target_url: Optional[str] = None

    embed_src: Optional[str] = None
    embed_width: Optional[int] = None
    embed_height: Optional[int] = None

class Config:
    from_attributes = True