# Contributing to EvoAgent

EvoAgent is an open experiment in autonomous self-improving AI.
Every contribution moves this forward — code, ideas, benchmarks, new tools.

---

## Getting Started

```bash
git clone https://github.com/your-username/evoagent.git
cd evoagent
pip install -r requirements.txt
cp config.example.yaml config.yaml   # add your API key
pytest tests/ -v                     # all should pass
```

---

## What to Build

### 🔧 New Built-in Tools (`tools/builtins.py`)
The easiest contribution. Add a function following the contract:
```python
def my_tool(**kwargs) -> dict:
    try:
        # do something real
        return {"success": True, "output": result}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}
```
Then add it to `BUILTIN_TOOLS`. Some ideas:
- `csv_parse` — read/write CSV
- `http_get` — make HTTP requests  
- `regex_extract` — extract patterns from text
- `file_read` / `file_write` — file operations
- `code_run` — run Python snippets (meta!)
- `summarize` — LLM-based text summarization
- `diff_text` — diff two strings

### 🧠 Smarter Recall (`core/memory.py`)
Currently uses keyword matching. Upgrade ideas:
- Embedding-based semantic search (sentence-transformers)
- Vector store integration (FAISS, ChromaDB)
- Tool usage statistics (use success rate to rank tools)

### 🔄 Better Reflection Prompts (`core/agent.py`)
The reflection prompt drives when and what the agent evolves.
Better prompts → better self-improvement. Experiment freely.

### 🤖 Multi-Agent Evolution
Agents that evolve each other:
- Agent A generates a tool, Agent B critiques it
- Debate-style improvement before integration
- Population-based evolution (keep best variants)

### 📊 Benchmarks
Build tasks that measure agent improvement over generations:
- Standard task sets with known optimal solutions
- Regression detection (did this evolution break something?)
- Speed benchmarks

### 🌐 Alternative LLM Backends
Add support for Ollama, Mistral, Gemini, etc. in `main.py`.

---

## Code Style

- Python 3.10+
- Type hints where they add clarity
- Keep functions small and focused
- Every new feature needs a test in `tests/test_all.py`

---

## Submitting

```bash
git checkout -b your-feature
# make changes
pytest tests/ -v
git commit -m "feat: what you built"
git push origin your-feature
# open a pull request
```

Commit prefixes: `feat:` `fix:` `docs:` `refactor:` `test:` `perf:`

---

That's it. Ship it.
