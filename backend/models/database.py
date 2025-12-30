from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine.url import make.url

# Fetch database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create Async Engine for FastAPI performance
engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"), echo=True)

# Session factory for dependency injection
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

Base = declarative_base()

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(255), unique=True, nullable=False, index=True) # For fast lookups
    source = Column(String(50), nullable=False, index=True) # Indexed for filtering
    content = Column(Text, nullable=False)
    author = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    ingested_at = Column(DateTime, server_default=func.now())

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign key referencing social_media_posts.post_id
    post_id = Column(String(255), ForeignKey("social_media_posts.post_id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    sentiment_label = Column(String(20), nullable=False) # positive, negative, neutral
    confidence_score = Column(Float, nullable=False)
    emotion = Column(String(50), nullable=True) # joy, anger, sadness, etc.
    analyzed_at = Column(DateTime, server_default=func.now(), index=True)

class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False) # e.g., "high_negative_ratio"
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    post_count = Column(Integer, nullable=False)
    triggered_at = Column(DateTime, server_default=func.now(), index=True)
    details = Column(JSON, nullable=True)

# Required Indexes for frequently queried columns
Index('idx_post_created_at', SocialMediaPost.created_at)