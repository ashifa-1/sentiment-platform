from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import text
from models.database import SessionLocal

router = APIRouter()


@router.websocket("/ws/sentiment")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            db = SessionLocal()
            now = datetime.utcnow()

            rows = db.execute(
                text("""
                SELECT sentiment_label, COUNT(*)
                FROM sentiment_analysis
                WHERE analyzed_at >= :since
                GROUP BY sentiment_label
                """),
                {"since": now - timedelta(hours=24)}
            ).all()
            db.close()

            metrics = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
            for label, count in rows:
                metrics[label] = count
                metrics["total"] += count

            await ws.send_json({
                "type": "metrics_update",
                "data": {"last_24_hours": metrics},
                "timestamp": now.isoformat()
            })

            await asyncio.sleep(15)

    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected")
