import os
import time
import json
import redis
import torch
from sqlalchemy.orm import Session

from backend/models.database import SessionLocal
from backend/models.sentiment import SentimentAnalysis
from sentiment_model import SentimentModel


class SentimentWorker:
    def __init__(self):
        print("🧩 Worker initialized")

        # Redis config
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

        # Sentiment model
        self.model = SentimentModel()

        print("🚀 Worker running")

    # ✅ REQUIRED: create consumer group safely
    def ensure_consumer_group(self):
        try:
            self.redis.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id="0",
                mkstream=True
            )
            print("✅ Consumer group created")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print("ℹ️ Consumer group already exists")
            else:
                raise

    def process_message(self, message_id, data):
        db: Session = SessionLocal()

        try:
            content = data.get("content", "")
            source = data.get("source", "")
            author = data.get("author", "")
            created_at = data.get("created_at")

            sentiment_label, sentiment_score = self.model.predict(content)

            record = SentimentAnalysis(
                post_id=data.get("post_id"),
                source=source,
                author=author,
                content=content,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score
            )

            db.add(record)
            db.commit()

            print(f"✅ Processed {message_id} → {sentiment_label}")

        except Exception as e:
            db.rollback()
            print("❌ Error processing message:", e)

        finally:
            db.close()

    def run(self):
        self.ensure_consumer_group()

        while True:
            try:
                messages = self.redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=5,
                    block=5000
                )

                for stream, entries in messages:
                    for message_id, data in entries:
                        self.process_message(message_id, data)
                        self.redis.xack(
                            self.stream_name,
                            self.consumer_group,
                            message_id
                        )

            except Exception as e:
                print("🔥 Worker fatal error, restarting loop:", e)
                time.sleep(2)


if __name__ == "__main__":
    worker = SentimentWorker()
    worker.run()
