import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import agent
import item

# Load .env from project root so it works when running from backend/
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# CORS: comma-separated origins, e.g. "http://localhost:3000,https://app.example.com"
_cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()]

app = FastAPI()

# CORS: Allow requests from allowed domains from .env file
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Listen to POST requests sent to /message/, get AI response
@app.post("/message/")
def create_item(item: item.Item):
    response_message = agent.chat(item)
    return {"message": response_message}
