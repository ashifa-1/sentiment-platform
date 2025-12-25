from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import text
from models.database import SessionLocal

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def get_metrics():
    db = SessionLocal()
    now = datetime.utcnow()

    def fetch(since):
        rows = db.execute(
            text("""
                SELECT sentiment_label, COUNT(*) 
                FROM sentiment_analysis
                WHERE analyzed_at >= :since
                GROUP BY sentiment_label
            """),
            {"since": since}
        ).all()

        data = {"positive": 0, "negative": 0, "neutral": 0}
        total = 0
        for label, count in rows:
            data[label] = count
            total += count
        data["total"] = total
        return data

    try:
        return {
            "last_minute": fetch(now - timedelta(minutes=1)),
            "last_hour": fetch(now - timedelta(hours=1)),
            "last_24_hours": fetch(now - timedelta(hours=24))
        }
    finally:
        db.close()


@router.websocket("/ws/sentiment")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    await websocket.send_json({
        "type": "connected",
        "message": "Connected to sentiment stream",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    try:
        while True:
            metrics = await get_metrics()

            await manager.broadcast({
                "type": "metrics_update",
                "data": metrics,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

            await asyncio.sleep(30)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
