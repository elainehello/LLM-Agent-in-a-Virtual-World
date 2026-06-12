import json
from dataclasses import dataclass, field
from typing import Literal

ActionName = Literal[
    "move_up","move_down","move_left","move_right",
    "pick_up","use_item","wait"
]

ACTION_DESCRIPTIONS = {
    "move_up":    "Move north one cell",
    "move_down":  "Move south one cell",
    "move_left":  "Move west one cell",
    "move_right": "Move east one cell",
    "pick_up":    "Pick up object at current position",
    "use_item":   "Use held item on adjacent interactable",
    "wait":       "Stay in place — ONLY use if completely blocked with no valid moves",
}

FALLBACK = "wait"

@dataclass
class ActionResult:
    action:  str
    outcome: Literal["success", "failed"]
    events:  list[str] = field(default_factory=list)
    # events examples: ["found_key"], ["picked_up_key"],
    #                  ["door_unlocked"], ["wall_collision"],
    #                  ["entered_room"], ["goal_visible"]

    def to_prompt_section(self) -> str:
        lines = [
            "LAST ACTION RESULT",
            f"Action:  {self.action}",
            f"Outcome: {self.outcome}",
        ]
        if self.events:
            lines.append(f"Events:  {', '.join(self.events)}")
        return "\n".join(lines)


def validate(llm_output: str, world, agent) -> tuple[str, str | None]:
    """Returns (action_name, error_or_None). Invalid → wait."""
    try:
        data = json.loads(llm_output.strip())
    except (json.JSONDecodeError, ValueError):
        return FALLBACK, "invalid_json"

    action = data.get("action", "")
    if action not in ACTION_DESCRIPTIONS:
        return FALLBACK, "unknown_action"

    return action, None
