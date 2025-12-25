import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import text
from models.database import SessionLocal
import redis


class AlertService:
    """
    Monitors sentiment metrics and triggers alerts on anomalies
    """

    def __init__(self, db_session_maker=SessionLocal, redis_client=None):
        # Load config from environment
        self.threshold = float(os.getenv("ALERT_NEGATIVE_RATIO_THRESHOLD", 2.0))
        self.window_minutes = int(os.getenv("ALERT_WINDOW_MINUTES", 5))
        self.min_posts = int(os.getenv("ALERT_MIN_POSTS", 10))

        self.db_session_maker = db_session_maker
        self.redis = redis_client or redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )

    async def check_thresholds(self) -> Optional[dict]:
        """
        Check if sentiment thresholds are exceeded
        """
        db = self.db_session_maker()
        try:
            since = datetime.utcnow() - timedelta(minutes=self.window_minutes)

            rows = db.execute(
                text("""
                    SELECT sentiment_label, COUNT(*) AS count
                    FROM sentiment_analysis
                    WHERE analyzed_at >= :since
                    GROUP BY sentiment_label
                """),
                {"since": since}
            ).mappings().all()

            metrics = {"positive": 0, "negative": 0, "neutral": 0}
            for row in rows:
                metrics[row["sentiment_label"]] = row["count"]

            total = sum(metrics.values())
            if total < self.min_posts:
                return None

            positive = metrics["positive"]
            negative = metrics["negative"]

            # Avoid division by zero
            ratio = negative / max(positive, 1)

            if ratio > self.threshold:
                return {
                    "alert_triggered": True,
                    "alert_type": "high_negative_ratio",
                    "threshold": self.threshold,
                    "actual_ratio": round(ratio, 2),
                    "window_minutes": self.window_minutes,
                    "metrics": {
                        "positive_count": positive,
                        "negative_count": negative,
                        "neutral_count": metrics["neutral"],
                        "total_count": total
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

            return None

        finally:
            db.close()

    async def save_alert(self, alert_data: dict) -> int:
        """
        Persist alert to database
        """
        db = self.db_session_maker()
        try:
            result = db.execute(
                text("""
                    INSERT INTO sentiment_alerts (
                        alert_type,
                        threshold_value,
                        actual_value,
                        window_start,
                        window_end,
                        post_count,
                        created_at,
                        metadata
                    )
                    VALUES (
                        :alert_type,
                        :threshold,
                        :actual,
                        :start,
                        :end,
                        :count,
                        NOW(),
                        :meta
                    )
                    RETURNING id
                """),
                {
                    "alert_type": alert_data["alert_type"],
                    "threshold": alert_data["threshold"],
                    "actual": alert_data["actual_ratio"],
                    "start": datetime.utcnow() - timedelta(minutes=alert_data["window_minutes"]),
                    "end": datetime.utcnow(),
                    "count": alert_data["metrics"]["total_count"],
                    "meta": alert_data
                }
            )

            alert_id = result.scalar()
            db.commit()
            return alert_id

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    async def run_monitoring_loop(self, check_interval_seconds: int = 60):
        """
        Continuous monitoring loop
        """
        while True:
            alert = await self.check_thresholds()
            if alert:
                alert_id = await self.save_alert(alert)
                print(f"🚨 ALERT TRIGGERED (id={alert_id}):", alert, flush=True)

            await asyncio.sleep(check_interval_seconds)
