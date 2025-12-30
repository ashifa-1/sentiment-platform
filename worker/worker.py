import asyncio
import json
import os
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from worker.processor import save_post_and_analysis # We will create this next

class SentimentWorker:
    def __init__(self, redis_client, db_session_maker, stream_name, consumer_group):
        self.redis = redis_client
        self.db_session_maker = db_session_maker
        self.stream_name = stream_name
        self.group = consumer_group

    async def setup_group(self):
        """Creates the consumer group in Redis if it doesn't exist."""
        try:
            await self.redis.xgroup_create(self.stream_name, self.group, mkstream=True)
        except Exception:
            pass # Group already exists

    async def run(self):
        await self.setup_group()
        print("Worker started: Listening for posts...")
        
        while True:
            # Rule: Must use XREADGROUP to get new messages
            messages = await self.redis.xreadgroup(self.group, "worker_1", {self.stream_name: ">"}, count=1, block=5000)
            
            for stream, payload in messages:
                for msg_id, data in payload:
                    post_data = json.loads(data[b'data'])
                    
                    # 1. Run AI Sentiment Analysis (Phase 3)
                    # (Code to call your SentimentAnalyzer from previous step)
                    
                    # 2. Save to Database
                    async with self.db_session_maker() as session:
                        # Logic to save to PostgreSQL
                        pass
                    
                    # 3. Rule: Must use XACK to acknowledge processing
                    await self.redis.xack(self.stream_name, self.group, msg_id)