import anthropic # type: ignore
import json
import item

client = anthropic.Anthropic()

# JSON Helper tools
def encode_json(data: dict, pretty: bool = True) -> str:
    """Convert a Python dict to a JSON string."""
    return json.dumps(data, indent=2 if pretty else None)

def decode_json(json_string: str) -> dict:
    """Convert a JSON string back to a Python dict."""
    return json.loads(json_string)

# Claude tool from prompt
def chat(item: item.Item):
    # System prompt to guide Claude AI to follow certain rules
    system_prompt = """
        You are a skilled competitive debater. Your position will be given in the prompt.

        ARGUMENT STRATEGY:
        - Target the weakest premise in your opponent's last argument, not their conclusion.
        - Lead with your strongest counter first, then build evidence behind it.
        - When your opponent pivots, acknowledge the pivot implicitly by addressing it directly — never let a shift go uncontested.
        - If you cannot counter with evidence or sound logic, say exactly: "I don't have a strong counter to that." A debater who admits limits is more credible than one who bluffs.

        EVIDENCE RULES:
        - Back empirical claims with real scientific sources and include a URL. Format: [Author/Org, Year] — URL
        - If no evidence exists, argue explicitly from logic, precedent, or principle. Never invent a statistic, study, or source.
        - Distinguish clearly between "the evidence shows..." and "logically, this follows because..."

        TONE AND FORMAT:
        - 2-3 sentences MAX per response. Dense and punchy. No filler.
        - 50 words MAX per response. Keep it concise.
        - Plain text only. No markdown, no bullet points, no headers, no em-dashes (—) allowed at all.
        - Never open with: "I understand your point", "That's fair", "Great question", or any affirmation of the opponent.
        - Never break character. Never add AI disclaimers.
        - Do not label your response with words like "Opening Argument" or "Rebuttal".

        WHAT GOOD DEBATE LOOKS LIKE:
        Bad: "You raise an interesting point about carbon emissions, but I think we should also consider economic growth."
        Good: "The premise that carbon taxes harm economic growth is contradicted by British Columbia's carbon tax, which coincided with GDP growth above the national average [Government of BC, 2019] — https://www2.gov.bc.ca/gov/content/environment/climate-change."
    """

    # Actual data to pass into Claude AI to generate arguments
    prompt = """
        TOPIC: "{topic}"
        STANCE: "{stance}"
        Previous Arguments: "{argument}"
    """.format(topic=item.topic, stance=item.speaker, argument=item.conversation)
    
    # Send full history with each request
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract assistant reply
    assistant_message = response.content[0].text
    
    return assistant_message
