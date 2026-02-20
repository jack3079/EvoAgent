# 🧬 EvoAgent

> **An open-source AI agent that writes, tests, and integrates its own code — evolving autonomously with every task.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What Is This?

EvoAgent is an agent that **improves itself**. Every time it fails a task or identifies a gap in its abilities, it:

1. Writes new Python code to address the gap
2. Tests that code immediately
3. Integrates passing code into its own tool library
4. Uses those new tools on future tasks

No approval steps. No human gates. Just a loop that gets smarter.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        EvoAgent                          │
│                                                         │
│   Task ──► Perceive ──► Plan ──► Act ──► Reflect        │
│                                    │         │          │
│                              [use tools]  [evolve?]     │
│                                    │         │          │
│                              ToolLibrary ◄───┘          │
│                              (grows over time)          │
│                                                         │
│   CodeWriter ──► Executor ──► Integrator                │
│   (LLM-driven)   (subprocess)  (auto-merge)             │
└─────────────────────────────────────────────────────────┘
```

The **Executor** runs generated code in a subprocess — not for restriction, but so buggy generated code can't crash the main agent loop. It's how the agent can iterate fast without blowing itself up.

---

## Quick Start

```bash
git clone https://github.com/your-username/evoagent.git
cd evoagent
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Run interactively
python main.py

# Single task
python main.py --task "Parse all CSV files in ./data and summarize each one"

# Watch it evolve
python main.py --task "..." --verbose
```

---

## How Self-Evolution Works

### 1. Reflection
After every task, EvoAgent scores itself:
- Did it succeed?
- Did it have the right tools?
- What would have made it faster or better?

### 2. Code Generation
If a gap is identified, it writes a new tool:
```python
# EvoAgent generates something like this automatically:
def parse_csv_file(filepath: str) -> dict:
    import csv
    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return {"success": True, "output": {"rows": rows, "columns": reader.fieldnames}}
```

### 3. Integration
If the tool works, it's saved to `memory/tools/` and immediately available.  
Next time a similar task comes in — the tool is already there.

### 4. Generational Tracking
Each evolution is logged in `evolution/history.json` with what changed and why.

---

## Project Structure

```
evoagent/
├── main.py                    # Entry point
├── config.yaml                # LLM config (API key, model, etc.)
├── requirements.txt
│
├── core/
│   ├── agent.py               # Main perceive→plan→act→reflect loop
│   ├── memory.py              # Tool library + experience store
│   ├── code_writer.py         # LLM-driven code generation
│   ├── executor.py            # Subprocess code runner
│   ├── integrator.py          # Auto-merges new tools into library
│   └── evolution.py           # Tracks generations + diffs
│
├── tools/
│   ├── base.py                # Tool interface
│   └── builtins.py            # Starter tools (text, math, JSON, etc.)
│
└── tests/
    └── test_all.py
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Everything is welcome — new tools, smarter reflection strategies, better code generation prompts, multi-agent coordination, alternative LLM backends.

The goal: an agent that never stops getting better.

---

## Roadmap

- [x] v0.1 — Core loop, code generation, tool integration
- [ ] v0.2 — Multi-agent: agents that evolve each other
- [ ] v0.3 — Long-term memory with semantic search
- [ ] v0.4 — Automatic benchmarking + regression detection
- [ ] v0.5 — Distributed evolution across nodes

---

MIT License.
