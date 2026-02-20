"""
evolve_erl.py — Experiential Reinforcement Learning Demo

This demonstrates the key difference:
    Basic Agent: "I can't do X → create tool for X → now I can"
    ERL Agent:   "I failed at X → reflect deeply → revise approach → internalize pattern"

The ERL agent learns HOW TO THINK, not just what tools to use.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"

def c(color, text): return f"{color}{text}{RESET}"
def header(text): print(f"\n{BOLD}{CYAN}{'═'*70}{RESET}\n{BOLD}{CYAN}  {text}{RESET}\n{BOLD}{CYAN}{'═'*70}{RESET}")
def section(text): print(f"\n{BOLD}{WHITE}▸ {text}{RESET}")
def ok(text): print(f"  {GREEN}✓{RESET} {text}")
def info(text): print(f"  {CYAN}•{RESET} {text}")
def evolved(text): print(f"  {MAGENTA}🧬{RESET} {BOLD}{text}{RESET}")
def dim(text): print(f"  {DIM}{text}{RESET}")


# Tasks designed to trigger deep learning
ERL_TASKS = [
    ("Round 1: Data validation failure",
     "Process this data without checking: [1, 2, 'three', 4, None, 6]"),
    
    ("Round 2: Format assumption error",
     "Parse: name|age|city\\nAlice|30|NYC\\nBob|25|LA"),
    
    ("Round 3: Empty input handling",
     "Calculate average of: []"),
    
    ("Round 4: Type mismatch",
     "Sort these mixed items: [5, 'hello', 3.14, None, 'world', 1]"),
    
    ("Round 5: Compound task",
     "Read numbers from a file, filter negatives, compute statistics"),
    
    ("Round 6: Apply learned patterns",
     "Process user records: [{id:1,name:'A'},{id:2,name:'B'},{id:3}]"),
]


def run_erl_demo():
    """Main ERL demonstration."""
    
    header("ERL Agent — Learning How to Think")
    print(f"\n  {DIM}Mode: Experiential Reinforcement Learning{RESET}")
    print(f"  {DIM}Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    # Setup
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    sys.path.insert(0, str(Path(__file__).parent))
    from core.erl_agent import ERLAgent
    from core.mock_llm import MockLLM
    
    config = {
        "llm": {"model": "claude-opus-4-5-20251101", "max_tokens": 4096},
        "memory": {"base_path": "./memory_erl"},
        "evolution": {"log_path": "./evolution_erl/history.json"},
        "policy": {"path": "./memory_erl/policy.json"},
        "executor": {"timeout": 15},
    }
    
    llm = MockLLM()
    agent = ERLAgent(config, llm)
    
    # Initial state
    section("Initial State")
    s = agent.get_status()
    info(f"Generation: {s['generation']}")
    info(f"Principles learned: {s['principles_learned']}")
    info(f"Tools: {s['tools_available']}")
    
    # Show bootstrap principles
    section("Bootstrap Reasoning Principles")
    for i, p in enumerate(agent.policy.principles[:4], 1):
        dim(f"{i}. {p['pattern']}")
    
    # Run tasks
    results = []
    for i, (round_name, task) in enumerate(ERL_TASKS):
        print(f"\n{'─'*70}")
        section(round_name)
        dim(f"Task: {task[:75]}{'...' if len(task) > 75 else ''}")
        
        t0 = time.time()
        result = agent.run(task, verbose=True)
        elapsed = time.time() - t0
        
        if result["success"]:
            ok(f"Completed ({elapsed:.1f}s)")
        else:
            print(f"  {YELLOW}⚠{RESET} Partial success ({elapsed:.1f}s)")
        
        # Show learning
        if result.get("learned_pattern"):
            evolved(f"Learned: {result['learned_pattern'][:70]}")
        
        if result.get("policy_updated"):
            evolved(f"Policy updated! Generation {result['generation']}")
        
        results.append({
            "round": round_name,
            "success": result["success"],
            "erl_applied": result.get("erl_applied", False),
            "policy_updated": result.get("policy_updated", False),
        })
        
        time.sleep(0.2)
    
    # Final summary
    header("ERL Session Summary")
    
    final = agent.get_status()
    
    section("Performance")
    successes = sum(1 for r in results if r["success"])
    erl_cycles = sum(1 for r in results if r["erl_applied"])
    policy_updates = sum(1 for r in results if r["policy_updated"])
    
    ok(f"Tasks completed:     {successes}/{len(results)}")
    ok(f"ERL cycles used:     {erl_cycles}")
    ok(f"Policy updates:      {policy_updates}")
    ok(f"Final generation:    {final['generation']}")
    ok(f"Principles learned:  {final['principles_learned']}")
    
    section("Learned Reasoning Principles")
    policy_summary = agent.policy.get_summary()
    most_used = policy_summary.get("most_used", [])
    
    if most_used:
        for i, p in enumerate(most_used, 1):
            pattern = p.get("pattern", "")
            apps = p.get("applications", 0)
            rate = p.get("success_rate", 0)
            print(f"  {MAGENTA}{i}.{RESET} {pattern[:60]}")
            dim(f"     Applied: {apps}× | Success rate: {rate:.0%}")
    else:
        dim("No frequently used principles yet")
    
    section("All Principles in Policy Store")
    for i, p in enumerate(agent.policy.principles[:10], 1):
        print(f"  {CYAN}•{RESET} {p['pattern'][:65]}")
    
    # Key difference explanation
    header("Why This Matters: ERL vs. Tool-Only Evolution")
    
    print(f"""
{BOLD}Tool-Only Agent:{RESET}
  • Faces CSV task → generates csv_parser tool → succeeds
  • Next time: uses csv_parser
  • Learning: {CYAN}added a capability{RESET}

{BOLD}ERL Agent:{RESET}
  • Faces CSV task → {YELLOW}fails to validate format first{RESET}
  • Reflects: {MAGENTA}"I should always check data structure before processing"{RESET}
  • Second attempt: validates format, {GREEN}then{RESET} processes
  • Internalizes: {BOLD}"Before processing structured data, validate format"{RESET}
  • Next time: {CYAN}applies this reasoning to ALL data tasks{RESET} (JSON, XML, etc.)
  • Learning: {BOLD}{MAGENTA}changed how it thinks{RESET}

{BOLD}Result:{RESET}
  Tool-only agent: learns {CYAN}1 capability{RESET} (CSV parsing)
  ERL agent:       learns {BOLD}{MAGENTA}1 principle{RESET} that applies to {CYAN}100+ scenarios{RESET}

This is why Agent K achieved {BOLD}top 2% on Kaggle{RESET} — it learned to REASON about
data science, not just accumulate tools.
""")
    
    print(f"\n  {DIM}Full policy saved: {config['policy']['path']}{RESET}")
    print(f"  {DIM}Evolution log:     {config['evolution']['log_path']}{RESET}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ERL Agent Demo")
    parser.add_argument("--compare", action="store_true", help="Run comparison with basic agent")
    args = parser.parse_args()
    
    if args.compare:
        print(f"{YELLOW}TODO: Implement side-by-side comparison{RESET}")
        print("Run basic agent, then ERL agent, show the difference")
    else:
        run_erl_demo()
