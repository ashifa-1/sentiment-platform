from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(String(50), index=True, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_posts_created_at", "created_at"),
    )


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(
        String(255),
        ForeignKey("social_media_posts.post_id"),
        nullable=False
    )
    model_name = Column(String(100), nullable=False)
    sentiment_label = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    emotion = Column(String(50))
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)


class SentimentAlert(Base):
    __tablename__ = "sentiment_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False)
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    post_count = Column(Integer, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON)


def init_db():
    Base.metadata.create_all(bind=engine)
