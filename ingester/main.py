import asyncio
import os
import redis.asyncio as redis
from ingester import DataIngester

async def main():
    # Connect to Redis using the hostname defined in docker-compose
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    stream_name = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
    
    # Initialize Redis client
    client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    # Initialize the Ingester (Phase 2)
    # Defaulting to 60 posts per minute as per requirements
    ingester = DataIngester(
        redis_client=client, 
        stream_name=stream_name,
        posts_per_minute=60
    )
    
    print(f"Ingester started. Publishing to stream: {stream_name}")
    
    try:
        await ingester.start()
    except KeyboardInterrupt:
        print("Ingester shutting down...")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())