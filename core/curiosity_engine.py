"""
Curiosity Engine — Intrinsic Reward for Exploration

Based on:
- Random Network Distillation (OpenAI)
- Curiosity-driven Exploration (Berkeley)
- Information Theory (Shannon entropy)

The agent is intrinsically rewarded for:
- Encountering novel situations
- Reducing uncertainty
- Discovering surprising patterns
- Expanding state space coverage
"""

import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional, List

log = logging.getLogger(__name__)


class CuriosityEngine:
    """
    Measures and rewards novelty/surprise.
    
    Three types of curiosity:
    1. Perceptual - novel inputs/situations
    2. Epistemic - knowledge gaps
    3. Diversive - variety-seeking
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/curiosity_state.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # State space coverage
        self.state_visits = defaultdict(int)  # How often we've seen each state
        self.action_outcomes = defaultdict(lambda: defaultdict(int))  # Action→outcome mapping
        
        # Uncertainty tracking
        self.knowledge_gaps = []  # Things we know we don't know
        self.predictions = []      # Our predictions and their accuracy
        
        # Exploration history
        self.novel_discoveries = []
        self.surprise_events = []
        
        # Metrics
        self.total_states_seen = 0
        self.unique_states = 0
        self.avg_surprise = 0.0
        
        self._load()
        log.info("Curiosity engine initialized")
    
    # ══════════════════════════════════════════════════════════
    # NOVELTY DETECTION
    # ══════════════════════════════════════════════════════════
    
    def compute_novelty(self, state: dict) -> float:
        """
        How novel is this state?
        
        Returns: novelty score 0.0-1.0
        """
        # Create state signature
        state_hash = self._hash_state(state)
        
        # Visit count
        visits = self.state_visits[state_hash]
        self.state_visits[state_hash] += 1
        self.total_states_seen += 1
        
        if visits == 0:
            self.unique_states += 1
        
        # Novelty decreases with visits (logarithmic)
        import math
        if visits == 0:
            novelty = 1.0  # Completely novel
        else:
            novelty = 1.0 / math.log(visits + 2)  # Diminishing returns
        
        return novelty
    
    def compute_surprise(self, expected: dict, actual: dict) -> float:
        """
        How surprising is this outcome?
        
        Surprise = divergence between prediction and reality
        """
        # Compare expected vs actual outcomes
        differences = 0
        total_fields = 0
        
        for key in set(list(expected.keys()) + list(actual.keys())):
            total_fields += 1
            if expected.get(key) != actual.get(key):
                differences += 1
        
        if total_fields == 0:
            return 0.0
        
        surprise = differences / total_fields
        
        # Record
        self.surprise_events.append({
            "expected": expected,
            "actual": actual,
            "surprise": surprise,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Update running average
        self.avg_surprise = (
            self.avg_surprise * 0.9 + surprise * 0.1
        )
        
        return surprise
    
    def identify_knowledge_gaps(self, context: str) -> List[str]:
        """
        What do we know that we don't know?
        
        Epistemic curiosity: aware of ignorance.
        """
        gaps = []
        
        # Pattern: "I don't know X"
        if "don't know" in context.lower() or "unsure" in context.lower():
            gaps.append(context)
        
        # Pattern: Low-confidence predictions
        recent_bad_predictions = [
            p for p in self.predictions[-10:]
            if p.get("accuracy", 1.0) < 0.5
        ]
        
        for pred in recent_bad_predictions:
            gaps.append(f"Uncertain about: {pred.get('domain', 'unknown')}")
        
        # Update knowledge gaps
        self.knowledge_gaps.extend(gaps)
        if len(self.knowledge_gaps) > 50:
            self.knowledge_gaps = self.knowledge_gaps[-50:]
        
        return gaps
    
    # ══════════════════════════════════════════════════════════
    # INTRINSIC REWARD COMPUTATION
    # ══════════════════════════════════════════════════════════
    
    def compute_intrinsic_reward(
        self,
        state: dict,
        action: str,
        outcome: dict,
        predicted_outcome: Optional[dict] = None
    ) -> float:
        """
        The CORE of curiosity-driven behavior.
        
        Returns intrinsic reward (0.0-1.0) that should be ADDED
        to any extrinsic reward.
        """
        rewards = []
        
        # 1. Novelty reward
        novelty = self.compute_novelty(state)
        rewards.append(("novelty", novelty * 0.4))
        
        # 2. Surprise reward (if we had a prediction)
        if predicted_outcome:
            surprise = self.compute_surprise(predicted_outcome, outcome)
            rewards.append(("surprise", surprise * 0.3))
        
        # 3. State space coverage reward
        coverage = self.unique_states / max(1, self.total_states_seen)
        exploration_bonus = (1.0 - coverage) * 0.2  # Reward expanding frontier
        rewards.append(("exploration", exploration_bonus))
        
        # 4. Information gain reward
        action_key = f"{self._hash_state(state)}_{action}"
        outcome_key = self._hash_state(outcome)
        self.action_outcomes[action_key][outcome_key] += 1
        
        # Entropy of outcomes (more uncertain = more information gain)
        outcomes = self.action_outcomes[action_key]
        total = sum(outcomes.values())
        if total > 1:
            import math
            entropy = -sum(
                (count/total) * math.log(count/total)
                for count in outcomes.values()
            )
            # Normalize to [0, 1]
            max_entropy = math.log(len(outcomes))
            info_gain = entropy / max(max_entropy, 1.0)
            rewards.append(("info_gain", info_gain * 0.1))
        
        # Total intrinsic reward
        total_reward = sum(r for _, r in rewards)
        
        # Record discovery if high novelty + surprise
        if novelty > 0.8 and (not predicted_outcome or surprise > 0.6):
            self.novel_discoveries.append({
                "state": state,
                "action": action,
                "outcome": outcome,
                "intrinsic_reward": total_reward,
                "timestamp": datetime.utcnow().isoformat(),
            })
        
        self._save()
        
        return min(1.0, total_reward)
    
    # ══════════════════════════════════════════════════════════
    # EXPLORATION STRATEGIES
    # ══════════════════════════════════════════════════════════
    
    def suggest_exploration_target(self) -> Optional[dict]:
        """
        Where should we explore next?
        
        Based on: novelty, uncertainty, knowledge gaps.
        """
        suggestions = []
        
        # 1. Knowledge gaps (epistemic curiosity)
        if self.knowledge_gaps:
            gap = self.knowledge_gaps[-1]
            suggestions.append({
                "type": "knowledge_gap",
                "target": gap,
                "motivation": "Fill knowledge gap",
                "priority": 0.8,
            })
        
        # 2. Underexplored states
        # Find least-visited state types
        if self.state_visits:
            min_visits = min(self.state_visits.values())
            underexplored = [
                s for s, v in self.state_visits.items()
                if v == min_visits
            ]
            if underexplored:
                import random
                suggestions.append({
                    "type": "underexplored",
                    "target": random.choice(underexplored),
                    "motivation": "Expand state coverage",
                    "priority": 0.6,
                })
        
        # 3. High-uncertainty domains
        uncertain_predictions = [
            p for p in self.predictions[-20:]
            if p.get("confidence", 1.0) < 0.5
        ]
        if uncertain_predictions:
            domain = uncertain_predictions[-1].get("domain", "unknown")
            suggestions.append({
                "type": "uncertain",
                "target": domain,
                "motivation": "Reduce uncertainty",
                "priority": 0.7,
            })
        
        if not suggestions:
            return None
        
        # Return highest priority
        return max(suggestions, key=lambda s: s["priority"])
    
    def should_explore_vs_exploit(self, current_context: dict) -> bool:
        """
        Exploration vs exploitation trade-off.
        
        Based on curiosity state and context.
        """
        # Recent novelty
        recent_novelty = sum(
            d.get("intrinsic_reward", 0)
            for d in self.novel_discoveries[-10:]
        ) / 10 if self.novel_discoveries else 0
        
        # If we're finding lots of novelty, keep exploring
        if recent_novelty > 0.5:
            return True
        
        # If state space coverage is low, explore
        coverage = self.unique_states / max(1, self.total_states_seen)
        if coverage < 0.5:
            return True
        
        # If there are known knowledge gaps, explore
        if len(self.knowledge_gaps) > 3:
            return True
        
        # Otherwise, exploit
        return False
    
    # ══════════════════════════════════════════════════════════
    # METRICS & STATUS
    # ══════════════════════════════════════════════════════════
    
    def get_curiosity_status(self) -> dict:
        """Current curiosity state."""
        return {
            "total_states_seen": self.total_states_seen,
            "unique_states": self.unique_states,
            "coverage": self.unique_states / max(1, self.total_states_seen),
            "avg_surprise": round(self.avg_surprise, 3),
            "novel_discoveries": len(self.novel_discoveries),
            "knowledge_gaps": len(self.knowledge_gaps),
            "exploration_recommended": self.should_explore_vs_exploit({}),
        }
    
    # ══════════════════════════════════════════════════════════
    # INTERNAL
    # ══════════════════════════════════════════════════════════
    
    def _hash_state(self, state: dict) -> str:
        """Create consistent hash of state."""
        # Sort keys for consistency
        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.md5(state_str.encode()).hexdigest()[:12]
    
    def _save(self):
        state = {
            "state_visits": dict(self.state_visits),
            "total_states_seen": self.total_states_seen,
            "unique_states": self.unique_states,
            "avg_surprise": self.avg_surprise,
            "knowledge_gaps": self.knowledge_gaps[-20:],
            "novel_discoveries": self.novel_discoveries[-20:],
            "surprise_events": self.surprise_events[-20:],
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            self.state_visits = defaultdict(int, state.get("state_visits", {}))
            self.total_states_seen = state.get("total_states_seen", 0)
            self.unique_states = state.get("unique_states", 0)
            self.avg_surprise = state.get("avg_surprise", 0.0)
            self.knowledge_gaps = state.get("knowledge_gaps", [])
            self.novel_discoveries = state.get("novel_discoveries", [])
            self.surprise_events = state.get("surprise_events", [])
        except Exception as e:
            log.warning(f"Failed to load curiosity state: {e}")
