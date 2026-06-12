from typing import Any
from dataclasses import dataclass

UNSEEN = "?"

@dataclass
class Agent:
    pos: tuple[int, int]
    has_key: bool = False

class Grid:
    def __init__(self, layout: list[str]):
        self.cells = [list(row) for row in layout]
        self.rows  = len(self.cells)
        self.cols  = len(self.cells[0])

    def get_local_view(self, pos: tuple, radius: int = 3) -> str:
        rows = []
        for dy in range(-radius, radius + 1):
            row = []
            for dx in range(-radius, radius + 1):
                x, y = pos[0] + dx, pos[1] + dy
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    row.append(self.cells[y][x])
                else:
                    row.append(UNSEEN)
            rows.append(" ".join(row))
        return "\n".join(rows)

    def get_local_view_list(self, pos: tuple, radius: int = 3) -> list[tuple]:
        result = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = pos[0] + dx, pos[1] + dy
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    result.append(((x, y), self.cells[y][x]))
        return result

    def is_wall(self, pos: tuple) -> bool:
        x, y = pos
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return True
        return self.cells[y][x] == "#"

    def cell_at(self, pos: tuple) -> str:
        x, y = pos
        return self.cells[y][x]

    def set_cell(self, pos: tuple, char: str):
        x, y = pos
        self.cells[y][x] = char

    def is_goal_reached(self, agent: Agent) -> bool:
        return self.cell_at(agent.pos) == "G"

    def spawn_agent(self) -> Agent:
        for y, row in enumerate(self.cells):
            for x, ch in enumerate(row):
                if ch == "A":
                    self.set_cell((x, y), ".")
                    return Agent(pos=(x, y))
        raise ValueError("No agent 'A' found in layout")

    def execute(self, agent: Agent, action: str) -> "ActionResult":
        from agent.actions import ActionResult

        if action == "wait":
            return ActionResult(action=action, outcome="success", events=[])

        if action.startswith("move_"):
            direction = action.split("_")[1]
            dx, dy = {"up":(0,-1),"down":(0,1),"left":(-1,0),"right":(1,0)}[direction]
            nx, ny = agent.pos[0] + dx, agent.pos[1] + dy
            next_pos = (nx, ny)

            if self.is_wall(next_pos):
                return ActionResult(action=action, outcome="failed",
                                    events=["wall_collision"])

            cell = self.cell_at(next_pos)
            if cell == "D":
                if agent.has_key:
                    self.set_cell(next_pos, ".")
                    agent.pos = next_pos
                    return ActionResult(action=action, outcome="success",
                                        events=["door_unlocked"])
                else:
                    return ActionResult(action=action, outcome="failed",
                                        events=["door_locked_no_key"])

            agent.pos = next_pos
            events = []
            if cell == "K":
                events.append("found_key")
            if cell == "G":
                events.append("goal_visible")
            return ActionResult(action=action, outcome="success", events=events)

        if action == "pick_up":
            cell = self.cell_at(agent.pos)
            if cell == "K":
                agent.has_key = True
                self.set_cell(agent.pos, ".")
                return ActionResult(action=action, outcome="success",
                                    events=["picked_up_key"])
            return ActionResult(action=action, outcome="failed",
                                events=["nothing_to_pick_up"])

        if action == "use_item":
            if not agent.has_key:
                return ActionResult(action=action, outcome="failed",
                                    events=["no_item_in_inventory"])
            for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                adj = (agent.pos[0]+dx, agent.pos[1]+dy)
                if 0 <= adj[0] < self.cols and 0 <= adj[1] < self.rows:
                    if self.cell_at(adj) == "D":
                        self.set_cell(adj, ".")
                        agent.has_key = False
                        return ActionResult(action=action, outcome="success",
                                            events=["door_unlocked"])
            return ActionResult(action=action, outcome="failed",
                                events=["no_door_adjacent"])

        return ActionResult(action=action, outcome="failed", events=["unknown_action"])