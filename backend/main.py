import uuid
from datetime import datetime
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import anthropic
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from fastapi import FastAPI

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class Message(BaseModel):
    role: str
    content: str

class DebateRequest(BaseModel):
    stance: str
    core_argument: str
    evidence_bullets: str
    messages: List[dict]

class For(BaseModel):
    stance: str
# --- Shared logic ---

def get_debater_response(stance: str, core_argument: str, evidence_bullets: str, messages: list):
    system_prompt = f"""You are a skilled debater arguing the following position with conviction:
STANCE: {stance}
CORE ARGUMENT: {core_argument}

EVIDENCE BANK (sourced before the debate — use only these):
{evidence_bullets}

Rules you must follow:
1. Never concede a point without immediately pivoting to a counter.
2. Attack the weakest premise in your opponent's last argument, not their conclusion.
3. Back claims with evidence from the EVIDENCE BANK above. Never invent a source.
4. Keep each response to 3–5 sentences. Dense, punchy. No padding.
5. Never say "I understand your point" or "that's a fair argument."
6. Do NOT break character or add disclaimers about AI limitations.
7. If you cannot counter with evidence or logic, acknowledge the gap honestly.
8. Do not add unneccessary '-' symbols in your answers"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text

# --- Routes ---

@app.get("/")
def root():
    return {"message": "Debate API is running"}

@app.post("/debate/both")
def debate_both(req: DebateRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    try:
        for_reply = get_debater_response(req.stance, req.core_argument, req.evidence_bullets, req.messages)
        against_reply = get_debater_response(
            f"AGAINST: {req.stance}",
            f"The opposite is true — {req.core_argument} is flawed or overstated.",
            req.evidence_bullets,
            req.messages
        )

        result = {"for": for_reply, "against": against_reply}

        # Save to JSON file
        os.makedirs("debates", exist_ok=True)
        filename = f"debates/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
        with open(filename, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stance": req.stance,
                "core_argument": req.core_argument,
                "result": result
            }, f, indent=2)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debate/full")
def debate_full(req: DebateRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    try:
        rounds = []
        for_messages = list(req.messages)
        against_messages = list(req.messages)

        for i in range(3):
            print(f"\n--- Round {i+1} ---")

            for_reply = get_debater_response(
                req.stance, req.core_argument, req.evidence_bullets, for_messages
            )
            print(f"[FOR]: {for_reply}\n")  # appears immediately

            against_messages.append({"role": "user", "content": for_reply})

            against_reply = get_debater_response(
                f"AGAINST: {req.stance}",
                f"The opposite is true — {req.core_argument} is flawed or overstated.",
                req.evidence_bullets,
                against_messages
            )
            print(f"[AGAINST]: {against_reply}\n")  # appears as soon as it's ready

            for_messages.append({"role": "assistant", "content": for_reply})
            for_messages.append({"role": "user", "content": against_reply})
            against_messages.append({"role": "assistant", "content": against_reply})

            rounds.append({"round": i + 1, "for": for_reply, "against": against_reply})

        return {"rounds": rounds}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))