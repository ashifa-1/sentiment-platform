import asyncio
import redis.asyncio as redis
from backend.models.database import AsyncSessionLocal
from worker.worker import SentimentWorker # Class we defined in the previous turn
from backend.services.sentiment_analyzer import SentimentAnalyzer


async def main():
    # Setup dependencies
    redis_client = redis.from_url(f"redis://{os.getenv('REDIS_HOST')}")
    analyzer = SentimentAnalyzer(model_type='local')
    
    worker = SentimentWorker(
        redis_client=redis_client,
        db_session_maker=AsyncSessionLocal,
        stream_name=os.getenv("REDIS_STREAM_NAME"),
        consumer_group=os.getenv("REDIS_CONSUMER_GROUP")
    )
    
    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())