"""
EvoAgent — Entry Point

Usage:
    python main.py                          # interactive mode
    python main.py --task "do something"   # single task
    python main.py --task "..." --verbose  # see the thinking
    python main.py --report                # evolution history
    python main.py --status                # agent status
"""

import os
import sys
import json
import logging
import argparse

def setup(level: str = "WARNING"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

def load_config() -> dict:
    import yaml
    for name in ["config.yaml", "config.yml"]:
        if os.path.exists(name):
            with open(name, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    # Minimal default config
    return {
        "llm": {
            "provider": "anthropic",
            "model": "claude-opus-4-5-20251101",
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "max_tokens": 4096,
        },
        "memory": {"base_path": "./memory"},
        "evolution": {"log_path": "./evolution/history.json"},
        "executor": {"timeout": 30},
    }

def make_llm(config: dict):
    key = config.get("llm", {}).get("api_key") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("⚠  No API key found. Running in demo mode (no real LLM calls).")
        print("   Set ANTHROPIC_API_KEY or add it to config.yaml\n")
        return None
    provider = config.get("llm", {}).get("provider", "anthropic")
    try:
        if provider == "anthropic":
            import anthropic
            return anthropic.Anthropic(api_key=key)
        elif provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=key)
    except ImportError as e:
        print(f"⚠  Import error: {e}")
        return None

BANNER = """
  ███████╗██╗   ██╗ ██████╗  █████╗  ██████╗ ███████╗███╗   ██╗████████╗
  ██╔════╝██║   ██║██╔═══██╗██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
  █████╗  ██║   ██║██║   ██║███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
  ██╔══╝  ╚██╗ ██╔╝██║   ██║██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
  ███████╗ ╚████╔╝ ╚██████╔╝██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
  ╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝  
  self-evolving AI agent — github.com/your-username/evoagent
"""

def main():
    parser = argparse.ArgumentParser(description="EvoAgent — self-evolving AI agent")
    parser.add_argument("--task", "-t", help="Run a single task and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show agent thinking steps")
    parser.add_argument("--report", action="store_true", help="Print evolution history and exit")
    parser.add_argument("--status", action="store_true", help="Print agent status and exit")
    parser.add_argument("--log", default="WARNING", help="Log level (DEBUG/INFO/WARNING)")
    args = parser.parse_args()

    setup(args.log)
    print(BANNER)

    config = load_config()
    llm = make_llm(config)

    from core.agent import EvoAgent
    agent = EvoAgent(config, llm)

    print(f"  Generation: {agent.state.generation}  |  "
          f"Tools: {len(agent.memory.all_tools())}  |  "
          f"Tasks done: {agent.state.done}\n")

    if args.report:
        print(agent.evo.report())
        return

    if args.status:
        print(json.dumps(agent.status(), indent=2))
        return

    if args.task:
        _run_task(agent, args.task, args.verbose)
        return

    # Interactive loop
    print("  Type a task and press Enter. Commands: status | report | quit\n")
    while True:
        try:
            user = input("  task> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye.")
            break

        if not user:
            continue
        if user.lower() in ("quit", "exit", "q"):
            print("  Goodbye.")
            break
        elif user.lower() == "status":
            print(json.dumps(agent.status(), indent=2))
        elif user.lower() == "report":
            print(agent.evo.report())
        else:
            _run_task(agent, user, args.verbose)


def _run_task(agent, task: str, verbose: bool):
    print(f"\n  Running: {task}\n")
    result = agent.run(task, verbose=verbose)
    icon = "✓" if result["success"] else "✗"
    print(f"\n  {icon} {result['output']}")
    if result.get("evolved"):
        print(f"  🧬 Evolved → generation {result['generation']}")
    if result.get("learned"):
        for item in result["learned"]:
            print(f"  📚 {item}")
    print()


if __name__ == "__main__":
    main()
