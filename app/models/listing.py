from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from .database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    original_title = Column(String(255), nullable=False, index=True)  # Index for title searches
    original_description = Column(Text, nullable=False)
    images = Column(JSON, default=[])
    generated_title = Column(String(255))
    generated_description = Column(Text)
    generated_bullets = Column(JSON, default=[])
    keywords = Column(JSON, default=[])
    optimized_title = Column(String(255))
    optimized_description = Column(Text)
    optimized_bullets = Column(JSON, default=[])
    additional_images = Column(JSON, default=[])
    status = Column(String(50), default="draft", index=True)  # Index for status filtering
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Index for ordering
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_title_status', 'original_title', 'status'),
    )