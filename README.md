# LLM Agent in a Virtual World

A Claude-powered agent that navigates a 2D grid maze: find the key, unlock the door, reach the goal.

![demo](llm-agent-world/demo/demo.gif)

---

## What it does

The agent runs a perception → reasoning → action loop at every step:

1. **Observer** builds a text observation from the local grid view, known world state, and a navigation hint.
2. **LLM** (Claude Haiku) reads the observation and responds with a JSON action.
3. **Harness** executes the action on the grid and feeds the result back.

Two modes are available: `scripted` (hard-coded optimal path, no API calls) and `llm` (live Claude inference).

---

## Setup

### 1. Install uv

[uv](https://docs.astral.sh/uv/) is the package manager used by this project.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Enter the project directory

```bash
cd llm-agent-world
```

### 3. Install dependencies

```bash
uv sync
```

This creates a virtual environment and installs all packages listed in `pyproject.toml`, including `anthropic` and `pygame-ce`.

### 4. Set your API key

An **Anthropic API key** is required to run the LLM mode. Create a `.env` file inside `llm-agent-world/` and add your key — never commit this file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

> `.env` is already in `.gitignore`. Do not hardcode credentials anywhere in the source.

---

## Running

All commands must be run from inside `llm-agent-world/`.

### Scripted agent (no API key needed)

```bash
uv run python run.py --mode scripted
```

### LLM agent (requires API key)

```bash
uv run python run.py --mode llm
```

### With Pygame visualisation

Add `--render` to either mode to open a graphical window:

```bash
uv run python run.py --mode scripted --render
uv run python run.py --mode llm --render
```

### Example output

```
Step 01 | move_right   | success | events: —                | pos: (2, 1)
...
Step 19 | pick_up      | success | events: ['picked_up_key'] | pos: (5, 5)
Step 24 | move_left    | success | events: ['door_unlocked'] | pos: (4, 7)
Step 36 | move_right   | success | events: ['goal_visible']  | pos: (8, 9)

SUCCESS — 36 steps | 121 cells explored | 0 invalid actions
```

Each run saves a full JSON log to `logs/` with the observation, raw LLM output, action, outcome, and position at every step.

---

## Design notes

### Agent harness

The harness is a thin loop: build observation → call LLM → validate → execute → log. The LLM is never given direct access to the grid object; it only sees a text observation and returns a JSON string. This keeps the interface clean and the LLM replaceable — swapping Claude for any other model requires changing one file (`llm/client.py`).

### Observation representation

Each observation contains four things the agent needs to act:

- **Local view** — a 9×9 ASCII window centred on the agent, with `?` for unseen cells. Partial observability is made explicit rather than hidden.
- **World model** — a persistent `WorldModel` accumulates key, door, and goal positions across steps and injects them as structured text (`Key location: (5,5)`). The LLM is stateless per call; the world model is the agent's memory.
- **Inventory and task status** — current item held and steps remaining, so the LLM always knows where it is in the task sequence.
- **Navigation hint** — a one-line directive derived from position and task state (e.g. *"Door is unlocked. Goal G is at (8,9). Move onto that cell to win."*). This encodes maze structure the LLM cannot reliably infer from a local view alone, and was the key fix for eliminating oscillation loops.

### Action space

Six actions: four directions, `pick_up`, and `use_item`. `wait` is included but strongly discouraged in the system prompt. A small, named action space reduces the LLM's decision surface and makes invalid-action rate a meaningful quality signal.

### What worked

Separating world-model updates from grid state kept the LLM's memory consistent with ground-truth events (key picked up, door unlocked) rather than inferred from the visual. State-aware navigation hints cut the LLM's reliance on multi-step spatial reasoning, which models handle poorly without chain-of-thought. Using a scripted agent as a baseline made it fast to isolate whether a failure was an environment bug or a reasoning failure.

### What didn't work at first

A plain "explore and find the goal" prompt produced `wait` loops once the agent hit a wall it couldn't see past. The fix was not a better prompt — it was injecting the explicit next step directly into the observation. The LLM is good at following clear instructions; it is poor at maintaining spatial state across turns without structured help.

---

## Project layout

```
llm-agent-world/
  run.py              entry point, map definition, CLI flags
  agent/
    harness.py        main loop: observe → act → log
    observer.py       builds the text observation sent to the LLM
    world_model.py    tracks key/door/goal locations and inventory across steps
    actions.py        action names, descriptions, and validation
  llm/
    client.py         Anthropic API wrapper (reads ANTHROPIC_API_KEY from env)
  world/
    grid.py           grid state, movement, events (found_key, door_unlocked, …)
    renderer.py       Pygame visualisation
  logs/               per-run JSON logs saved automatically
  demo/
    demo.gif          screen recording of a successful LLM run
```

---

## Map legend

| Symbol | Meaning |
|--------|---------|
| `#`    | Wall |
| `.`    | Empty cell |
| `?`    | Unexplored (partial observability) |
| `K`    | Key |
| `D`    | Door (requires key to unlock) |
| `G`    | Goal |
| `A`    | Agent start position |
