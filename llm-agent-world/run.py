# run.py
import argparse
from dotenv import load_dotenv
from world.grid    import Grid
from agent.harness import run

load_dotenv()

MEDIUM = [
    "###########",
    "#A . . . .#",
    "#. # # # .#",
    "#. . K . .#",
    "#. # # # .#",
    "#. . . D .#",
    "#. # # # .#",
    "#. . . . G#",
    "###########",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["llm","scripted"], default="scripted")
    args   = parser.parse_args()

    grid = Grid(MEDIUM)

    if args.mode == "llm":
        from llm.client import LLMClient
        llm = LLMClient()
    else:
        llm = None

    result = run(grid, llm=llm, max_steps=50, mode=args.mode)
    print(f"\n{'SUCCESS' if result['success'] else 'FAILED'} — "
          f"{result['steps']} steps | "
          f"{result['cells_explored']} cells explored | "
          f"{result['invalid_actions']} invalid actions")
