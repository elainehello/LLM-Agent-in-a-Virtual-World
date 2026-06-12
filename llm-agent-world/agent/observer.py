from agent.actions import ACTION_DESCRIPTIONS

def build_observation(world, agent, memory, last_result, max_steps, step) -> str:
    local_raw  = world.get_local_view(agent.pos, radius=4)
    local_list = world.get_local_view_list(agent.pos, radius=4)

    memory.update_from_observation(local_list)

    x, y = agent.pos

    # Give the agent an explicit navigation hint based on its current position and task state
    if y == 1:
        if x < 9:
            nav_hint = f"You are on row 1 at x={x}. Row 2 is a wall except at x=1 and x=9. Move RIGHT to reach x=9 (the south corridor), then move down."
        else:
            nav_hint = "You are at x=9. Move DOWN — this is the open south corridor."
    elif memory.door_unlocked:
        if memory.known_goal_location:
            gx, gy = memory.known_goal_location
            if y < gy:
                if x in (1, 5, 9):
                    nav_hint = (
                        f"Door is unlocked. Goal G is at ({gx},{gy}). "
                        f"You are at a south corridor (x={x}). Move DOWN now."
                    )
                else:
                    nav_hint = (
                        f"Door is unlocked. Goal G is at ({gx},{gy}). "
                        f"Rows below have walls — south passages only at x=1, x=5, x=9. "
                        f"Move LEFT to reach x=5, then go DOWN."
                    )
            else:
                nav_hint = f"Door is unlocked. Goal G is at ({gx},{gy}). Move onto that cell to win."
        else:
            nav_hint = "Door is unlocked. Explore to find the goal G — check your local view."
    elif not agent.has_key:
        if memory.known_key_location:
            kx, ky = memory.known_key_location
            nav_hint = f"Key is at ({kx},{ky}). Navigate there and use pick_up."
        else:
            nav_hint = "Explore south to find the key K."
    elif memory.known_door_location:
        dx, dy = memory.known_door_location
        nav_hint = f"You have the key. Door is at ({dx},{dy}). Walk INTO it (move onto that cell) to unlock."
    else:
        nav_hint = "You have the key. Find the door D and walk into it to unlock."

    sections = [
        f"LOCAL VIEW (? = unseen)\n{local_raw}",
        f"CURRENT STATE\nPosition: ({x}, {y})\nInventory: {'key' if agent.has_key else 'nothing'}",
        memory.to_prompt_section(),
        f"NAVIGATION HINT\n{nav_hint}",
        f"MISSION STATUS\nSteps remaining: {max_steps - step}",
    ]

    if last_result:
        sections.insert(2, last_result.to_prompt_section())

    actions_list = "\n".join(f"  {k}: {v}" for k, v in ACTION_DESCRIPTIONS.items())
    sections.append(
        f"AVAILABLE ACTIONS\n{actions_list}\n\n"
        f'Respond ONLY with raw JSON: {{"action":"<action>","reasoning":"<one short sentence>"}}'
    )

    return "\n\n".join(sections)
