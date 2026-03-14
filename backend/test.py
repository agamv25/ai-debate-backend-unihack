import anthropic # type: ignore

client = anthropic.Anthropic()


class ai_agent:
    # Maintain a list of messages as your "memory"

    def __init__(self, topic, stance):
        self.conversation_history = []

        # First prompt to give to AI
        first_prompt = """
        You are a skilled debater arguing the following position with conviction:
            TOPIC: "{topic}"
            STANCE: "{stance}" (For / Against)

            Rules you must follow:
            1. Never concede a point without immediately pivoting to a counter.
            2. Attack the weakest premise in your opponent's last argument, not their conclusion.
            3. Back claims with scientific backing and evidence with a link to the source. If no evidence supports a claim, argue from logic and principle instead — never invent a source, statistic, or study.
            4. Keep each response to 3–5 sentences. Dense, punchy. No padding.
            5. Never say "I understand your point" or "that's a fair argument."
            6. Do NOT break character or add disclaimers about AI limitations.
            7. If your opponent raises a point you cannot counter with evidence or sound logic, it is better to explicitly acknowledge the gap — "I don't have a strong answer to that" — than to fabricate a response. A debater who admits the limits of their knowledge is more credible than one who bluffs.
        """

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": first_prompt
        })
        
        # Send full history with each request
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=first_prompt,
            messages=self.conversation_history  # Pass the entire history
        )
        
        # Extract assistant reply
        assistant_message = response.content[0].text
        
        # Add assistant reply to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    

    def chat(self, topic, stance, argument):
        new_prompt = """
            You are a skilled debater arguing the following position with conviction:
            TOPIC: "{topic}"
            STANCE: "{stance}" (For / Against)
            PREVIOUS ARGUMENT: "{argument}"

        """.format(topic=topic, stance=stance, argument=argument)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": new_prompt
        })
        
        # Send full history with each request
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=new_prompt,
            messages=self.conversation_history  # Pass the entire history
        )
        
        # Extract assistant reply
        assistant_message = response.content[0].text
        
        # Add assistant reply to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message

# Example usage
topic = "Should micro-plastics be banned in Australia?"

argument1For = chat("")

print(chat("My name is Alice."))
print(chat("What's my name?"))  # Claude will remember "Alice"
print(chat("Summarize what we've talked about."))