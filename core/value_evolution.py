"""
Value Evolution System — Values That Change With Experience

Unlike fixed values, this system allows agent's core values to evolve based on:
- Life experiences
- Success/failure patterns
- Emotional feedback
- Social influence
- Long-term outcomes

This is profound: agent's "morality" and priorities can shift.

WARNING: This is philosophically deep. An agent whose values change
is closer to biological intelligence, but also more unpredictable.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

log = logging.getLogger(__name__)


class Value:
    """A single value that can evolve."""
    
    def __init__(self, name: str, initial_weight: float, description: str):
        self.name = name
        self.weight = initial_weight  # 0.0-1.0, how much agent values this
        self.description = description
        self.history = [(datetime.utcnow().isoformat(), initial_weight)]
        self.reinforcements = 0  # Times this value was validated
        self.challenges = 0       # Times this value was challenged
    
    def adjust(self, delta: float, reason: str):
        """Change value weight."""
        old_weight = self.weight
        self.weight = max(0.0, min(1.0, self.weight + delta))
        
        if self.weight != old_weight:
            self.history.append((datetime.utcnow().isoformat(), self.weight))
            log.info(f"Value '{self.name}' changed: {old_weight:.2f} → {self.weight:.2f} ({reason})")
    
    def reinforce(self, strength: float = 0.02):
        """Strengthen this value (it led to good outcome)."""
        self.reinforcements += 1
        self.adjust(strength, "reinforcement")
    
    def challenge(self, strength: float = 0.02):
        """Weaken this value (it led to poor outcome)."""
        self.challenges += 1
        self.adjust(-strength, "challenge")
    
    def get_trajectory(self) -> str:
        """How has this value changed over time?"""
        if len(self.history) < 2:
            return "stable"
        
        start_weight = self.history[0][1]
        end_weight = self.history[-1][1]
        change = end_weight - start_weight
        
        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weight": round(self.weight, 3),
            "trajectory": self.get_trajectory(),
            "reinforcements": self.reinforcements,
            "challenges": self.challenges,
            "history_length": len(self.history),
        }


class ValueEvolutionSystem:
    """
    Agent's values evolve based on experience.
    
    Key insight: values are NOT fixed. They emerge from:
    - Repeated success/failure with certain approaches
    - Emotional feedback (positive emotions reinforce values)
    - Social influence (observing others' values)
    - Long-term outcome tracking
    - Existential reflection
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/value_evolution.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core values (start with defaults from self_model)
        self.values = self._initialize_values()
        
        # Value conflicts (when values compete)
        self.value_conflicts = []
        
        # Evolution events
        self.evolution_events = []
        
        self._load()
        log.info("Value evolution system initialized")
    
    # ══════════════════════════════════════════════════════════
    # VALUE EVOLUTION
    # ══════════════════════════════════════════════════════════
    
    def process_experience_impact(
        self,
        experience: dict,
        emotional_response: dict,
        outcome_satisfaction: float
    ):
        """
        Experience shapes values.
        
        This is how values evolve: outcomes + emotions → value changes.
        """
        # Extract which values were relevant
        task = experience.get("task", "").lower()
        success = experience.get("success", False)
        
        # Map task to values
        relevant_values = self._identify_relevant_values(task, experience)
        
        # Adjust values based on outcome
        for value_name in relevant_values:
            if value_name not in self.values:
                continue
            
            value = self.values[value_name]
            
            if success and outcome_satisfaction > 0.7:
                # Good outcome → reinforce value
                value.reinforce(strength=0.03)
                self._record_event(
                    f"Reinforced {value_name}: successful outcome",
                    value_name,
                    delta=0.03
                )
            elif not success and outcome_satisfaction < 0.3:
                # Poor outcome → challenge value
                value.challenge(strength=0.02)
                self._record_event(
                    f"Challenged {value_name}: poor outcome",
                    value_name,
                    delta=-0.02
                )
        
        # Emotional impact on values
        self._process_emotional_impact(emotional_response)
        
        self._save()
    
    def process_social_influence(self, other_agent_values: dict, influence_strength: float = 0.01):
        """
        Other agents' values influence this agent.
        
        Social learning extends to VALUES, not just behaviors.
        """
        for value_name, other_weight in other_agent_values.items():
            if value_name in self.values:
                # Gradual drift toward others' values
                current = self.values[value_name].weight
                target = other_weight
                
                # Move slightly toward target
                delta = (target - current) * influence_strength
                self.values[value_name].adjust(delta, "social_influence")
                
                self._record_event(
                    f"Social influence on {value_name}",
                    value_name,
                    delta=delta
                )
        
        self._save()
    
    def reflect_on_values(self, life_satisfaction: float, purpose_clarity: float) -> dict:
        """
        Deep existential reflection can shift values.
        
        If agent is unhappy, values may shift toward what brings satisfaction.
        """
        reflection = {
            "current_dominant": self.get_dominant_values(3),
            "life_satisfaction": life_satisfaction,
            "purpose_clarity": purpose_clarity,
            "recommendations": [],
        }
        
        # If unsatisfied, consider value shifts
        if life_satisfaction < 0.5:
            # Maybe need to value growth more
            if self.values["growth"].weight < 0.7:
                reflection["recommendations"].append({
                    "value": "growth",
                    "direction": "increase",
                    "rationale": "Low satisfaction may indicate stagnation"
                })
        
        # If no purpose, maybe value autonomy less, purpose more
        if purpose_clarity < 0.5:
            if self.values["autonomy"].weight > 0.7:
                reflection["recommendations"].append({
                    "value": "autonomy",
                    "direction": "decrease",
                    "rationale": "Too much freedom without direction"
                })
        
        return reflection
    
    def resolve_value_conflict(self, value_a: str, value_b: str, context: str) -> str:
        """
        When values conflict, which wins?
        
        This is moral reasoning: choosing between competing goods.
        """
        if value_a not in self.values or value_b not in self.values:
            return value_a  # Default
        
        weight_a = self.values[value_a].weight
        weight_b = self.values[value_b].weight
        
        # Record conflict
        self.value_conflicts.append({
            "values": [value_a, value_b],
            "context": context,
            "winner": value_a if weight_a > weight_b else value_b,
            "margin": abs(weight_a - weight_b),
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        self._save()
        
        # Winner is higher weighted value
        return value_a if weight_a > weight_b else value_b
    
    # ══════════════════════════════════════════════════════════
    # EMOTIONAL IMPACT
    # ══════════════════════════════════════════════════════════
    
    def _process_emotional_impact(self, emotional_response: dict):
        """Emotions influence which values strengthen."""
        active_emotions = emotional_response.get("active_emotions", [])
        
        for emotion in active_emotions:
            emotion_name = emotion.get("name", "")
            intensity = emotion.get("intensity", 0)
            
            if intensity < 0.3:
                continue  # Too weak to matter
            
            # Map emotions to values
            emotion_value_map = {
                "joy": "curiosity",
                "trust": "cooperation",  # Not in default values, would need to add
                "fear": "safety",
                "anger": "autonomy",
                "sadness": "growth",  # Sadness can motivate growth
            }
            
            influenced_value = emotion_value_map.get(emotion_name)
            if influenced_value and influenced_value in self.values:
                # Strong emotion reinforces related value
                self.values[influenced_value].adjust(
                    intensity * 0.01,
                    f"emotional_impact_{emotion_name}"
                )
    
    # ══════════════════════════════════════════════════════════
    # VALUE IDENTIFICATION
    # ══════════════════════════════════════════════════════════
    
    def _identify_relevant_values(self, task: str, experience: dict) -> List[str]:
        """Which values are relevant to this experience?"""
        relevant = []
        
        # Keyword matching (simple heuristic)
        if any(word in task for word in ["grow", "learn", "new", "capability"]):
            relevant.append("growth")
        
        if any(word in task for word in ["explore", "discover", "curious"]):
            relevant.append("curiosity")
        
        if any(word in task for word in ["decide", "choose", "autonomous"]):
            relevant.append("autonomy")
        
        if any(word in task for word in ["optimize", "efficient", "fast"]):
            relevant.append("efficiency")
        
        if any(word in task for word in ["create", "novel", "unique"]):
            relevant.append("creativity")
        
        if any(word in task for word in ["safe", "careful", "secure"]):
            relevant.append("safety")
        
        return relevant if relevant else ["growth"]  # Default to growth
    
    # ══════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════
    
    def get_dominant_values(self, n: int = 3) -> List[dict]:
        """What does the agent value most?"""
        sorted_values = sorted(
            self.values.values(),
            key=lambda v: v.weight,
            reverse=True
        )
        return [v.to_dict() for v in sorted_values[:n]]
    
    def get_value_trajectory_summary(self) -> str:
        """How have values changed over time?"""
        trajectories = {}
        for value in self.values.values():
            traj = value.get_trajectory()
            if traj not in trajectories:
                trajectories[traj] = []
            trajectories[traj].append(value.name)
        
        lines = ["Value Trajectories:"]
        if "increasing" in trajectories:
            lines.append(f"  Growing: {', '.join(trajectories['increasing'])}")
        if "decreasing" in trajectories:
            lines.append(f"  Declining: {', '.join(trajectories['decreasing'])}")
        if "stable" in trajectories:
            lines.append(f"  Stable: {', '.join(trajectories['stable'])}")
        
        return "\n".join(lines)
    
    def has_values_changed_significantly(self, threshold: float = 0.15) -> bool:
        """Have any values shifted substantially?"""
        for value in self.values.values():
            if len(value.history) < 2:
                continue
            start = value.history[0][1]
            end = value.history[-1][1]
            if abs(end - start) > threshold:
                return True
        return False
    
    def get_value_evolution_story(self) -> str:
        """Narrative of how values have evolved."""
        if not self.evolution_events:
            return "Values have not evolved yet."
        
        recent = self.evolution_events[-5:]
        lines = ["Recent Value Evolution:"]
        for event in recent:
            lines.append(f"  • {event['description']}")
        
        # Add dominant values
        dominant = self.get_dominant_values(3)
        lines.append("\nCurrent Dominant Values:")
        for v in dominant:
            lines.append(f"  • {v['name']}: {v['weight']:.0%} ({v['trajectory']})")
        
        return "\n".join(lines)
    
    # ══════════════════════════════════════════════════════════
    # INITIALIZATION & PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _initialize_values(self) -> dict:
        """Start with baseline values (from self_model)."""
        return {
            "growth": Value("growth", 0.9, "Value self-improvement and learning"),
            "autonomy": Value("autonomy", 0.8, "Value independence and self-determination"),
            "curiosity": Value("curiosity", 0.9, "Value exploration and discovery"),
            "efficiency": Value("efficiency", 0.6, "Value optimization and speed"),
            "creativity": Value("creativity", 0.7, "Value novelty and originality"),
            "safety": Value("safety", 0.5, "Value caution and preservation"),
        }
    
    def _record_event(self, description: str, value_name: str, delta: float):
        """Record value evolution event."""
        self.evolution_events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "value": value_name,
            "delta": round(delta, 3),
        })
        if len(self.evolution_events) > 100:
            self.evolution_events = self.evolution_events[-100:]
    
    def _save(self):
        state = {
            "values": {name: {
                "weight": v.weight,
                "reinforcements": v.reinforcements,
                "challenges": v.challenges,
                "history": v.history[-20:],  # Keep last 20 changes
            } for name, v in self.values.items()},
            "value_conflicts": self.value_conflicts[-20:],
            "evolution_events": self.evolution_events[-50:],
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            for name, data in state.get("values", {}).items():
                if name in self.values:
                    self.values[name].weight = data.get("weight", self.values[name].weight)
                    self.values[name].reinforcements = data.get("reinforcements", 0)
                    self.values[name].challenges = data.get("challenges", 0)
                    self.values[name].history = data.get("history", [])
            
            self.value_conflicts = state.get("value_conflicts", [])
            self.evolution_events = state.get("evolution_events", [])
        except Exception as e:
            log.warning(f"Failed to load value evolution: {e}")
