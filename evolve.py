"""
evolve.py — START THE SELF-EVOLUTION

This script runs EvoAgent through a series of tasks, watches it identify
capability gaps, write new tools, test them, and integrate them.

Usage:
    python evolve.py                    # full demo, no API key needed
    python evolve.py --live             # use real LLM (needs API key)
    python evolve.py --rounds 10        # run more evolution rounds
    python evolve.py --task "your task" # evolve on a specific task
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# ── Pretty output ────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"

def c(color, text): return f"{color}{text}{RESET}"
def header(text):   print(f"\n{BOLD}{CYAN}{'═'*62}{RESET}\n{BOLD}{CYAN}  {text}{RESET}\n{BOLD}{CYAN}{'═'*62}{RESET}")
def section(text):  print(f"\n{BOLD}{WHITE}  ▸ {text}{RESET}")
def ok(text):       print(f"  {GREEN}✓{RESET} {text}")
def warn(text):     print(f"  {YELLOW}⚠{RESET} {text}")
def info(text):     print(f"  {CYAN}·{RESET} {text}")
def evolved(text):  print(f"  {MAGENTA}🧬{RESET} {BOLD}{MAGENTA}{text}{RESET}")
def fail(text):     print(f"  {RED}✗{RESET} {text}")
def dim(text):      print(f"  {DIM}{text}{RESET}")

def ticker(msg, delay=0.03):
    """Print text character by character for effect."""
    sys.stdout.write("  ")
    for ch in msg:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ── Tasks that will drive evolution ─────────────────────

EVOLUTION_TASKS = [
    # These tasks are chosen to trigger tool creation
    ("Round 1: Basic capability check",
     "Analyze this text and count words: 'The quick brown fox jumps over the lazy dog'"),

    ("Round 2: CSV parsing — new capability needed",
     "Parse this CSV data and summarize: name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,Chicago"),

    ("Round 3: Statistical computation",
     "Calculate statistics for these numbers: 14, 28, 7, 42, 21, 35, 63, 56"),

    ("Round 4: List operations",
     "Sort this list in descending order: [42, 7, 19, 3, 88, 15, 64, 31]"),

    ("Round 5: File operations",
     "Read the file at ./memory/experiences.json and tell me how many experiences are stored"),

    ("Round 6: Compound task using evolved tools",
     "Sort these scores and compute their statistics: 95, 67, 88, 73, 91, 55, 82, 78"),

    ("Round 7: HTTP data fetching",
     "Fetch data from https://httpbin.org/json and extract the slideshow title"),

    ("Round 8: Self-reflection on growth",
     "Analyze your own evolution history and summarize what new capabilities you have gained"),
]


def run_evolution(rounds: int, use_real_llm: bool, single_task: str = None):
    """Main evolution loop."""

    header("EvoAgent — Self-Evolution Session")
    print(f"\n  {DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"  {DIM}Mode:    {'🌐 Live LLM' if use_real_llm else '🔧 Demo (MockLLM)'}{RESET}")
    print(f"  {DIM}Rounds:  {rounds}{RESET}")

    # ── Setup ────────────────────────────────────────────
    logging.basicConfig(level=logging.WARNING)

    sys.path.insert(0, str(Path(__file__).parent))
    from core.agent import EvoAgent
    from core.mock_llm import MockLLM

    config = {
        "llm": {
            "model": "claude-opus-4-5-20251101",
            "max_tokens": 4096,
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        },
        "memory":    {"base_path": "./memory"},
        "evolution": {"log_path": "./evolution/history.json"},
        "executor":  {"timeout": 15},
    }

    # Choose LLM
    if use_real_llm:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            warn("ANTHROPIC_API_KEY not set — falling back to MockLLM")
            llm = MockLLM()
        else:
            import anthropic
            llm = anthropic.Anthropic(api_key=key)
            ok("Connected to Anthropic API")
    else:
        llm = MockLLM()
        ok("MockLLM ready (full offline demo)")

    agent = EvoAgent(config, llm)

    # ── Show initial state ───────────────────────────────
    section("Initial State")
    s = agent.status()
    info(f"Generation:  {s['generation']}")
    info(f"Tools ready: {s['tools_available']} — {s['tool_names'] or ['(none yet)']}")
    info(f"Experience:  {s['tasks_done']} tasks completed")

    # ── Run tasks ────────────────────────────────────────
    tasks = [(single_task, single_task)] * rounds if single_task else EVOLUTION_TASKS[:rounds]
    results_log = []

    for i, task_entry in enumerate(tasks):
        if isinstance(task_entry, tuple):
            round_name, task = task_entry
        else:
            round_name, task = f"Round {i+1}", task_entry

        print(f"\n{'─'*62}")
        section(round_name)
        dim(f"Task: {task[:80]}{'...' if len(task) > 80 else ''}")

        t0 = time.time()
        result = agent.run(task, verbose=False)
        elapsed = time.time() - t0

        if result["success"]:
            ok(f"Completed in {elapsed:.1f}s")
        else:
            fail(f"Failed after {elapsed:.1f}s")

        # Show output
        output = result.get("output", "")
        if output:
            print(f"\n  {DIM}Output:{RESET}")
            for line in str(output)[:300].split("\n"):
                dim(f"    {line}")

        # Show learning
        if result.get("learned"):
            print(f"\n  {CYAN}Learned:{RESET}")
            for item in result["learned"]:
                info(item)

        # Show evolution
        if result.get("evolved"):
            evolved(f"EVOLVED → Generation {result['generation']}!")
            # Show what was gained
            new_tools = [t for t in agent.memory.all_tools()
                        if t.get("source") == "generated"]
            if new_tools:
                latest = new_tools[-1]
                evolved(f"New tool: '{latest['name']}' — {latest.get('description','')[:60]}")

        results_log.append({
            "round": round_name,
            "task": task[:80],
            "success": result["success"],
            "evolved": result.get("evolved", False),
            "generation": result["generation"],
            "elapsed": round(elapsed, 2),
        })

        time.sleep(0.3)  # brief pause between rounds

    # ── Final status ─────────────────────────────────────
    header("Evolution Complete")

    final = agent.status()
    total_rounds = len(tasks)
    successes = sum(1 for r in results_log if r["success"])
    evolutions = sum(1 for r in results_log if r["evolved"])

    section("Session Summary")
    ok(f"Tasks completed:   {successes}/{total_rounds}")
    ok(f"Evolutions:        {evolutions}")
    ok(f"Final generation:  {final['generation']}")
    ok(f"Tools in library:  {final['tools_available']}")

    section("Tool Library")
    for tool in agent.memory.all_tools():
        source_tag = f"{DIM}[{tool.get('source','?')}]{RESET}"
        print(f"  {GREEN}▸{RESET} {BOLD}{tool['name']:<25}{RESET} {source_tag}  {DIM}{tool.get('description','')[:45]}{RESET}")

    section("Evolution Timeline")
    timeline = agent.evo.timeline()
    if timeline:
        for entry in timeline:
            print(f"  {MAGENTA}Gen {entry['gen']:>3}{RESET}  {DIM}{entry['ts']}{RESET}  "
                  f"{BOLD}{entry['tool']:<25}{RESET}  {DIM}{entry['trigger'][:35]}{RESET}")
    else:
        dim("No evolutions recorded in this session")

    # ── Save run report ──────────────────────────────────
    report_path = Path("./evolution/run_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "session_id": agent.state.session,
        "timestamp": datetime.now().isoformat(),
        "mode": "live" if use_real_llm else "demo",
        "rounds": results_log,
        "final_status": final,
        "evolution_timeline": timeline,
    }
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n  {DIM}Full report saved: {report_path}{RESET}")
    print(f"\n  {BOLD}Run {c(CYAN,'python evolve.py --report')} to see evolution history anytime.{RESET}\n")

    return report


def show_report():
    """Display the last run report."""
    p = Path("./evolution/history.json")
    if not p.exists():
        print("No evolution history found. Run: python evolve.py")
        return
    sys.path.insert(0, str(Path(__file__).parent))
    from core.evolution import EvolutionLog
    evo = EvolutionLog({"log_path": str(p)})
    print(evo.report())


def main():
    parser = argparse.ArgumentParser(
        description="EvoAgent — Self-Evolution System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evolve.py                     # run full demo offline
  python evolve.py --live              # use real Anthropic API
  python evolve.py --rounds 4          # run only 4 evolution rounds
  python evolve.py --task "sort [5,3,1,4,2] and compute stats"
  python evolve.py --report            # show evolution history
        """
    )
    parser.add_argument("--live",    action="store_true", help="Use real LLM (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--rounds",  type=int, default=8, help="Number of evolution rounds (default: 8)")
    parser.add_argument("--task",    type=str, default="", help="Run a single specific task")
    parser.add_argument("--report",  action="store_true", help="Show evolution report and exit")
    args = parser.parse_args()

    if args.report:
        show_report()
        return

    run_evolution(
        rounds=args.rounds,
        use_real_llm=args.live,
        single_task=args.task or None,
    )


if __name__ == "__main__":
    main()
