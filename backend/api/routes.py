from fastapi import APIRouter, Query, status
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import text
from models.database import SessionLocal
import redis
import os

router = APIRouter()

# ------------------------------------------------------------------
# Endpoint 1: Health Check
# ------------------------------------------------------------------
@router.get("/api/health", status_code=200)
async def health_check():
    db_status = "connected"
    redis_status = "connected"

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    finally:
        db.close()

    try:
        redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        ).ping()
    except Exception:
        redis_status = "disconnected"

    try:
        db = SessionLocal()
        total_posts = db.execute(
            text("SELECT COUNT(*) FROM social_media_posts")
        ).scalar()

        total_analyses = db.execute(
            text("SELECT COUNT(*) FROM sentiment_analysis")
        ).scalar()

        recent_posts = db.execute(
            text("""
                SELECT COUNT(*) FROM social_media_posts
                WHERE ingested_at >= :since
            """),
            {"since": datetime.utcnow() - timedelta(hours=1)}
        ).scalar()
    finally:
        db.close()

    status_value = "healthy"
    http_status = status.HTTP_200_OK

    if db_status == "disconnected" or redis_status == "disconnected":
        status_value = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": status_value,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": db_status,
            "redis": redis_status
        },
        "stats": {
            "total_posts": total_posts,
            "total_analyses": total_analyses,
            "recent_posts_1h": recent_posts
        }
    }

# ------------------------------------------------------------------
# Endpoint 2: Get Posts
# ------------------------------------------------------------------
@router.get("/api/posts")
async def get_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    p.post_id,
                    p.source,
                    p.content,
                    p.author,
                    p.created_at,
                    s.sentiment_label,
                    s.confidence_score,
                    s.emotion,
                    s.model_name
                FROM social_media_posts p
                JOIN sentiment_analysis s
                  ON p.post_id = s.post_id
                WHERE s.analyzed_at = (
                    SELECT MAX(analyzed_at)
                    FROM sentiment_analysis
                    WHERE post_id = p.post_id
                )
                ORDER BY p.created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        ).mappings().all()

        total = db.execute(
            text("SELECT COUNT(*) FROM social_media_posts")
        ).scalar()

        posts = []
        for row in rows:
            posts.append({
                "post_id": row["post_id"],
                "source": row["source"],
                "content": row["content"],
                "author": row["author"],
                "created_at": row["created_at"].isoformat(),
                "sentiment": {
                    "label": row["sentiment_label"],
                    "confidence": row["confidence_score"],
                    "emotion": row["emotion"],
                    "model_name": row["model_name"]
                }
            })

        return {
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset,
            "filters": {}
        }
    finally:
        db.close()

# ------------------------------------------------------------------
# Endpoint 3: Sentiment Aggregate
# ------------------------------------------------------------------
@router.get("/api/sentiment/aggregate")
async def get_sentiment_aggregate(
    period: str = Query(..., regex="^(minute|hour|day)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    db = SessionLocal()

    if not start_date:
        start_date = datetime.utcnow() - timedelta(hours=24)
    if not end_date:
        end_date = datetime.utcnow()

    try:
        rows = db.execute(
            text("""
                SELECT
                    date_trunc(:period, analyzed_at) AS ts,
                    sentiment_label,
                    COUNT(*) AS count,
                    AVG(confidence_score) AS avg_conf
                FROM sentiment_analysis
                WHERE analyzed_at BETWEEN :start AND :end
                GROUP BY ts, sentiment_label
                ORDER BY ts ASC
            """),
            {
                "period": period,
                "start": start_date,
                "end": end_date
            }
        ).mappings().all()

        buckets = {}

        for row in rows:
            ts = row["ts"].isoformat()
            if ts not in buckets:
                buckets[ts] = {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0,
                    "confidence_sum": 0.0
                }

            buckets[ts][row["sentiment_label"]] += row["count"]
            buckets[ts]["total"] += row["count"]
            buckets[ts]["confidence_sum"] += row["avg_conf"] * row["count"]

        data = []
        for ts, v in buckets.items():
            total = v["total"]
            data.append({
                "timestamp": ts,
                "positive_count": v["positive"],
                "negative_count": v["negative"],
                "neutral_count": v["neutral"],
                "total_count": total,
                "positive_percentage": (v["positive"] / total) * 100 if total else 0,
                "negative_percentage": (v["negative"] / total) * 100 if total else 0,
                "neutral_percentage": (v["neutral"] / total) * 100 if total else 0,
                "average_confidence": v["confidence_sum"] / total if total else 0
            })

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": data
        }
    finally:
        db.close()

# ------------------------------------------------------------------
# Endpoint 4: Sentiment Distribution
# ------------------------------------------------------------------
@router.get("/api/sentiment/distribution")
async def get_sentiment_distribution(
    hours: int = Query(24, ge=1, le=168)
):
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    cache_key = f"sentiment_distribution_{hours}"
    cached = redis_client.get(cache_key)

    if cached:
        return {
            **eval(cached),
            "cached": True,
            "cached_at": datetime.utcnow().isoformat() + "Z"
        }

    since = datetime.utcnow() - timedelta(hours=hours)
    db = SessionLocal()

    try:
        # Sentiment counts
        sentiment_rows = db.execute(
            text("""
                SELECT sentiment_label, COUNT(*) AS count
                FROM sentiment_analysis
                WHERE analyzed_at >= :since
                GROUP BY sentiment_label
            """),
            {"since": since}
        ).mappings().all()

        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        total = 0

        for row in sentiment_rows:
            distribution[row["sentiment_label"]] = row["count"]
            total += row["count"]

        percentages = {
            k: (v / total * 100 if total else 0)
            for k, v in distribution.items()
        }

        # Emotion counts
        emotion_rows = db.execute(
            text("""
                SELECT emotion, COUNT(*) AS count
                FROM sentiment_analysis
                WHERE analyzed_at >= :since
                GROUP BY emotion
                ORDER BY count DESC
                LIMIT 5
            """),
            {"since": since}
        ).mappings().all()

        top_emotions = {row["emotion"]: row["count"] for row in emotion_rows}

        response = {
            "timeframe_hours": hours,
            "distribution": distribution,
            "total": total,
            "percentages": percentages,
            "top_emotions": top_emotions
        }

        # Cache for 60 seconds
        redis_client.setex(cache_key, 60, str(response))

        return {
            **response,
            "cached": False,
            "cached_at": datetime.utcnow().isoformat() + "Z"
        }

    finally:
        db.close()
