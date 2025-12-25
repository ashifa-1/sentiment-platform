from fastapi import FastAPI
from api.routes import router
from models.database import init_db
from api.websocket import router as websocket_router
import asyncio
from services.alerting import AlertService

app = FastAPI(title="Real-Time Sentiment Analysis API")


@app.on_event("startup")
async def start_alert_monitor():
    alert_service = AlertService()
    asyncio.create_task(alert_service.run_monitoring_loop())


@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(router)
app.include_router(websocket_router)
