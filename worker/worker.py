import os
import time
import json
import redis
import logging
from datetime import datetime

# Import modules from the backend (mounted via Docker volume)
# This allows us to reuse the AI logic and DB models without copying code!
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.models.database import SessionLocal, SocialMediaPost, SentimentAnalysis, init_db

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentWorker:
    def __init__(self):
        # 1. Setup Redis
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.stream_name = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
        self.group_name = os.getenv("REDIS_CONSUMER_GROUP", "sentiment_workers")
        self.consumer_name = f"worker_{os.uname().nodename}" # Unique ID for this container

        self.redis = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)

        # 2. Setup Database
        # Wait for DB to be ready (init_db creates tables if they don't exist)
        # In a real app, we might use a retry loop here
        time.sleep(5) 
        init_db()

        # 3. Setup AI Analyzer
        logger.info("Loading Sentiment Analyzer model... (this may take time on first run)")
        self.analyzer = SentimentAnalyzer(model_type='local')
        logger.info("Sentiment Analyzer loaded.")

        # 4. Create Consumer Group
        self._create_consumer_group()

    def _create_consumer_group(self):
        """Creates the Redis Consumer Group if it doesn't exist."""
        try:
            # '0' means start consuming from the beginning of the stream
            self.redis.xgroup_create(self.stream_name, self.group_name, id='0', mkstream=True)
            logger.info(f"Consumer group '{self.group_name}' created.")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{self.group_name}' already exists.")
            else:
                logger.error(f"Error creating consumer group: {e}")
                raise

    def process_message(self, message_id, message_data):
        """Process a single message: Analyze -> Save to DB -> Publish Update."""
        db = SessionLocal()
        try:
            # 1. Parse Data (Existing code)
            post_id = message_data.get('post_id')
            content = message_data.get('content')
            source = message_data.get('source')
            author = message_data.get('author')
            created_at_str = message_data.get('created_at')
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))

            logger.info(f"Processing post {post_id}: {content[:30]}...")

            # 2. Save Raw Post (Existing code)
            existing_post = db.query(SocialMediaPost).filter(SocialMediaPost.post_id == post_id).first()
            if not existing_post:
                new_post = SocialMediaPost(
                    post_id=post_id,
                    source=source,
                    content=content,
                    author=author,
                    created_at=created_at
                )
                db.add(new_post)
                db.commit()

            # 3. Run Analysis (Existing code)
            import asyncio
            sentiment_result = asyncio.run(self.analyzer.analyze_sentiment(content))
            emotion_result = asyncio.run(self.analyzer.analyze_emotion(content))

            # 4. Save Analysis Result (Existing code)
            analysis_record = SentimentAnalysis(
                post_id=post_id,
                model_name=sentiment_result.get('model_name'),
                sentiment_label=sentiment_result.get('sentiment_label'),
                confidence_score=sentiment_result.get('confidence_score'),
                emotion=emotion_result.get('emotion')
            )
            db.add(analysis_record)
            db.commit()

            # --- NEW STEP 5: Publish Update to Redis Channel ---
            update_message = {
                "type": "new_post",
                "data": {
                    "post_id": post_id,
                    "content": content[:100], # Truncate for performance
                    "source": source,
                    "sentiment_label": sentiment_result.get('sentiment_label'),
                    "confidence_score": sentiment_result.get('confidence_score'),
                    "emotion": emotion_result.get('emotion'),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            # Publish to 'sentiment_updates' channel
            self.redis.publish('sentiment_updates', json.dumps(update_message))
            
            logger.info(f"Saved analysis: {sentiment_result['sentiment_label']}")

        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            db.rollback()
        finally:
            db.close()

    def start(self):
        """Main Loop"""
        logger.info(f"Worker {self.consumer_name} started listening on {self.stream_name}...")
        
        while True:
            try:
                # XREADGROUP reads new messages for this group
                # '>' means "give me messages that have never been delivered to other workers"
                entries = self.redis.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: '>'},
                    count=1,
                    block=2000 # Block for 2 seconds if no data
                )

                if not entries:
                    continue

                for stream, messages in entries:
                    for message_id, message_data in messages:
                        self.process_message(message_id, message_data)
                        
                        # Acknowledge processing (remove from pending list)
                        self.redis.xack(self.stream_name, self.group_name, message_id)

            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    worker = SentimentWorker()
    worker.start()