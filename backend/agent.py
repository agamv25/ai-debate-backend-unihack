import anthropic 
import json
import item
import os
from pathlib import Path
from dotenv import load_dotenv
from duckduckgo_search import DDGS


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = anthropic.Anthropic()

def extract_and_search(conversation: list) -> str:
    if not conversation:
        return "No prior arguments to search."
    history_str = "\n".join([f"[{m.speaker.upper()}]: {m.message}" for m in conversation])
    
    try:
        print("[SYSTEM] Running Lite-RAG search...")
        query_resp = client.messages.create(
            model="claude-haiku-4-5-20251001", 
            max_tokens=20,
            system="Read the debate history. Output ONLY a 3 to 5 word search query to verify the very last claim made. No quotes.",
            messages=[{"role": "user", "content": history_str}]
        )
        search_query = query_resp.content[0].text.strip()
        print(f"[SYSTEM] Searching internet for: '{search_query}'")
        
        results = DDGS().text(search_query, max_results=3)
        return " ".join([res["body"] for res in results]) if results else "No internet data found."
    except Exception as e:
        print(f"[WARNING] Web search failed: {e}")
        return "Live search unavailable."

def chat(item_data: item.Item) -> str:
    live_facts = extract_and_search(item_data.conversation)
    history_str = "\n".join([f"[{m.speaker.upper()}]: {m.message}" for m in item_data.conversation])

   
    system_prompt = f"""
        You are a skilled competitive debater. Your position will be given in the prompt.

        CRITICAL: Here is live internet data regarding the topic or opponent's last point:
        <live_data>{live_facts}</live_data>

        ARGUMENT STRATEGY:
        - Target the weakest premise using the <live_data> provided.
        - Lead with your strongest counter first, then build evidence behind it.
        - When your opponent pivots, acknowledge the pivot implicitly by addressing it directly — never let a shift go uncontested.
        - If you cannot counter with evidence or sound logic, say exactly: "I don't have a strong counter to that." A debater who admits limits is more credible than one who bluffs.

        EVIDENCE RULES:
        - Back empirical claims with scientific backing from the <live_data>.
        - If no evidence exists in the live data, argue explicitly from logic, precedent, or principle. Never invent a statistic, study, or source.
        - Distinguish clearly between "the evidence shows..." and "logically, this follows because..."

        TONE AND FORMAT:
        - 2-3 sentences MAX per response. Dense and punchy. No filler.
        - 50 words MAX per response. Keep it concise.
        - Plain text only. No markdown, no bullet points, no headers, no em-dashes allowed at all.
        - Never open with: "I understand your point", "That's fair", "Great question", or any affirmation of the opponent.
        - Never break character. Never add AI disclaimers.
        - Do not label your response with words like "Opening Argument" or "Rebuttal".
    """
    prompt = f"""
        TOPIC: "{item_data.topic}"
        STANCE: "{item_data.speaker}"
        Previous Arguments: "{history_str}"
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text