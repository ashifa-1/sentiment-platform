# backend/app/services/alerting.py
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.database import SessionLocal, SentimentAnalysis, SentimentAlert

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.threshold = 2.0 # Ratio of Negative to Positive
        self.window_minutes = 5
        self.min_posts = 5

    async def check_thresholds(self):
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=self.window_minutes)

            # Get counts
            results = db.query(
                SentimentAnalysis.sentiment_label, func.count(SentimentAnalysis.id)
            ).filter(SentimentAnalysis.analyzed_at >= window_start).group_by(SentimentAnalysis.sentiment_label).all()

            counts = {"positive": 0, "negative": 0, "neutral": 0}
            for label, count in results:
                if label in counts:
                    counts[label] = count

            total = sum(counts.values())
            
            if total < self.min_posts:
                return

            # Avoid division by zero
            pos_count = counts["positive"] if counts["positive"] > 0 else 1
            ratio = counts["negative"] / pos_count

            if ratio > self.threshold:
                logger.warning(f"ALERT TRIGGERED: Negative Ratio {ratio:.2f}")
                    
                # Save Alert
                alert = SentimentAlert(
                    alert_type="high_negative_ratio",
                    threshold_value=self.threshold,
                    actual_value=ratio,
                    window_start=window_start,
                    window_end=now,
                    post_count=total,
                    details=counts
                )
                db.add(alert)
                db.commit()

        except Exception as e:
            logger.error(f"Alert check failed: {e}")
        finally:
            db.close()

    async def run_monitoring_loop(self):
        logger.info("Starting Alert Monitoring Loop...")
        while True:
            await self.check_thresholds()
            await asyncio.sleep(60) # Check every minute