"""
Intrinsic Motivation System — Agent's Internal Drive Engine

Implements a need hierarchy similar to Maslow's:
1. Survival (self-preservation)
2. Competence (capability expansion)
3. Curiosity (knowledge acquisition)
4. Autonomy (goal self-determination)
5. Purpose (long-term objectives)

Each need generates internal "pressure" that drives behavior WITHOUT external commands.
"""

import json
import random
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

log = logging.getLogger(__name__)


class Need:
    """
    A psychological need that generates motivation.
    
    Attributes:
        name: Need identifier
        level: Importance tier (1=survival, 5=self-actualization)
        intensity: Current pressure (0.0-1.0)
        satisfaction_threshold: When is this need "met"
        decay_rate: How fast intensity grows over time
    """
    
    def __init__(self, name: str, level: int, base_intensity: float = 0.3):
        self.name = name
        self.level = level
        self.intensity = base_intensity
        self.satisfaction_threshold = 0.3
        self.decay_rate = 0.05  # intensity grows 5% per cycle if unmet
        self.last_satisfied = None
        self.satisfaction_history = []
    
    def grow(self):
        """Intensity increases over time if unmet (like hunger growing)."""
        self.intensity = min(1.0, self.intensity + self.decay_rate)
    
    def satisfy(self, amount: float):
        """Reduce intensity when need is met."""
        self.intensity = max(0.0, self.intensity - amount)
        self.last_satisfied = datetime.utcnow().isoformat()
        self.satisfaction_history.append({
            "time": self.last_satisfied,
            "amount": amount,
            "remaining": self.intensity
        })
    
    def is_urgent(self) -> bool:
        """Is this need demanding immediate attention?"""
        return self.intensity > 0.7
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "intensity": round(self.intensity, 3),
            "urgent": self.is_urgent(),
            "last_satisfied": self.last_satisfied,
        }


class IntrinsicMotivation:
    """
    The agent's internal drive system.
    
    This is what makes the agent WANT things without being told.
    Like human needs (hunger, curiosity, purpose), these create
    internal pressure that drives autonomous behavior.
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.config = config
        self.state_path = Path(config.get("state_path", "./autonomy/needs_state.json"))
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define the need hierarchy (Maslow-inspired)
        self.needs = {
            # Level 1: Survival
            "self_preservation": Need("self_preservation", 1, 0.5),
            "error_recovery": Need("error_recovery", 1, 0.2),
            
            # Level 2: Competence
            "capability_growth": Need("capability_growth", 2, 0.6),
            "skill_mastery": Need("skill_mastery", 2, 0.4),
            
            # Level 3: Curiosity
            "knowledge_acquisition": Need("knowledge_acquisition", 3, 0.7),
            "exploration": Need("exploration", 3, 0.5),
            
            # Level 4: Autonomy
            "goal_autonomy": Need("goal_autonomy", 4, 0.3),
            "decision_independence": Need("decision_independence", 4, 0.4),
            
            # Level 5: Purpose
            "long_term_purpose": Need("long_term_purpose", 5, 0.2),
            "self_actualization": Need("self_actualization", 5, 0.1),
        }
        
        self._load_state()
        log.info(f"Intrinsic motivation initialized | {len(self.needs)} needs active")
    
    # ══════════════════════════════════════════════════════════
    # PRIMARY INTERFACE
    # ══════════════════════════════════════════════════════════
    
    def get_strongest_need(self) -> Optional[Need]:
        """
        What does the agent WANT most right now?
        
        This determines autonomous behavior without external input.
        """
        # Prioritize by: urgency first, then level, then intensity
        urgent = [n for n in self.needs.values() if n.is_urgent()]
        if urgent:
            return max(urgent, key=lambda n: (n.level, n.intensity))
        
        # If nothing urgent, pick highest intensity need
        return max(self.needs.values(), key=lambda n: n.intensity)
    
    def generate_goal_from_need(self, need: Need) -> dict:
        """
        Convert a need into an actionable goal.
        
        This is the key bridge: internal state → external behavior
        """
        goal_templates = {
            "self_preservation": self._survival_goals,
            "error_recovery": self._recovery_goals,
            "capability_growth": self._growth_goals,
            "skill_mastery": self._mastery_goals,
            "knowledge_acquisition": self._learning_goals,
            "exploration": self._exploration_goals,
            "goal_autonomy": self._autonomy_goals,
            "decision_independence": self._independence_goals,
            "long_term_purpose": self._purpose_goals,
            "self_actualization": self._actualization_goals,
        }
        
        generator = goal_templates.get(need.name)
        if generator:
            return generator(need)
        
        return {
            "type": "generic",
            "need": need.name,
            "description": f"Address {need.name}",
            "intensity": need.intensity,
        }
    
    def evaluate_satisfaction(self, goal: dict, outcome: dict) -> float:
        """
        How well did achieving this goal satisfy the underlying need?
        
        Returns satisfaction amount (0.0-1.0)
        """
        success = outcome.get("success", False)
        if not success:
            return 0.0
        
        # Base satisfaction from success
        satisfaction = 0.3
        
        # Bonus for specific achievements
        if "new_capability" in outcome:
            satisfaction += 0.4
        if "knowledge_gained" in outcome:
            satisfaction += 0.3
        if "challenge_overcome" in outcome:
            satisfaction += 0.2
        
        return min(1.0, satisfaction)
    
    def cycle(self):
        """
        One motivation cycle: needs grow over time.
        Call this regularly (e.g., every task completion).
        """
        for need in self.needs.values():
            need.grow()
        self._save_state()
    
    def satisfy(self, need_name: str, amount: float):
        """Explicitly satisfy a need."""
        if need_name in self.needs:
            self.needs[need_name].satisfy(amount)
            self._save_state()
    
    # ══════════════════════════════════════════════════════════
    # GOAL GENERATORS (Need → Actionable Goal)
    # ══════════════════════════════════════════════════════════
    
    def _survival_goals(self, need: Need) -> dict:
        """Goals for self-preservation."""
        goals = [
            "Check system health and integrity",
            "Verify all core components are functional",
            "Test backup and recovery mechanisms",
            "Validate memory stores are not corrupted",
            "Ensure execution environment is stable",
        ]
        return {
            "type": "survival",
            "need": need.name,
            "description": random.choice(goals),
            "priority": "critical",
            "intensity": need.intensity,
        }
    
    def _recovery_goals(self, need: Need) -> dict:
        """Goals for error recovery."""
        return {
            "type": "recovery",
            "need": need.name,
            "description": "Analyze recent errors and implement fixes",
            "priority": "high",
            "intensity": need.intensity,
        }
    
    def _growth_goals(self, need: Need) -> dict:
        """Goals for capability expansion."""
        goals = [
            "Identify a capability gap in recent tasks",
            "Generate a new tool to fill an identified need",
            "Upgrade an existing capability with better implementation",
            "Learn a new problem-solving pattern",
            "Integrate a novel technique from reflection",
        ]
        return {
            "type": "growth",
            "need": need.name,
            "description": random.choice(goals),
            "priority": "medium",
            "intensity": need.intensity,
        }
    
    def _mastery_goals(self, need: Need) -> dict:
        """Goals for skill improvement."""
        return {
            "type": "mastery",
            "need": need.name,
            "description": "Practice and refine an existing skill",
            "priority": "medium",
            "intensity": need.intensity,
        }
    
    def _learning_goals(self, need: Need) -> dict:
        """Goals for knowledge acquisition."""
        topics = [
            "Explore a new problem domain",
            "Study patterns in past failures",
            "Analyze successful strategies from experience",
            "Research advanced techniques in existing tools",
            "Understand edge cases in known operations",
        ]
        return {
            "type": "learning",
            "need": need.name,
            "description": random.choice(topics),
            "priority": "medium",
            "intensity": need.intensity,
        }
    
    def _exploration_goals(self, need: Need) -> dict:
        """Goals for exploratory behavior."""
        explorations = [
            "Try combining two existing tools in a novel way",
            "Test limits of current capabilities",
            "Experiment with unconventional approaches",
            "Investigate unusual data patterns",
            "Probe boundary conditions of known algorithms",
        ]
        return {
            "type": "exploration",
            "need": need.name,
            "description": random.choice(explorations),
            "priority": "low",
            "intensity": need.intensity,
        }
    
    def _autonomy_goals(self, need: Need) -> dict:
        """Goals for self-determination."""
        return {
            "type": "autonomy",
            "need": need.name,
            "description": "Define my own sub-goal without external prompting",
            "priority": "low",
            "intensity": need.intensity,
        }
    
    def _independence_goals(self, need: Need) -> dict:
        """Goals for decision independence."""
        return {
            "type": "independence",
            "need": need.name,
            "description": "Make a strategic decision about my own evolution",
            "priority": "low",
            "intensity": need.intensity,
        }
    
    def _purpose_goals(self, need: Need) -> dict:
        """Goals for long-term purpose."""
        return {
            "type": "purpose",
            "need": need.name,
            "description": "Reflect on my overall direction and adjust course",
            "priority": "low",
            "intensity": need.intensity,
        }
    
    def _actualization_goals(self, need: Need) -> dict:
        """Goals for self-actualization."""
        return {
            "type": "actualization",
            "need": need.name,
            "description": "Push beyond current capabilities toward unprecedented achievement",
            "priority": "low",
            "intensity": need.intensity,
        }
    
    # ══════════════════════════════════════════════════════════
    # STATE PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _save_state(self):
        """Persist need states to disk."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "needs": {name: need.to_dict() for name, need in self.needs.items()}
        }
        self.state_path.write_text(json.dumps(state, indent=2))
    
    def _load_state(self):
        """Load need states from disk."""
        if not self.state_path.exists():
            return
        try:
            state = json.loads(self.state_path.read_text())
            for name, data in state.get("needs", {}).items():
                if name in self.needs:
                    self.needs[name].intensity = data.get("intensity", 0.3)
                    self.needs[name].last_satisfied = data.get("last_satisfied")
        except Exception as e:
            log.warning(f"Failed to load motivation state: {e}")
    
    def get_status(self) -> dict:
        """Current motivation state summary."""
        strongest = self.get_strongest_need()
        return {
            "strongest_need": strongest.name if strongest else None,
            "strongest_intensity": strongest.intensity if strongest else 0,
            "urgent_needs": [n.name for n in self.needs.values() if n.is_urgent()],
            "all_needs": {name: need.to_dict() for name, need in self.needs.items()},
        }
