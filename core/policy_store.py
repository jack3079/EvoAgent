"""
PolicyStore — Manages learned reasoning principles and heuristics

Unlike tools (which add capabilities), policies change HOW the agent thinks.
This implements the "internalization" part of ERL — successful reflection-guided
behavior is reinforced back into the base policy.

Based on: Kolb's Experiential Learning + the paper's policy internalization approach
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)


class PolicyStore:
    """
    Stores learned reasoning patterns, heuristics, and principles.
    
    These are NOT tools (executable code), but rather:
    - Problem-solving patterns ("when X fails, try Y")
    - Domain heuristics ("for data tasks, always check dimensions first")
    - Meta-cognitive strategies ("if stuck, break into smaller steps")
    - Error recovery patterns ("if timeout, reduce input size")
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./memory/policy.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core policy document
        self.principles: list[dict] = self._load()
        
        # Bootstrap with fundamental principles if empty
        if not self.principles:
            self._bootstrap()
        
        log.info(f"PolicyStore loaded: {len(self.principles)} principles")

    def add_principle(self, principle: dict):
        """
        Add a learned principle to the policy.
        
        principle structure:
        {
            "pattern": "when facing X, do Y",
            "context": "task category or domain",
            "learned_from": "specific task that taught this",
            "success_rate": 1.0,
            "applications": 1,
            "added_at": "timestamp"
        }
        """
        principle["added_at"] = datetime.utcnow().isoformat()
        principle["applications"] = principle.get("applications", 0)
        principle["success_rate"] = principle.get("success_rate", 1.0)
        
        # Check for duplicate patterns
        existing = next(
            (p for p in self.principles if p.get("pattern") == principle.get("pattern")),
            None
        )
        
        if existing:
            # Reinforce existing principle
            existing["applications"] += 1
            # Update success rate (exponential moving average)
            alpha = 0.3
            existing["success_rate"] = (
                alpha * principle.get("success_rate", 1.0) +
                (1 - alpha) * existing["success_rate"]
            )
            existing["last_reinforced"] = datetime.utcnow().isoformat()
            log.info(f"Reinforced principle: {principle.get('pattern', '')[:60]}")
        else:
            self.principles.append(principle)
            log.info(f"New principle learned: {principle.get('pattern', '')[:60]}")
        
        self._save()

    def get_relevant_principles(self, task: str, context: str = "", top_k: int = 5) -> list[dict]:
        """
        Retrieve principles relevant to the current task.
        Used to guide reasoning on new tasks.
        """
        query_words = set(task.lower().split()) | set(context.lower().split())
        scored = []
        
        for p in self.principles:
            text = f"{p.get('pattern', '')} {p.get('context', '')}".lower()
            score = sum(1 for w in query_words if w in text)
            # Boost by success rate and application count
            score *= p.get("success_rate", 0.5)
            score *= (1 + 0.1 * min(p.get("applications", 0), 10))  # cap boost
            if score > 0:
                scored.append((score, p))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]

    def to_prompt_section(self, task: str = "") -> str:
        """
        Format relevant principles as a prompt section.
        This gets injected into the agent's system prompt dynamically.
        """
        relevant = self.get_relevant_principles(task, top_k=8)
        if not relevant:
            return ""
        
        lines = ["## Learned Reasoning Principles\n"]
        lines.append("Based on past experience, apply these patterns when relevant:\n")
        for i, p in enumerate(relevant, 1):
            pattern = p.get("pattern", "")
            apps = p.get("applications", 0)
            rate = p.get("success_rate", 0)
            lines.append(f"{i}. {pattern} (applied {apps}× | {rate:.0%} success)")
        
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Statistics about the policy store."""
        return {
            "total_principles": len(self.principles),
            "avg_success_rate": (
                sum(p.get("success_rate", 0) for p in self.principles) / 
                max(1, len(self.principles))
            ),
            "total_applications": sum(p.get("applications", 0) for p in self.principles),
            "most_used": sorted(
                self.principles,
                key=lambda p: p.get("applications", 0),
                reverse=True
            )[:3] if self.principles else []
        }

    # ── Internal ──────────────────────────────────────────

    def _bootstrap(self):
        """Initialize with fundamental reasoning principles."""
        fundamentals = [
            {
                "pattern": "When a task is unclear, break it into concrete sub-steps before executing",
                "context": "general",
                "learned_from": "bootstrap",
                "success_rate": 0.9,
                "applications": 0,
            },
            {
                "pattern": "When encountering unfamiliar data format, first inspect structure before processing",
                "context": "data",
                "learned_from": "bootstrap",
                "success_rate": 0.85,
                "applications": 0,
            },
            {
                "pattern": "When a direct approach fails, try decomposing the problem into smaller pieces",
                "context": "general",
                "learned_from": "bootstrap",
                "success_rate": 0.8,
                "applications": 0,
            },
            {
                "pattern": "When dealing with lists or collections, verify they are non-empty before operations",
                "context": "data",
                "learned_from": "bootstrap",
                "success_rate": 0.95,
                "applications": 0,
            },
        ]
        self.principles = fundamentals
        self._save()

    def _load(self) -> list[dict]:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
            except Exception as e:
                log.warning(f"Failed to load policy: {e}")
        return []

    def _save(self):
        try:
            self.path.write_text(
                json.dumps(self.principles, indent=2, default=str),
                encoding="utf-8"
            )
        except Exception as e:
            log.error(f"Failed to save policy: {e}")
