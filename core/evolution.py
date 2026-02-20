"""
EvolutionLog — Tracks every capability the agent adds to itself.

Stored in evolution/history.json.
Each record: generation, timestamp, trigger task, new tool name, test results.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)


class EvolutionLog:

    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("log_path", "./evolution/history.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.history: list = self._load()
        log.info(f"Evolution log: {len(self.history)} generations recorded")

    def record(
        self,
        generation: int,
        trigger: str,
        new_tool: str,
        description: str,
        test_results: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        entry = {
            "generation": generation,
            "timestamp": datetime.utcnow().isoformat(),
            "trigger": trigger,
            "new_tool": new_tool,
            "description": description,
            "test_pass_rate": _pass_rate(test_results) if test_results else None,
            **(metadata or {}),
        }
        self.history.append(entry)
        self._save()
        log.info(f"Generation {generation} recorded: {new_tool}")

    def timeline(self) -> list[dict]:
        return [
            {
                "gen": e["generation"],
                "ts": e["timestamp"][:10],
                "tool": e["new_tool"],
                "trigger": e["trigger"][:60],
            }
            for e in self.history
        ]

    def report(self) -> str:
        if not self.history:
            return "No evolutions yet."
        lines = [
            f"{'='*60}",
            f"EvoAgent Evolution Report",
            f"{'='*60}",
            f"Total generations: {len(self.history)}",
            f"First evolution: {self.history[0]['timestamp'][:10]}",
            f"Latest evolution: {self.history[-1]['timestamp'][:10]}",
            f"",
            f"Timeline:",
        ]
        for e in self.history:
            lines.append(
                f"  Gen {e['generation']:>3} | {e['timestamp'][:10]} | "
                f"{e['new_tool']:<30} | {e['trigger'][:40]}"
            )
        lines.append(f"{'='*60}")
        return "\n".join(lines)

    def _load(self) -> list:
        if self.path.exists():
            try:
                d = json.loads(self.path.read_text(encoding="utf-8"))
                return d if isinstance(d, list) else []
            except Exception:
                return []
        return []

    def _save(self):
        self.path.write_text(
            json.dumps(self.history, indent=2, default=str),
            encoding="utf-8"
        )


def _pass_rate(results: list) -> Optional[float]:
    if not results:
        return None
    passed = sum(1 for r in results if r.get("passed"))
    return passed / len(results)
