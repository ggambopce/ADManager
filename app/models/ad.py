from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    func,
)

from app.core.database import Base


class Ad(Base):
    """
    광고 테이블
    - 이미지/내용/타겟 URL/숏링크
    - is_active 로 비활성 처리 가능
    """
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # 정적 파일 경로 (예: /static/ads/1_abcdef.jpg)
    image_url = Column(String(500), nullable=True)

    # 원본 이동 URL (제휴 링크, 링크프라이스 딥링크 등)
    target_url = Column(String(1000), nullable=True)

    # buly 등 외부 숏링크
    short_url = Column(String(500), nullable=True)

    # 논리적 활성화 여부 (soft delete 용도)
    is_active = Column(Boolean, nullable=False, server_default="1")

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Ad(id={self.id}, title={self.title})>"
