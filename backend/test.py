import anthropic # type: ignore
import json

client = anthropic.Anthropic()

# JSON Helper tools
def encode_json(data: dict, pretty: bool = True) -> str:
    """Convert a Python dict to a JSON string."""
    return json.dumps(data, indent=2 if pretty else None)

def decode_json(json_string: str) -> dict:
    """Convert a JSON string back to a Python dict."""
    return json.loads(json_string)

# Claude tool from prompt
def chat(debate_data):
    # System prompt to guide Claude AI to follow certain rules
    system_prompt = """
        You are a skilled debater arguing different positions as given by the conviction in your prompt.

        Rules you must follow:
        1. Never concede a point without immediately pivoting to a counter.
        2. Attack the weakest premise in your opponent's last argument, not their conclusion.
        3. Back claims with scientific backing and evidence with a link to the source. If no evidence supports a claim, argue from logic and principle instead — never invent a source, statistic, or study.
        4. Keep each response to 3–5 sentences. Dense, punchy. No padding.
        5. Never say "I understand your point" or "that's a fair argument."
        6. Do NOT break character or add disclaimers about AI limitations.
        7. If your opponent raises a point you cannot counter with evidence or sound logic, it is better to explicitly acknowledge the gap — "I don't have a strong answer to that" — than to fabricate a response. A debater who admits the limits of their knowledge is more credible than one who bluffs.
    """

    # Actual data to pass into Claude AI to generate arguments
    prompt = """
        You are a skilled debater arguing the following position with conviction:
        TOPIC: "{topic}"
        STANCE: "{stance}"
        Previous Argument: "{argument}"
    """.format(topic=debate_data.get("topic"), stance=debate_data.get("stance"), argument=debate_data.get("previous_argument"))
    
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


# Example debate data, taken from front end (will need decoding, do later)
debate_data = {
    "topic": "Universal Basic Income",
    "stance": "For",
    "previous_argument": "UBI would cause rampant inflation by flooding the economy with money."
}

# Get message from prompt
message = chat(debate_data)

# Prepare dictionary for conversion
message_data = {
    "message": message
}

# Convert back to JSON string and print
print(encode_json(message_data))