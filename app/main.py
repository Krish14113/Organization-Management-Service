from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.org_router import router as org_router
from app.core.config import settings
from app.db import client

app = FastAPI(title="Org Management Backend")

# Simple CORS — change origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(org_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
