import json, datetime, pathlib
from typing import Any
from world.grid        import Grid
from agent.observer    import build_observation
from agent.world_model import WorldModel
from agent.actions     import validate, ActionResult

SCRIPTED = [
    "move_right","move_right","move_right","move_right",
    "move_right","move_right","move_right","move_right",
    "move_down","move_down","move_down","move_down",
    "move_left","move_left","move_left","move_left",
    "pick_up",
    "move_down","move_down",
    "move_left",        # walks into door → unlocks automatically
    "move_right",
    "move_down","move_down",
    "move_right","move_right","move_right",
]

def run(grid: Grid, llm=None, max_steps=50, mode="llm", render=False) -> dict[str, Any]:
    agent       = grid.spawn_agent()
    memory      = WorldModel()
    log         = []
    metrics     = {"success":False,"steps":0,"api_calls":0,
                   "invalid_actions":0,"cells_explored":0}
    last_result = None
    script_idx  = 0

    renderer = None
    if render:
        from world.renderer import Renderer
        renderer = Renderer(grid.rows, grid.cols)

    for step in range(max_steps):
        obs = build_observation(grid, agent, memory, last_result, max_steps, step)

        if mode == "scripted":
            action_name = SCRIPTED[script_idx] if script_idx < len(SCRIPTED) else "wait"
            raw         = json.dumps({"action": action_name, "reasoning": "scripted"})
            error       = None
            script_idx += 1
        else:
            raw    = llm.call(obs)
            metrics["api_calls"] += 1
            action_name, error = validate(raw, grid, agent)

            # Debugging: when validation fails or when waiting around critical steps,
            # print the full observation and raw LLM output to help diagnose stalls.
            if error or (action_name == "wait" and 4 <= step <= 7):
                print("=" * 40)
                print("OBSERVATION:")
                print(obs)
                print("RAW_LLM_OUTPUT:")
                print(raw)
                print("=" * 40)

        if error:
            metrics["invalid_actions"] += 1

        last_result = grid.execute(agent, action_name)
        memory.update_from_result(last_result, agent.pos)
        metrics["cells_explored"] = len(memory.known_cells)

        log.append({
            "step":        step,
            "observation": obs,
            "raw_llm":     raw,
            "action":      action_name,
            "fallback":    error,
            "events":      last_result.events,
            "outcome":     last_result.outcome,
            "position":    list(agent.pos),
        })

        print(f"Step {step+1:02d} | {action_name:<12} | {last_result.outcome} "
              f"| events: {last_result.events or '—'} | pos: {agent.pos}")

        if renderer:
            renderer.draw(grid, agent, step + 1, action_name,
                          last_result.outcome, last_result.events)

        if grid.is_goal_reached(agent):
            metrics["success"] = True
            metrics["steps"]   = step + 1
            if renderer:
                renderer.draw(grid, agent, step + 1, action_name,
                              last_result.outcome, last_result.events)
                renderer.pause(2000)
            break

    if renderer:
        renderer.close()

    result: dict[str, Any] = {**metrics, "mode": mode, "log": log}
    _save(result, mode)
    return result

def _save(result: dict[str, Any], mode: str):
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(f"logs/{mode}_{ts}.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2))
    print(f"\nLog saved → {path}")
