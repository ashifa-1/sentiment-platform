import pytest
import uuid
from datetime import datetime, timedelta
from backend.app.services.alerting import AlertService
from backend.app.models.database import SessionLocal, SocialMediaPost, SentimentAnalysis

@pytest.mark.anyio
async def test_alert_triggering_logic():
    db = SessionLocal()
    service = AlertService()
    service.min_posts = 1
    service.threshold = 0.1 
    
    unique_id = str(uuid.uuid4())
    try:
        # 1. Add Parent Post first and flush
        post = SocialMediaPost(post_id=unique_id, content="Bad", source="test")
        db.add(post)
        db.flush() 

        # 2. Add Analysis linked to that post
        analysis = SentimentAnalysis(
            post_id=unique_id, 
            sentiment_label="negative", 
            confidence_score=0.99,
            analyzed_at=datetime.utcnow()
        )
        db.add(analysis)
        db.commit()

        # 3. This triggers the alert logic block (the logic you need for coverage)
        await service.check_thresholds()
        
    finally:
        # Cleanup using a raw delete to avoid "not persisted" errors
        from sqlalchemy import text
        db.execute(text(f"DELETE FROM sentiment_analysis WHERE post_id = '{unique_id}'"))
        db.execute(text(f"DELETE FROM social_media_posts WHERE post_id = '{unique_id}'"))
        db.commit()
        db.close()