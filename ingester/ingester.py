# ingester/ingester.py
import os
import time
import random
import uuid
import json
import redis
from datetime import datetime

class DataIngester:
    def __init__(self, redis_host, redis_port, stream_name, posts_per_minute=60):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.stream_name = stream_name
        self.posts_per_minute = posts_per_minute
        print(f"Ingester initialized. Target: {posts_per_minute} posts/min")

    def generate_post(self):
        """Generates a realistic social media post."""
        sources = ['twitter', 'reddit', 'facebook']
        products = ['iPhone 16', 'Tesla Model 3', 'ChatGPT', 'Netflix']
        
        # Templates
        pos_templates = ["I absolutely love {}", "{} is amazing!", "Best purchase ever: {}"]
        neg_templates = ["Hate {}", "{} is terrible", "Disappointed with {}"]
        neu_templates = ["Just bought {}", "Thinking about {}", "Saw an ad for {}"]
        
        sentiment_roll = random.random()
        product = random.choice(products)
        
        if sentiment_roll < 0.4: # 40% Positive
            content = random.choice(pos_templates).format(product)
        elif sentiment_roll < 0.7: # 30% Negative
            content = random.choice(neg_templates).format(product)
        else: # 30% Neutral
            content = random.choice(neu_templates).format(product)

        return {
            'post_id': str(uuid.uuid4()),
            'source': random.choice(sources),
            'content': content,
            'author': f"user_{random.randint(1000, 9999)}",
            'created_at': datetime.utcnow().isoformat()
        }

    def publish_post(self, post_data):
        try:
            # XADD adds to the stream
            self.redis_client.xadd(self.stream_name, post_data)
            return True
        except redis.RedisError as e:
            print(f"Error publishing to Redis: {e}")
            return False

    def start(self):
        print(f"Starting ingestion to stream: {self.stream_name}")
        while True:
            post = self.generate_post()
            success = self.publish_post(post)
            
            if success:
                print(f"Published: {post['content'][:30]}...")
            
            # Rate limiting logic
            sleep_time = 60.0 / self.posts_per_minute
            time.sleep(sleep_time)

if __name__ == "__main__":
    # Load config from env
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
    
    ingester = DataIngester(REDIS_HOST, REDIS_PORT, STREAM_NAME)
    
    # Wait for Redis to be ready
    time.sleep(5) 
    ingester.start()