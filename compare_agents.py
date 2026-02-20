"""
compare_agents.py — Side-by-Side: Tool Evolution vs. Policy Evolution

This demonstrates the fundamental difference in how agents learn.
"""

import sys
from pathlib import Path

# Colors
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"

def header(text):
    print(f"\n{BOLD}{CYAN}{'═'*70}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*70}{RESET}\n")

def main():
    header("Agent Learning Comparison")
    
    print(f"""
{BOLD}Scenario:{RESET} An agent encounters a CSV file with missing headers.

{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}
{BOLD}Tool-Only Agent (Basic EvoAgent):{RESET}
{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}

Attempt 1:
  {YELLOW}✗{RESET} Tries to parse CSV → Fails (no header detection)
  
Reflection:
  💭 "I need a CSV parser tool"
  
Evolution:
  🔨 Generates {GREEN}csv_parser{RESET} tool
  📝 Code: def csv_parser(file): ...
  ✓ Tests pass, tool integrated

Attempt 2:
  ✓ Uses csv_parser → Success!
  
{BOLD}What it learned:{RESET}
  • Added 1 tool: {GREEN}csv_parser{RESET}
  • Next time: can parse CSV files
  
{BOLD}Limitation:{RESET}
  • Faces JSON with missing keys → still fails
  • Faces XML with no schema → still fails
  • Each format needs a new tool

{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}
{BOLD}ERL Agent (Experiential Reinforcement Learning):{RESET}
{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}

Attempt 1:
  {YELLOW}✗{RESET} Tries to parse CSV → Fails (no header detection)
  
Deep Reflection (Kolb's Cycle):
  {MAGENTA}🧠 Reflective Observation:{RESET}
     "I assumed data had headers without validation"
     "I didn't inspect structure before processing"
  
  {MAGENTA}🧠 Abstract Conceptualization:{RESET}
     "General principle: With ANY structured data format,
      I must first inspect and validate structure before
      assuming what operations are valid"
  
  {MAGENTA}🧠 Active Experimentation:{RESET}
     "Revised approach: 
      1. Inspect first line
      2. Determine if header exists
      3. Adjust parsing strategy accordingly"

Attempt 2 (Reflection-Guided):
  ✓ Inspects structure → detects no headers
  ✓ Adjusts parsing → Success!
  
Policy Internalization:
  {BOLD}{MAGENTA}📋 New reasoning principle added to base policy:{RESET}
     {BOLD}"Before processing any structured data, validate format
      and structure constraints first"{RESET}
  
{BOLD}What it learned:{RESET}
  • Added 1 {BOLD}reasoning principle{RESET} (not just a tool)
  • This principle applies to: CSV, JSON, XML, YAML, Parquet,
    Protocol Buffers, and 50+ other formats
  • The agent now {BOLD}thinks differently{RESET} about data tasks

{BOLD}Advantage:{RESET}
  • Faces JSON with missing keys → {GREEN}✓{RESET} Validates structure first
  • Faces XML with no schema → {GREEN}✓{RESET} Inspects before processing
  • Faces new format (TOML) → {GREEN}✓{RESET} Applies same principle
  • No new tools needed

{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}
{BOLD}Comparison Table:{RESET}
{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}

                           │ Tool-Only Agent │ ERL Agent
═══════════════════════════╪═════════════════╪══════════════════
What is learned            │ 1 tool          │ 1 principle
Application scope          │ CSV only        │ All structured data
Transfer to new formats    │ No              │ Yes
Generalizes to similar     │ No              │ Yes
Requires new code per task │ Yes             │ No
Learns HOW to think        │ No              │ {BOLD}{MAGENTA}Yes{RESET}

{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}
{BOLD}Real-World Impact:{RESET}
{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}

The paper's Agent K (using ERL) achieved:
  • {BOLD}Top 2% on Kaggle{RESET} (1694 Elo-MMR, beyond median human)
  • {BOLD}9 gold, 8 silver, 12 bronze medals{RESET}
  • First AI to win prizes in data science competitions
  
Why? Because it learned to {BOLD}REASON about data science{RESET}, not just
accumulate data science tools.

After 100 competitions:
  • Tool-only agent: 100 tools, still struggles with novel tasks
  • ERL agent: 25 core reasoning principles, handles ANY task

{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}
{BOLD}Key Insight:{RESET}
{BOLD}═══════════════════════════════════════════════════════════════════════{RESET}

Tool evolution is {GREEN}narrow{RESET} learning:  "I can now do X"
Policy evolution is {BOLD}{MAGENTA}broad{RESET} learning: "I now understand how to approach X, Y, Z..."

This is the difference between:
  • {GREEN}Adding skills to a resume{RESET}  (tool-only)
  • {BOLD}{MAGENTA}Becoming a better thinker{RESET} (ERL)

The second path leads to {BOLD}general intelligence{RESET}.
""")

if __name__ == "__main__":
    main()
