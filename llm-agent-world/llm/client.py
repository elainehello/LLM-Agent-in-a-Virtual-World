import anthropic, os

SYSTEM = """You are an agent in a 2D grid world. Each step you receive
an observation and must choose one action.
Respond ONLY with valid JSON: {"action":"<action>","reasoning":"<why>"}
No other text. No markdown. Just the JSON object."""

class LLMClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def call(self, observation: str) -> str:
        msg = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            system=SYSTEM,
            messages=[{"role":"user","content": observation}]
        )
        return msg.content[0].text
