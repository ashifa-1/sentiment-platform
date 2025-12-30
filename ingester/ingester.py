import asyncio
import json
import random
import uuid
from datetime import datetime
import redis.asyncio as redis

class DataIngester:
    def __init__(self, redis_client, stream_name, posts_per_minute=60):
        self.redis = redis_client
        self.stream_name = stream_name
        self.delay = 60.0 / posts_per_minute

    async def generate_post(self) -> dict:
        products = ["iPhone 16", "Tesla Model 3", "ChatGPT", "Netflix"]
        pos_templates = ["I absolutely love {p}!", "This {p} is amazing!", "{p} exceeded my expectations!"]
        neg_templates = ["Very disappointed with {p}", "Terrible experience with {p}", "Would not recommend {p}"]
        
        # Weighted sentiment: 40% pos, 30% neu, 30% neg
        choice = random.random()
        if choice < 0.4:
            content = random.choice(pos_templates).format(p=random.choice(products))
        elif choice < 0.7:
            content = f"Just tried {random.choice(products)} today."
        else:
            content = random.choice(neg_templates).format(p=random.choice(products))

        return {
            "post_id": str(uuid.uuid4()),
            "source": random.choice(["reddit", "twitter"]),
            "content": content,
            "author": f"user_{random.randint(100, 999)}",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    async def publish_post(self, post_data: dict) -> bool:
        try:
            # Rule: Must use XADD command
            await self.redis.xadd(self.stream_name, {"data": json.dumps(post_data)})
            return True
        except Exception as e:
            print(f"Redis connection error: {e}")
            return False

    async def start(self):
        while True:
            post = await self.generate_post()
            await self.publish_post(post)
            print(f"Published post: {post['post_id']}")
            await asyncio.sleep(self.delay)