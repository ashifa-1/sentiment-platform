from fastapi import FastAPI
from models.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    # This creates the tables in PostgreSQL automatically
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")