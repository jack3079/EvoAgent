# 🚀 EvoAgent v2.0 — Quick Start Guide

## What You Have

Two evolution systems in one package:

1. **Basic Tool Evolution** — Learns capabilities  
2. **ERL (Policy Evolution)** — Learns reasoning principles ⭐

---

## Installation

```bash
unzip EvoAgent_v2_ERL.zip
cd EvoAgent_v2
pip install -r requirements.txt
```

---

## Run Demos (No API Key Needed)

### 1. See the Difference First
```bash
python compare_agents.py
```
This explains why ERL is revolutionary.

### 2. Run Basic Tool Evolution
```bash
python evolve.py
```
Watch the agent add tools to its library.

### 3. Run ERL Evolution ⭐
```bash
python evolve_erl.py
```
Watch the agent learn **reasoning principles** that transfer across tasks.

---

## With Real LLM (Anthropic API)

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Tool evolution
python evolve.py --live

# ERL evolution (recommended)
python evolve_erl.py --live
```

---

## Interactive Mode

```bash
python main.py
# or
python -c "from core.erl_agent import ERLAgent; agent = ERLAgent({}, None); print(agent.run('your task'))"
```

---

## Key Files to Explore

**ERL Core:**
- `core/erl_agent.py` — Two-attempt learning cycle
- `core/policy_store.py` — Learned reasoning principles
- `core/reflection_engine.py` — Deep reflection (Kolb's cycle)

**Comparison:**
- `compare_agents.py` — See the difference explained

**Demos:**
- `evolve.py` — Basic tool evolution
- `evolve_erl.py` — ERL demonstration

---

## What ERL Does Differently

**Tool-only:**
```python
Task: Parse CSV → Fails
→ Creates csv_parser tool
→ Next CSV: ✓  |  Next JSON: ✗
```

**ERL:**
```python
Task: Parse CSV → Fails
→ Reflects: "I assumed format without validation"
→ Learns: "Always validate data structure first"
→ Next CSV: ✓  |  Next JSON: ✓  |  Next XML: ✓
```

**One learns capabilities. The other learns to THINK.**

---

## Research Paper

Based on:
> "Kolb-Based Experiential Learning for Generalist Agents  
> with Human-Level Kaggle Data Science Performance"

Agent K (using ERL) achieved:
- **Top 2% on Kaggle** (1694 Elo-MMR)
- **9 gold, 8 silver, 12 bronze medals**
- First AI to beat median humans in data science

---

## Next Steps

1. Run `python compare_agents.py` — Understand the difference
2. Run `python evolve_erl.py` — See it in action
3. Read `README_ERL.md` — Full documentation
4. Explore `memory_erl/policy.json` — See learned principles
5. Modify `evolve_erl.py` — Add your own tasks

---

## Need Help?

- Check the demos first — they're self-explanatory
- Read the code comments — they explain the "why"
- The paper explains the theory
- PRs welcome for improvements!

---

**The goal: Build agents that don't just learn skills — they learn to think.**
