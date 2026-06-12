from agent.actions import ACTION_DESCRIPTIONS

def build_observation(world, agent, memory, last_result, max_steps, step) -> str:
    local_raw  = world.get_local_view(agent.pos, radius=3)
    local_list = world.get_local_view_list(agent.pos, radius=3)

    memory.update_from_observation(local_list)

    sections = [
        f"LOCAL VIEW (? = unseen)\n{local_raw}",
        f"CURRENT STATE\nPosition: {agent.pos}\nInventory: {'key' if agent.has_key else 'nothing'}",
        memory.to_prompt_section(),
        f"MISSION STATUS\nSteps remaining: {max_steps - step}",
    ]
    if last_result:
        sections.insert(2, last_result.to_prompt_section())

    actions_list = "\n".join(f"  {k}: {v}" for k, v in ACTION_DESCRIPTIONS.items())
    sections.append(
        f"AVAILABLE ACTIONS\n{actions_list}\n\n"
        f'Respond ONLY with valid JSON: {{"action":"<action>","reasoning":"<why>"}}'
    )

    return "\n\n".join(sections)
