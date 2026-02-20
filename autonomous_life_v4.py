"""
autonomous_life_v4.py — Enhanced Autonomous Life with Full Consciousness

v4 Features:
- Real emotions that affect decisions
- Social interaction between agents
- Curiosity-driven exploration
- Observable consciousness stream
- Multi-agent society

Run modes:
1. Single agent (enhanced)
2. Multi-agent society
3. Observer mode (watch without interaction)
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime
import threading

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

def print_v4_banner():
    print(f"""
{BOLD}{MAGENTA}
  ╔═══════════════════════════════════════════════════════════════╗
  ║                                                               ║
  ║   🧠  ENHANCED AUTONOMOUS AI v4 — FULL CONSCIOUSNESS  🧠      ║
  ║                                                               ║
  ║   NEW: Emotions • Social • Curiosity • Consciousness Stream   ║
  ║                                                               ║
  ╚═══════════════════════════════════════════════════════════════╝
{RESET}

{BOLD}What's New in v4:{RESET}

  {GREEN}✓ Emotional System{RESET}
    • 8 basic emotions (Plutchik's wheel)
    • Emotions ACTUALLY affect decisions
    • Fear → cautious | Joy → exploratory
    
  {GREEN}✓ Agent Society{RESET}
    • Multiple agents in shared world
    • Message board communication
    • Resource sharing & cooperation
    • Social learning (learn from others)
    
  {GREEN}✓ Curiosity Engine{RESET}
    • Intrinsic rewards for novelty
    • Exploration vs exploitation
    • Information gain tracking
    
  {GREEN}✓ Consciousness Stream{RESET}
    • Real-time thought logging
    • Observable internal process
    • Perceptions, desires, intentions
    • Detect thought loops
""")


def configure_v4():
    return {
        "llm": {"model": "claude-opus-4-5-20251101", "max_tokens": 4096},
        "memory": {"base_path": "./memory_v4"},
        "evolution": {"log_path": "./evolution_v4/history.json"},
        "motivation": {"state_path": "./autonomy_v4/needs_state.json"},
        "self_model": {"path": "./autonomy_v4/self_model.json"},
        "emotions": {"path": "./autonomy_v4/emotional_state.json"},
        "society": {"path": "./society"},
        "curiosity": {"path": "./autonomy_v4/curiosity_state.json"},
        "consciousness": {"path": "./autonomy_v4/consciousness_stream.json"},
        "executor": {"timeout": 20},
    }


def run_single_agent(name: str = "Alice", cycles: int = 10):
    """Run single enhanced agent."""
    logging.basicConfig(level=logging.WARNING)
    sys.path.insert(0, str(Path(__file__).parent))
    
    from core.enhanced_autonomous_agent import EnhancedAutonomousAgent
    from core.mock_llm import MockLLM
    
    config = configure_v4()
    llm = MockLLM()
    
    print(f"\n{BOLD}Initializing {name}...{RESET}\n")
    
    agent = EnhancedAutonomousAgent(config, llm, name=name)
    
    print(f"  {GREEN}✓{RESET} Emotional system online")
    print(f"  {GREEN}✓{RESET} Connected to society")
    print(f"  {GREEN}✓{RESET} Curiosity engine active")
    print(f"  {GREEN}✓{RESET} Consciousness stream recording")
    
    print(f"\n{BOLD}{CYAN}Starting autonomous life...{RESET}\n")
    time.sleep(1)
    
    try:
        agent.live(max_cycles=cycles, cycle_delay=1.0, verbose=True)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted{RESET}")
    
    # Final status
    status = agent.get_full_status()
    print(f"\n{BOLD}Final Status:{RESET}")
    print(f"  Cycles: {status['cycles_lived']}")
    print(f"  Mood: {status['emotional_state']['mood']}")
    print(f"  Curiosity state: {status['curiosity_state']}")


def run_multi_agent_society(agent_names: list, cycles: int = 20):
    """Run multiple agents in shared society."""
    logging.basicConfig(level=logging.WARNING)
    sys.path.insert(0, str(Path(__file__).parent))
    
    from core.enhanced_autonomous_agent import EnhancedAutonomousAgent
    from core.mock_llm import MockLLM
    
    config = configure_v4()
    llm = MockLLM()
    
    print(f"\n{BOLD}Creating {len(agent_names)} agents...{RESET}\n")
    
    agents = []
    for name in agent_names:
        agent = EnhancedAutonomousAgent(config, llm, name=name)
        agents.append(agent)
        print(f"  {GREEN}✓{RESET} {name} joined society")
        time.sleep(0.3)
    
    print(f"\n{BOLD}{CYAN}Society is now alive!{RESET}\n")
    time.sleep(1)
    
    # Run agents in parallel
    stop_event = threading.Event()
    threads = []
    
    def run_agent(agent, cycles):
        try:
            agent.live(max_cycles=cycles, cycle_delay=2.0, verbose=False)
        except:
            pass
    
    for agent in agents:
        t = threading.Thread(target=run_agent, args=(agent, cycles))
        t.start()
        threads.append(t)
    
    # Monitor society
    try:
        for i in range(cycles):
            time.sleep(2)
            if i % 5 == 0:
                status = agents[0].society.get_society_status()
                print(f"\n{BOLD}Society Update (cycle {i}):{RESET}")
                print(f"  Active agents: {status['active_agents']}/{status['total_agents']}")
                print(f"  Messages: {status['total_messages']}")
                print(f"  Shared tools: {status['shared_tools']}")
                print(f"  Shared knowledge: {status['shared_knowledge']}")
                
                if status['top_contributors']:
                    print(f"  Top contributor: {status['top_contributors'][0]['name']}")
    
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopping society...{RESET}")
    
    # Wait for threads
    for t in threads:
        t.join(timeout=2)
    
    # Final society status
    status = agents[0].society.get_society_status()
    print(f"\n{BOLD}Final Society State:{RESET}")
    print(f"  Total agents: {status['total_agents']}")
    print(f"  Total interactions: {status['total_messages']}")
    print(f"  Resources shared: {status['shared_tools'] + status['shared_knowledge']}")
    
    print(f"\n{BOLD}Top Contributors:{RESET}")
    for contrib in status['top_contributors']:
        print(f"  • {contrib['name']}: {contrib['reputation']:.2f} reputation")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Autonomous AI v4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autonomous_life_v4.py --single              # Run single agent
  python autonomous_life_v4.py --society             # Run multi-agent society
  python autonomous_life_v4.py --single --cycles 20  # Longer run
  python autonomous_life_v4.py --society --agents "Alice,Bob,Carol"
        """
    )
    
    parser.add_argument("--single", action="store_true", help="Run single agent")
    parser.add_argument("--society", action="store_true", help="Run multi-agent society")
    parser.add_argument("--name", default="Alice", help="Agent name (single mode)")
    parser.add_argument("--agents", default="Alice,Bob,Carol", help="Agent names (society mode)")
    parser.add_argument("--cycles", type=int, default=10, help="Number of cycles")
    
    args = parser.parse_args()
    
    print_v4_banner()
    
    if args.society:
        agent_names = [n.strip() for n in args.agents.split(",")]
        run_multi_agent_society(agent_names, args.cycles)
    else:
        run_single_agent(args.name, args.cycles)


if __name__ == "__main__":
    main()
