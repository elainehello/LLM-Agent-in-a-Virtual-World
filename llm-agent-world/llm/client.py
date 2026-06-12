import anthropic, os, re

SYSTEM = """You are an agent in a 2D grid world. Goal: find key K, unlock door D, reach goal G.

MAP SYMBOLS: # wall  . empty  ? unexplored  K key  D door  G goal  A you

NAVIGATION FACTS
- Row y=2 is almost all walls. Only x=1 and x=9 are open passages south.
- To go south: move to x=1 or x=9 first, then move down.
- If move_down fails, move left toward x=1 or right toward x=9 immediately.

RULES
- Keep reasoning SHORT (one sentence max).
- Never retry a failed move in the same direction from the same position.
- Never wait unless fully blocked.

Respond ONLY with raw JSON: {"action":"<action>","reasoning":"<one short sentence>"}"""

class LLMClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def call(self, observation: str) -> str:
        msg = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=128,
            system=SYSTEM,
            messages=[
                {"role": "user",    "content": observation},
                {"role": "assistant","content": "{"},   # prefill forces JSON start
            ]
        )
        raw = "{" + msg.content[0].text
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw.strip())
        return raw.strip()
