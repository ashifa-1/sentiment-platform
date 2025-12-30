# backend/app/models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 1. Setup Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define Tables

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), unique=True, index=True)
    source = Column(String(50), index=True)
    content = Column(Text)
    author = Column(String(255))
    created_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), ForeignKey("social_media_posts.post_id"))
    model_name = Column(String(100))
    sentiment_label = Column(String(20)) # positive, negative, neutral
    confidence_score = Column(Float)
    emotion = Column(String(50), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)

class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50))
    threshold_value = Column(Float)
    actual_value = Column(Float)
    window_start = Column(DateTime)
    window_end = Column(DateTime)
    post_count = Column(Integer)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON)

# Function to initialize DB
def init_db():
    Base.metadata.create_all(bind=engine)