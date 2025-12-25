import os
import asyncio
import random
import uuid
import logging
from datetime import datetime
import redis.asyncio as redis
from redis.exceptions import RedisError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataIngester")


class DataIngester:
    """
    Publishes simulated social media posts to Redis Stream
    """

    def __init__(self, redis_client, stream_name: str, posts_per_minute: int = 20):
        self.redis = redis_client
        self.stream_name = stream_name
        self.posts_per_minute = posts_per_minute
        self.sleep_time = 60.0 / posts_per_minute

        self.products = [
            "iPhone 16",
            "Tesla Model 3",
            "ChatGPT",
            "Netflix",
            "Amazon Prime",
            "Spotify",
            "Instagram"
        ]

        self.positive_templates = [
            "I absolutely love {product}! Highly recommended.",
            "{product} exceeded my expectations. Amazing experience!",
            "Great quality and performance from {product}."
        ]

        self.neutral_templates = [
            "Just tried {product}.",
            "Using {product} for the first time.",
            "Received {product} today."
        ]

        self.negative_templates = [
            "Very disappointed with {product}.",
            "Terrible experience using {product}.",
            "I regret buying {product}. Not worth it."
        ]

    def generate_post(self) -> dict:
        sentiment_choice = random.choices(
            ["positive", "neutral", "negative"],
            weights=[40, 30, 30]
        )[0]

        product = random.choice(self.products)

        if sentiment_choice == "positive":
            content = random.choice(self.positive_templates).format(product=product)
        elif sentiment_choice == "neutral":
            content = random.choice(self.neutral_templates).format(product=product)
        else:
            content = random.choice(self.negative_templates).format(product=product)

        return {
            "post_id": f"post_{uuid.uuid4()}",
            "source": random.choice(["twitter", "reddit"]),
            "content": content,
            "author": f"user_{random.randint(1000, 9999)}",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    async def publish_post(self, post_data: dict) -> bool:
        try:
            await self.redis.xadd(self.stream_name, post_data)
            logger.info(f"Published post {post_data['post_id']}")
            return True
        except RedisError as e:
            logger.error(f"Redis publish failed: {e}")
            return False

    async def start(self, duration_seconds: int = None):
        logger.info("🚀 DataIngester started")

        start_time = datetime.utcnow()

        try:
            while True:
                post = self.generate_post()
                await self.publish_post(post)

                if duration_seconds:
                    elapsed = (datetime.utcnow() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        break

                await asyncio.sleep(self.sleep_time)

        except KeyboardInterrupt:
            logger.info("🛑 Ingester stopped gracefully")


async def main():
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True
    )

    ingester = DataIngester(
        redis_client=redis_client,
        stream_name=os.getenv("REDIS_STREAM_NAME"),
        posts_per_minute=60
    )

    await ingester.start()


if __name__ == "__main__":
    asyncio.run(main())
