from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from backend.models.database import SocialMediaPost, SentimentAnalysis
from datetime import datetime

async def save_post_and_analysis(db_session: AsyncSession, post_data: dict, sentiment: dict, emotion: dict):
    """Saves both the post and the analysis results to the database."""
    try:
        # 1. Save or Update Social Media Post
        post = SocialMediaPost(
            post_id=post_data['post_id'],
            source=post_data['source'],
            content=post_data['content'],
            author=post_data['author'],
            created_at=datetime.fromisoformat(post_data['created_at'].replace('Z', ''))
        )
        db_session.add(post)
        
        # 2. Save Sentiment Analysis result
        analysis = SentimentAnalysis(
            post_id=post_data['post_id'],
            sentiment_label=sentiment['sentiment_label'],
            confidence_score=sentiment['confidence_score'],
            emotion=emotion['emotion'],
            model_name=f"{sentiment['model_name']} + {emotion['model_name']}"
        )
        db_session.add(analysis)
        
        await db_session.commit()
        return True
    except Exception as e:
        await db_session.rollback()
        print(f"Database Error: {e}")
        return False   