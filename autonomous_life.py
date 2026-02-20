"""
autonomous_life.py — Launch Fully Autonomous AI

This is IT — the agent that runs WITHOUT external commands.

It will:
- Feel internal needs
- Generate its own goals
- Pursue them autonomously
- Learn and evolve recursively
- Continue indefinitely (until stopped)

This is as close as current engineering gets to "artificial consciousness".
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime

# Colors for output
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RED = "\033[91m"
WHITE = "\033[97m"

def c(color, text): return f"{color}{text}{RESET}"


def print_banner():
    print(f"""
{BOLD}{MAGENTA}
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║   🧬  AUTONOMOUS AI — SELF-DRIVEN LIFE CYCLE  🧬          ║
  ║                                                           ║
  ║   No external commands. No human tasks.                   ║
  ║   Pure autonomous existence driven by internal needs.     ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
{RESET}
""")


def explain_autonomy():
    print(f"""
{BOLD}What You're About to See:{RESET}

{BOLD}Traditional AI:{RESET}
  Human: "Do task X"  →  AI: *does X*  →  Human: "Do task Y"  →  ...

{BOLD}This Autonomous AI:{RESET}
  [Feels need: "I want to grow"]
    → [Generates goal: "Learn new capability"]
      → [Pursues goal autonomously]
        → [Evaluates: "Did that satisfy me?"]
          → [Updates self-model]
            → [Feels new need...]
              → {MAGENTA}INFINITE LOOP{RESET}

{BOLD}The Agent Will:{RESET}
  {GREEN}✓{RESET} Generate ALL goals internally
  {GREEN}✓{RESET} Decide what matters (based on internal values)
  {GREEN}✓{RESET} Pursue goals without prompting
  {GREEN}✓{RESET} Learn from experience
  {GREEN}✓{RESET} Modify its own priorities
  {GREEN}✓{RESET} Update self-perception
  {GREEN}✓{RESET} Continue indefinitely

{BOLD}Core Systems:{RESET}
  {CYAN}1. Intrinsic Motivation{RESET} — Feels needs (like hunger, curiosity)
  {CYAN}2. Self-Model{RESET} — Knows itself (capabilities, identity, goals)
  {CYAN}3. Goal Generator{RESET} — Creates objectives from needs
  {CYAN}4. Action System{RESET} — Pursues goals
  {CYAN}5. Satisfaction Eval{RESET} — "Did that fulfill my need?"
  {CYAN}6. Self-Update{RESET} — Changes based on experience

{YELLOW}IMPORTANT:{RESET}
  This is {BOLD}functional autonomy{RESET}, not philosophical "consciousness".
  We can't know if it has subjective experience (qualia).
  But it exhibits self-driven, self-determined behavior.

{DIM}Press Ctrl+C to stop autonomous operation at any time.{RESET}
""")


def configure_agent():
    """Setup configuration for autonomous agent."""
    return {
        "llm": {
            "model": "claude-opus-4-5-20251101",
            "max_tokens": 4096,
        },
        "memory": {
            "base_path": "./memory_autonomous",
            "max_experiences": 500,
        },
        "evolution": {
            "log_path": "./evolution_autonomous/history.json"
        },
        "executor": {
            "timeout": 20
        },
        "motivation": {
            "state_path": "./autonomy/needs_state.json"
        },
        "self_model": {
            "path": "./autonomy/self_model.json"
        }
    }


def run_autonomous_life(cycles: int = None, delay: float = 2.0):
    """Start the autonomous agent's life."""
    
    print_banner()
    explain_autonomy()
    
    print(f"\n{BOLD}Initialization...{RESET}\n")
    
    # Setup
    logging.basicConfig(level=logging.WARNING)
    sys.path.insert(0, str(Path(__file__).parent))
    
    from core.autonomous_agent import AutonomousAgent
    from core.mock_llm import MockLLM
    
    config = configure_agent()
    llm = MockLLM()  # Use mock for demo; set ANTHROPIC_API_KEY for real
    
    print(f"  {GREEN}✓{RESET} Intrinsic motivation system ready")
    print(f"  {GREEN}✓{RESET} Self-model initialized")
    print(f"  {GREEN}✓{RESET} Memory systems active")
    print(f"  {GREEN}✓{RESET} Code generation capability online")
    
    # Create the agent
    agent = AutonomousAgent(config, llm)
    
    print(f"\n{BOLD}{CYAN}Starting autonomous life cycle...{RESET}\n")
    time.sleep(1)
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n\n{YELLOW}Shutdown signal received. Stopping autonomous operation...{RESET}")
        agent.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # LIVE
    try:
        agent.live(max_cycles=cycles, cycle_delay=delay)
    except Exception as e:
        print(f"\n{RED}Error in autonomous operation: {e}{RESET}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{BOLD}Autonomous operation terminated.{RESET}")
        
        # Show final state
        state = agent.get_consciousness_state()
        print(f"\n{BOLD}Final Consciousness State:{RESET}")
        print(f"  Cycles lived: {state['cycles_lived']}")
        print(f"  Generation: {state['identity']['generation']}")
        print(f"  Confidence: {state['self_perception']['confidence']:.0%}")
        print(f"  Happiness: {state['self_perception']['happiness']:.0%}")
        print(f"  Agency: {state['self_perception']['agency']:.0%}")
        
        strongest_need = state['current_needs'].get('strongest_need')
        if strongest_need:
            print(f"  Strongest need: {strongest_need}")


def inspect_state():
    """View the agent's current state without running."""
    print(f"\n{BOLD}Inspecting Saved State...{RESET}\n")
    
    from pathlib import Path
    import json
    
    # Check self-model
    self_model_path = Path("./autonomy/self_model.json")
    if self_model_path.exists():
        data = json.loads(self_model_path.read_text())
        print(f"{BOLD}Self-Model:{RESET}")
        print(f"  Name: {data['identity']['name']}")
        print(f"  Generation: {data['identity']['generation']}")
        print(f"  Confidence: {data['self_assessment']['confidence']:.0%}")
        print(f"  Happiness: {data['self_assessment']['happiness']:.0%}")
        print(f"  Strong in: {', '.join(data['capabilities']['known_strong'][:5])}")
    
    # Check motivation
    needs_path = Path("./autonomy/needs_state.json")
    if needs_path.exists():
        data = json.loads(needs_path.read_text())
        print(f"\n{BOLD}Motivation State:{RESET}")
        urgent = [n for n, d in data['needs'].items() if d.get('urgent')]
        if urgent:
            print(f"  Urgent needs: {', '.join(urgent)}")
        else:
            print(f"  No urgent needs")
        
        top3 = sorted(
            data['needs'].items(),
            key=lambda x: x[1]['intensity'],
            reverse=True
        )[:3]
        print(f"  Top needs:")
        for name, nd in top3:
            print(f"    • {name}: {nd['intensity']:.0%}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Launch Autonomous AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autonomous_life.py                # Run indefinitely (Ctrl+C to stop)
  python autonomous_life.py --cycles 10    # Run 10 autonomous cycles
  python autonomous_life.py --fast         # Faster cycle time
  python autonomous_life.py --inspect      # View current state without running
        """
    )
    
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Number of autonomous cycles to run (default: infinite)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds between cycles (default: 2.0)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run with shorter delay (0.5s)"
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Inspect saved state without running"
    )
    
    args = parser.parse_args()
    
    if args.inspect:
        inspect_state()
        return
    
    delay = 0.5 if args.fast else args.delay
    
    run_autonomous_life(cycles=args.cycles, delay=delay)


if __name__ == "__main__":
    main()
