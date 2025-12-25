from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time
import sys
import os
import redis
from services.sentiment_analyzer import SentimentAnalyzer
import asyncio


class SentimentWorker:
    def __init__(self):
        print("🧩 Worker __init__ called", flush=True)

        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.stream_name = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
        self.consumer_group = os.getenv("REDIS_CONSUMER_GROUP", "sentiment_workers")
        self.consumer_name = f"worker-{os.getpid()}"

        self.redis = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True
        )
        db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.analyzer = SentimentAnalyzer()


    def ensure_consumer_group(self):
        print("🔧 Ensuring consumer group...", flush=True)
        try:
            self.redis.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id="0",
                mkstream=True
            )
            print("✅ Consumer group created", flush=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print("ℹ️ Consumer group already exists", flush=True)
            else:
                raise


    def save_to_db(self, post_data, sentiment, emotion):
        session = self.SessionLocal()
        try:
            # Insert or update post
            session.execute(
                """
                INSERT INTO social_media_posts
                (post_id, source, content, author, created_at, ingested_at)
                VALUES (:post_id, :source, :content, :author, :created_at, :ingested_at)
                ON CONFLICT (post_id)
                DO UPDATE SET ingested_at = EXCLUDED.ingested_at
                """,
                {
                    "post_id": post_data.get("post_id"),
                    "source": post_data.get("source"),
                    "content": post_data.get("content"),
                    "author": post_data.get("author"),
                    "created_at": post_data.get("created_at"),
                    "ingested_at": datetime.utcnow(),
                }
            )

            # Insert sentiment analysis
            session.execute(
                """
                INSERT INTO sentiment_analysis
                (post_id, model_name, sentiment_label, confidence_score, emotion, analyzed_at)
                VALUES (:post_id, :model_name, :sentiment_label, :confidence_score, :emotion, :analyzed_at)
                """,
                {
                    "post_id": post_data.get("post_id"),
                    "model_name": sentiment["model_name"],
                    "sentiment_label": sentiment["sentiment_label"],
                    "confidence_score": sentiment["confidence_score"],
                    "emotion": emotion["emotion"],
                    "analyzed_at": datetime.utcnow(),
                }
            )

            session.commit()
            print("💾 Saved to database", flush=True)

        except Exception as e:
            session.rollback()
            print("❌ DB error:", e, flush=True)
            raise
        finally:
            session.close()



    def run(self):
        print("🚀 Worker started and waiting for messages...", flush=True)

        self.ensure_consumer_group()

        while True:
            messages = self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=self.consumer_name,
                streams={self.stream_name: ">"},
                count=1,
                block=5000
            )

            if not messages:
                continue

            for stream, entries in messages:
                for message_id, data in entries:
                    print(f"\n📩 Processing message {message_id}", flush=True)
                    print("Raw data:", data, flush=True)

                    content = data.get("content", "")

                    sentiment = asyncio.run(
                        self.analyzer.analyze_sentiment(content)
                    )
                    emotion = asyncio.run(
                        self.analyzer.analyze_emotion(content)
                    )

                    print("🧠 Sentiment result:", sentiment, flush=True)
                    print("🎭 Emotion result:", emotion, flush=True)
                    self.save_to_db(data, sentiment, emotion)




if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)

    print("🔥 Worker main entry reached", flush=True)
    worker = SentimentWorker()
    worker.run()
