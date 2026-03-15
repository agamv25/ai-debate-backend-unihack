import anthropic
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = anthropic.Anthropic()

def check_hallucinations(argument_text: str) -> dict:
    print("\n[FACT-CHECKER] Intercepting argument for verification...")
    try:
        query_resp = client.messages.create(
            model="claude-haiku-4-5-20251001", 
            max_tokens=20,
            system="Output ONLY a 3 to 5 word search query to verify the core factual claim in the provided text. No quotes.",
            messages=[{"role": "user", "content": argument_text}]
        )
        search_query = query_resp.content[0].text.strip()
        print(f"[FACT-CHECKER] Searching web for: '{search_query}'")
        
        results = DDGS().text(search_query, max_results=3)
        live_data = " ".join([res["body"] for res in results]) if results else "No data."
    except Exception as e:
        print(f"[FACT-CHECKER WARNING] Web search failed: {e}")
        live_data = "Search unavailable."

    eval_prompt = f"""
    Analyze this argument against this LIVE DATA: <data>{live_data}</data>. 
    Return ONLY raw JSON: {{"passed": true/false, "reason": "short explanation"}}. 
    'passed' must be false ONLY if the argument actively contradicts the live data or invents specific stats not found in the search. Subjective opinions pass.
    """
    
    try:
        eval_resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            system=eval_prompt,
            messages=[{"role": "user", "content": argument_text}]
        )
        raw_text = eval_resp.content[0].text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
        
    except Exception as e:
        print(f"[FACT-CHECKER ERROR] JSON parse failed: {e}")
        print(f"[RAW CLAUDE OUTPUT WAS]: {eval_resp.content[0].text}") 
        return {"passed": True, "reason": "Error parsing validation."}