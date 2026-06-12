from dataclasses import dataclass, field
from typing import Any

@dataclass
class WorldModel:
    known_cells:          dict              = field(default_factory=dict)
    known_key_location:   tuple | None      = None
    known_door_location:  tuple | None      = None
    has_key:              bool              = False
    action_history:       list              = field(default_factory=list)

    def update_from_observation(self, local_view: list[tuple[Any, Any]]):
        for pos, char in local_view:
            self.known_cells[pos] = char
            if char == "K" and self.known_key_location is None:
                self.known_key_location = pos
            if char == "D" and self.known_door_location is None:
                self.known_door_location = pos

    def update_from_result(self, result, pos: tuple):
        self.action_history.append({
            "action": result.action,
            "events": result.events,
            "pos":    pos,
        })
        if "picked_up_key"  in result.events: self.has_key = True
        if "door_unlocked"  in result.events: self.has_key = False
        if "key_location_known" in result.events and self.known_key_location is None:
            self.known_key_location = pos

    def to_prompt_section(self) -> str:
        return (
            f"KNOWN WORLD STATE\n"
            f"- Key location:   {self.known_key_location or 'not yet discovered'}\n"
            f"- Door location:  {self.known_door_location or 'not yet discovered'}\n"
            f"- Explored cells: {len(self.known_cells)}\n"
            f"- Inventory:      {'key' if self.has_key else 'nothing'}\n"
        )
