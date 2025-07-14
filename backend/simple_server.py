#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Simple Test Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Server is running"}

@app.get("/")
async def root():
    return {"message": "Simple test server is working"}

@app.post("/api/v1/presione1/campanhas/{campaign_id}/iniciar")
async def start_campaign(campaign_id: int):
    return {
        "success": True,
        "message": f"Campaign {campaign_id} started successfully",
        "campaign_id": campaign_id
    }

if __name__ == "__main__":
    print("🚀 Starting simple server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)