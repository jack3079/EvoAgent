"""
Memory — Persistent storage for tools, experiences, and agent knowledge.

Three stores:
  1. Tools      — Python functions the agent can call (JSON files in memory/tools/)
  2. Experiences— Past task outcomes used for similarity recall (memory/experiences.json)
  3. Archive    — Old versions of replaced tools (memory/archive/)
"""

import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from collections import deque
from typing import Optional

log = logging.getLogger(__name__)


class Memory:

    def __init__(self, config: dict = None):
        config = config or {}
        base = Path(config.get("base_path", "./memory"))
        self.tools_dir = base / "tools"
        self.archive_dir = base / "archive"
        self.exp_file = base / "experiences.json"

        for d in [self.tools_dir, self.archive_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self._tools: dict = self._load_tools()
        self._experiences: deque = deque(
            self._load_json(self.exp_file) or [],
            maxlen=config.get("max_experiences", 1000)
        )

        log.info(f"Memory loaded: {len(self._tools)} tools, {len(self._experiences)} experiences")

    # ── Tools ────────────────────────────────────────────────

    def save_tool(self, tool: dict):
        name = tool.get("name", f"tool_{_short_hash(str(tool))}")
        tool["name"] = name
        tool["updated_at"] = datetime.utcnow().isoformat()
        path = self.tools_dir / f"{name}.json"
        path.write_text(json.dumps(tool, indent=2, default=str), encoding="utf-8")
        self._tools[name] = tool
        log.debug(f"Saved tool: {name}")

    def get_tool(self, name: str) -> Optional[dict]:
        return self._tools.get(name)

    def all_tools(self) -> list[dict]:
        return list(self._tools.values())

    def best_tool_for(self, task: str) -> Optional[dict]:
        """Simple keyword matching to find the most relevant tool."""
        words = set(task.lower().split())
        best, best_score = None, 0
        for tool in self._tools.values():
            text = f"{tool.get('name','')} {tool.get('description','')}".lower()
            score = sum(1 for w in words if w in text)
            if score > best_score:
                best_score = score
                best = tool
        return best if best_score >= 2 else None

    def archive_tool(self, tool: dict):
        name = tool.get("name", "unknown")
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.archive_dir / f"{name}_{ts}.json"
        path.write_text(json.dumps(tool, indent=2, default=str), encoding="utf-8")
        log.debug(f"Archived old version: {name}")

    def delete_tool(self, name: str):
        if name in self._tools:
            tool = self._tools.pop(name)
            self.archive_tool(tool)
            p = self.tools_dir / f"{name}.json"
            if p.exists():
                p.unlink()

    # ── Experiences ──────────────────────────────────────────

    def store(self, experience: dict):
        experience["id"] = _short_hash(str(experience))
        self._experiences.append(experience)
        self._save_json(self.exp_file, list(self._experiences))

    def recall(self, query: str, k: int = 5) -> list[dict]:
        """Return up to k past experiences relevant to query (keyword match)."""
        words = set(query.lower().split())
        scored = []
        for exp in self._experiences:
            text = f"{exp.get('task','')} {' '.join(exp.get('learned',[]))}".lower()
            score = sum(1 for w in words if w in text)
            if score > 0:
                scored.append((score, exp))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"task": e.get("task"), "success": e.get("success"), "learned": e.get("learned", [])}
            for _, e in scored[:k]
        ]

    # ── Internal ─────────────────────────────────────────────

    def _load_tools(self) -> dict:
        tools = {}
        for f in self.tools_dir.glob("*.json"):
            try:
                t = json.loads(f.read_text(encoding="utf-8"))
                tools[t.get("name", f.stem)] = t
            except Exception as e:
                log.warning(f"Failed to load tool {f.name}: {e}")
        return tools

    def _load_json(self, path: Path):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def _save_json(self, path: Path, data):
        try:
            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        except Exception as e:
            log.error(f"Failed to save {path}: {e}")


def _short_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:10]
