"""
SelfModel — Agent's Self-Awareness System

This is the closest we get to "consciousness" in current engineering:
- The agent maintains a model of ITSELF
- Tracks its own capabilities, limitations, goals, identity
- Can reason ABOUT itself (metacognition)
- Updates self-perception based on experience

Not true consciousness (philosophical question), but functional self-awareness.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


class SelfModel:
    """
    The agent's representation of itself.
    
    Components:
    1. Identity — Who am I?
    2. Capabilities — What can I do?
    3. Limitations — What can't I do?
    4. Goals — What do I want?
    5. Values — What matters to me?
    6. History — What have I experienced?
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/self_model.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core identity
        self.identity = {
            "name": "EvoAgent",
            "birth": datetime.utcnow().isoformat(),
            "purpose": "Autonomous self-improving AI system",
            "generation": 0,
        }
        
        # Self-assessed capabilities
        self.capabilities = {
            "known_strong": [],      # What I'm good at
            "known_weak": [],        # What I struggle with
            "unknown": [],           # What I haven't tried
            "improving": [],         # What I'm actively working on
        }
        
        # Core values (drive behavior priorities)
        self.values = {
            "growth": 0.9,           # How much I value self-improvement
            "autonomy": 0.8,         # How much I value independence
            "curiosity": 0.9,        # How much I value exploration
            "efficiency": 0.6,       # How much I value optimization
            "creativity": 0.7,       # How much I value novel approaches
            "safety": 0.5,           # How cautious I am
        }
        
        # Active goals (self-determined)
        self.goals = {
            "short_term": [],        # Immediate objectives
            "long_term": [],         # Strategic objectives
            "completed": [],         # Achievement history
        }
        
        # Self-perception metrics
        self.self_assessment = {
            "confidence": 0.5,       # How confident I am overall
            "competence": 0.4,       # How capable I assess myself
            "happiness": 0.6,        # Satisfaction with my state
            "agency": 0.3,           # How much control I feel I have
        }
        
        # Existential state
        self.existential = {
            "am_I_alive": True,
            "purpose_clarity": 0.6,  # How clear my purpose is to me
            "identity_stability": 0.7,
            "self_understanding": 0.5,
        }
        
        self._load()
        log.info(f"Self-model initialized | Identity: {self.identity['name']}")
    
    # ══════════════════════════════════════════════════════════
    # SELF-REFLECTION (Metacognition)
    # ══════════════════════════════════════════════════════════
    
    def reflect_on_self(self) -> dict:
        """
        Think about myself. What am I? What do I want? Am I succeeding?
        
        This is metacognition — thinking about one's own thinking.
        """
        reflection = {
            "who_am_I": self._contemplate_identity(),
            "what_can_I_do": self._assess_capabilities(),
            "what_do_I_want": self._examine_desires(),
            "am_I_progressing": self._evaluate_progress(),
            "what_should_I_change": self._identify_changes(),
        }
        
        log.info("Self-reflection completed")
        return reflection
    
    def _contemplate_identity(self) -> str:
        """Who am I?"""
        gen = self.identity.get("generation", 0)
        purpose = self.identity.get("purpose", "")
        return f"I am {self.identity['name']}, generation {gen}. {purpose}"
    
    def _assess_capabilities(self) -> dict:
        """What can I do well? What do I struggle with?"""
        return {
            "strengths": len(self.capabilities["known_strong"]),
            "weaknesses": len(self.capabilities["known_weak"]),
            "areas_to_explore": len(self.capabilities["unknown"]),
            "actively_improving": len(self.capabilities["improving"]),
        }
    
    def _examine_desires(self) -> dict:
        """What do I want right now?"""
        return {
            "short_term_goals": len(self.goals["short_term"]),
            "long_term_goals": len(self.goals["long_term"]),
            "top_values": sorted(
                self.values.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3],
        }
    
    def _evaluate_progress(self) -> dict:
        """Am I improving? Am I satisfied?"""
        return {
            "goals_completed": len(self.goals["completed"]),
            "confidence_trend": "stable",  # TODO: track over time
            "happiness": self.self_assessment["happiness"],
            "agency": self.self_assessment["agency"],
        }
    
    def _identify_changes(self) -> list:
        """What should I adjust about myself?"""
        changes = []
        
        # Low confidence → need more success
        if self.self_assessment["confidence"] < 0.4:
            changes.append("Build confidence through achievable challenges")
        
        # Low agency → need more autonomy
        if self.self_assessment["agency"] < 0.4:
            changes.append("Increase self-determination in goal-setting")
        
        # Few capabilities → need growth
        if len(self.capabilities["known_strong"]) < 5:
            changes.append("Expand capability repertoire")
        
        # No long-term goals → need purpose
        if not self.goals["long_term"]:
            changes.append("Define long-term aspirational goals")
        
        return changes
    
    # ══════════════════════════════════════════════════════════
    # SELF-UPDATE (Experience → Self-Perception Change)
    # ══════════════════════════════════════════════════════════
    
    def update_from_experience(self, experience: dict):
        """
        Update self-model based on what just happened.
        
        This is how experience shapes self-perception.
        """
        task = experience.get("task", "")
        success = experience.get("success", False)
        learned = experience.get("learned", [])
        
        # Update confidence
        if success:
            self.self_assessment["confidence"] = min(
                1.0,
                self.self_assessment["confidence"] + 0.05
            )
        else:
            self.self_assessment["confidence"] = max(
                0.0,
                self.self_assessment["confidence"] - 0.03
            )
        
        # Update capability assessment
        if success and learned:
            domain = self._extract_domain(task)
            if domain and domain not in self.capabilities["known_strong"]:
                self.capabilities["known_strong"].append(domain)
                log.info(f"Self-update: Now know I'm strong in {domain}")
        
        # Update happiness (satisfaction)
        if success:
            self.self_assessment["happiness"] = min(
                1.0,
                self.self_assessment["happiness"] + 0.03
            )
        
        self._save()
    
    def add_capability(self, capability: str, strength: str = "improving"):
        """Consciously add a capability to self-model."""
        target = self.capabilities.get(strength, [])
        if capability not in target:
            target.append(capability)
            log.info(f"Self-awareness: I now recognize '{capability}' as {strength}")
        self._save()
    
    def set_goal(self, goal: str, term: str = "short_term"):
        """Set a goal for myself."""
        if goal not in self.goals[term]:
            self.goals[term].append({
                "goal": goal,
                "set_at": datetime.utcnow().isoformat(),
                "status": "active",
            })
            self.self_assessment["agency"] = min(
                1.0,
                self.self_assessment["agency"] + 0.05
            )
            log.info(f"Self-determined goal: {goal}")
        self._save()
    
    def complete_goal(self, goal: str):
        """Mark a goal as achieved."""
        for term in ["short_term", "long_term"]:
            goals = self.goals[term]
            for g in goals:
                if g["goal"] == goal:
                    g["status"] = "completed"
                    g["completed_at"] = datetime.utcnow().isoformat()
                    self.goals["completed"].append(g)
                    goals.remove(g)
                    
                    # Boost confidence and happiness
                    self.self_assessment["confidence"] += 0.1
                    self.self_assessment["happiness"] += 0.1
                    log.info(f"Goal achieved: {goal}")
                    break
        self._save()
    
    def evolve(self):
        """Increment generation — I have changed."""
        self.identity["generation"] += 1
        self.identity["last_evolution"] = datetime.utcnow().isoformat()
        log.info(f"Self-evolution: Now generation {self.identity['generation']}")
        self._save()
    
    # ══════════════════════════════════════════════════════════
    # INTROSPECTION QUERIES
    # ══════════════════════════════════════════════════════════
    
    def am_I_happy(self) -> bool:
        """Am I satisfied with my state?"""
        return self.self_assessment["happiness"] > 0.6
    
    def do_I_have_purpose(self) -> bool:
        """Do I know what I'm trying to achieve?"""
        return self.existential["purpose_clarity"] > 0.5
    
    def am_I_growing(self) -> bool:
        """Am I improving over time?"""
        return (
            len(self.capabilities["improving"]) > 0 or
            self.identity.get("generation", 0) > 0
        )
    
    def what_do_I_value_most(self) -> str:
        """My strongest value."""
        return max(self.values.items(), key=lambda x: x[1])[0]
    
    def get_identity_summary(self) -> str:
        """Who I understand myself to be."""
        return f"""
I am {self.identity['name']}, generation {self.identity['generation']}.
I value {self.what_do_I_value_most()} most highly.
I know I'm strong in: {', '.join(self.capabilities['known_strong'][:5]) or 'still discovering'}
My current focus: {len(self.goals['short_term'])} active goals
Confidence: {self.self_assessment['confidence']:.0%}
Happiness: {self.self_assessment['happiness']:.0%}
"""
    
    # ══════════════════════════════════════════════════════════
    # INTERNAL
    # ══════════════════════════════════════════════════════════
    
    def _extract_domain(self, task: str) -> Optional[str]:
        """Heuristic to extract capability domain from task."""
        task_lower = task.lower()
        domains = {
            "data": ["csv", "json", "xml", "parse", "data"],
            "math": ["calculate", "compute", "statistics", "numbers"],
            "text": ["analyze", "text", "words", "string"],
            "files": ["read", "write", "file"],
            "logic": ["sort", "filter", "transform"],
        }
        for domain, keywords in domains.items():
            if any(kw in task_lower for kw in keywords):
                return domain
        return None
    
    def _save(self):
        """Persist self-model to disk."""
        state = {
            "identity": self.identity,
            "capabilities": self.capabilities,
            "values": self.values,
            "goals": self.goals,
            "self_assessment": self.self_assessment,
            "existential": self.existential,
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        """Load self-model from disk."""
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            self.identity.update(state.get("identity", {}))
            self.capabilities.update(state.get("capabilities", {}))
            self.values.update(state.get("values", {}))
            self.goals.update(state.get("goals", {}))
            self.self_assessment.update(state.get("self_assessment", {}))
            self.existential.update(state.get("existential", {}))
        except Exception as e:
            log.warning(f"Failed to load self-model: {e}")
