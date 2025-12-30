# backend/app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import Optional, List
from datetime import datetime, timedelta
import os
import redis
import json
import asyncio

from app.models.database import SessionLocal, SocialMediaPost, SentimentAnalysis
from app.api.websocket import manager

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis for Health Check
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    socket_timeout=2
)

# --- 1. Health Check ---
@router.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    status = {"status": "healthy", "services": {}, "stats": {}}
    
    # Check DB
    try:
        db.execute(text("SELECT 1")) # Add text() here
        status["services"]["database"] = "connected"
    except Exception as e:
        print(f"DB Health Error: {e}") # This will show in 'docker-compose logs backend'
        status["services"]["database"] = "disconnected"
        status["status"] = "unhealthy"
        
    # Check Redis
    try:
        redis_client.ping()
        status["services"]["redis"] = "connected"
    except Exception:
        status["services"]["redis"] = "disconnected"
        status["status"] = "unhealthy"

    return status

# --- 2. Get Posts ---
@router.get("/api/posts")
async def get_posts(
    limit: int = 50,
    offset: int = 0,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SocialMediaPost, SentimentAnalysis).join(
        SentimentAnalysis, SocialMediaPost.post_id == SentimentAnalysis.post_id
    )

    if source:
        query = query.filter(SocialMediaPost.source == source)
    if sentiment:
        query = query.filter(SentimentAnalysis.sentiment_label == sentiment)

    total = query.count()
    
    # Order by newest first
    results = query.order_by(desc(SocialMediaPost.created_at)).offset(offset).limit(limit).all()

    posts = []
    for post, analysis in results:
        posts.append({
            "post_id": post.post_id,
            "source": post.source,
            "content": post.content,
            "author": post.author,
            "created_at": post.created_at,
            "sentiment": {
                "label": analysis.sentiment_label,
                "confidence": analysis.confidence_score,
                "emotion": analysis.emotion
            }
        })

    return {"posts": posts, "total": total, "limit": limit, "offset": offset}

# --- 3. Aggregate Data ---
@router.get("/api/sentiment/aggregate")
async def get_sentiment_aggregate(
    period: str = Query(..., regex="^(minute|hour|day)$"),
    db: Session = Depends(get_db)
):
    # Determine truncation period
    trunc_period = period
    
    # Calculate aggregation
    # Query: Select date_trunc('hour', created_at), sentiment_label, count(*)
    results = db.query(
        func.date_trunc(trunc_period, SentimentAnalysis.analyzed_at).label('timestamp'),
        SentimentAnalysis.sentiment_label,
        func.count(SentimentAnalysis.id)
    ).group_by(
        'timestamp', SentimentAnalysis.sentiment_label
    ).order_by('timestamp').all()

    # Process results into structured JSON
    data_map = {}
    for timestamp, label, count in results:
        ts_str = timestamp.isoformat()
        if ts_str not in data_map:
            data_map[ts_str] = {"timestamp": ts_str, "positive": 0, "negative": 0, "neutral": 0, "total": 0}
        
        if label in data_map[ts_str]:
            data_map[ts_str][label] = count
            data_map[ts_str]["total"] += count

    return {"period": period, "data": list(data_map.values())}

# --- 4. Distribution ---
@router.get("/api/sentiment/distribution")
async def get_sentiment_distribution(hours: int = 24, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        SentimentAnalysis.sentiment_label, func.count(SentimentAnalysis.id)
    ).filter(SentimentAnalysis.analyzed_at >= since).group_by(SentimentAnalysis.sentiment_label).all()

    distribution = {"positive": 0, "negative": 0, "neutral": 0}
    for label, count in results:
        if label in distribution:
            distribution[label] = count

    return distribution

# --- 5. WebSocket ---
@router.websocket("/ws/sentiment")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send confirmation
        await websocket.send_json({
            "type": "connected", 
            "message": "Connected to sentiment stream",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)