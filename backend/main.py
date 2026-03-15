from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import agent
import item
from fact_checker import check_hallucinations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aigument-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/message/")
def create_item(payload: item.Item):
    max_retries = 2
    attempts = 0
    while attempts <= max_retries:
        response_message = agent.chat(payload)
        evaluation = check_hallucinations(response_message)
        
        if evaluation.get("passed") is True:
            print(f"[SUCCESS] Fact-check passed on attempt {attempts + 1}")
            return {"message": response_message}
            
        print(f"[FAILED] Hallucination detected. Regenerating. Reason: {evaluation.get('reason')}")
        attempts += 1

    return {"message": "I must acknowledge that the data required to counter that specific point definitively is currently unavailable."}