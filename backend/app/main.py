# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import redis.asyncio as redis
import json
import os

from app.models.database import init_db
from app.api import routes
from app.api.websocket import manager
from app.services.alerting import AlertService

app = FastAPI(title="Sentiment Analysis Platform")

# CORS (Allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(routes.router)

# Background Task: Redis Subscriber for WebSocket
async def redis_subscriber():
    redis_host = os.getenv("REDIS_HOST", "redis")
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe('sentiment_updates')
    
    async for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            # Broadcast to all connected WebSocket clients
            await manager.broadcast(data)

@app.on_event("startup")
async def startup_event():
    # 1. Initialize DB
    init_db()
    
    # 2. Start Alert Service
    alert_service = AlertService()
    asyncio.create_task(alert_service.run_monitoring_loop())
    
    # 3. Start Redis Subscriber
    asyncio.create_task(redis_subscriber())

@app.get("/")
def read_root():
    return {"status": "Sentiment Platform API is running"}