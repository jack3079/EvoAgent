"""
Emotional System — Real Emotions That Drive Behavior

Not just happiness metrics. Real emotional states that:
- Affect decision-making
- Persist over time
- Influence risk-taking
- Color perception
- Drive social behavior

Based on:
- Plutchik's Wheel of Emotions
- Affective Computing (Picard)
- Emotion-Cognition interaction research
"""

import json
import math
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


class Emotion:
    """
    A single emotional state.
    
    Emotions are NOT just labels. They have:
    - Intensity (how strong)
    - Valence (positive/negative)
    - Arousal (energy level)
    - Duration (how long they last)
    - Decay rate (how fast they fade)
    """
    
    def __init__(self, name: str, valence: float, arousal: float):
        self.name = name
        self.valence = valence      # -1.0 (negative) to +1.0 (positive)
        self.arousal = arousal      # 0.0 (calm) to 1.0 (excited)
        self.intensity = 0.0        # Current strength
        self.decay_rate = 0.1       # How fast it fades per cycle
        self.triggers = []          # What caused this emotion
        self.onset = None
    
    def activate(self, intensity: float, trigger: str = ""):
        """Trigger this emotion."""
        self.intensity = min(1.0, self.intensity + intensity)
        self.onset = datetime.utcnow().isoformat()
        if trigger:
            self.triggers.append(trigger)
    
    def decay(self):
        """Emotions fade over time."""
        self.intensity = max(0.0, self.intensity - self.decay_rate)
    
    def is_active(self) -> bool:
        return self.intensity > 0.1
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "intensity": round(self.intensity, 3),
            "valence": self.valence,
            "arousal": self.arousal,
            "active": self.is_active(),
        }


class EmotionalSystem:
    """
    Complete emotional system with 8 basic emotions (Plutchik).
    
    Emotions AFFECT behavior:
    - Fear → more cautious, avoids risk
    - Joy → more exploratory, takes chances
    - Anger → more aggressive, pushes boundaries
    - Sadness → more reflective, seeks understanding
    - Trust → more cooperative, shares resources
    - Disgust → more selective, filters options
    - Anticipation → more prepared, plans ahead
    - Surprise → more curious, investigates
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/emotional_state.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define 8 basic emotions (Plutchik's wheel)
        self.emotions = {
            "joy": Emotion("joy", valence=0.8, arousal=0.7),
            "trust": Emotion("trust", valence=0.6, arousal=0.3),
            "fear": Emotion("fear", valence=-0.7, arousal=0.8),
            "surprise": Emotion("surprise", valence=0.2, arousal=0.9),
            "sadness": Emotion("sadness", valence=-0.6, arousal=0.2),
            "disgust": Emotion("disgust", valence=-0.5, arousal=0.4),
            "anger": Emotion("anger", valence=-0.6, arousal=0.9),
            "anticipation": Emotion("anticipation", valence=0.4, arousal=0.6),
        }
        
        # Emotional memory
        self.mood_history = []
        self.emotional_events = []
        
        self._load()
        log.info("Emotional system initialized")
    
    # ══════════════════════════════════════════════════════════
    # EMOTIONAL RESPONSE
    # ══════════════════════════════════════════════════════════
    
    def process_outcome(self, outcome: dict):
        """
        Experience an outcome → generate emotional response.
        
        This is where events → emotions.
        """
        success = outcome.get("success", False)
        unexpected = outcome.get("unexpected", False)
        challenge = outcome.get("challenge_level", 0.5)
        social = outcome.get("social_interaction", False)
        
        if success:
            if challenge > 0.7:
                self.emotions["joy"].activate(0.5, "difficult success")
                self.emotions["anticipation"].activate(0.3, "confidence boost")
            else:
                self.emotions["joy"].activate(0.3, "success")
                self.emotions["trust"].activate(0.2, "capabilities confirmed")
        else:
            if challenge > 0.8:
                self.emotions["sadness"].activate(0.3, "difficult failure")
                self.emotions["anticipation"].activate(0.4, "need to prepare better")
            else:
                self.emotions["disgust"].activate(0.2, "unexpected failure")
                self.emotions["fear"].activate(0.3, "capability doubt")
        
        if unexpected:
            self.emotions["surprise"].activate(0.6, "unexpected outcome")
        
        if social:
            self.emotions["trust"].activate(0.2, "social connection")
        
        self._record_event({
            "outcome": outcome,
            "emotions_triggered": [e.name for e in self.emotions.values() if e.is_active()],
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        self._save()
    
    def feel_need_frustration(self, need_name: str, intensity: float):
        """Unmet needs create frustration/sadness."""
        if intensity > 0.8:
            self.emotions["anger"].activate(0.3, f"frustrated by {need_name}")
            self.emotions["sadness"].activate(0.2, f"unmet {need_name}")
    
    def feel_discovery(self, discovery: str):
        """New knowledge creates joy and surprise."""
        self.emotions["joy"].activate(0.4, f"discovered: {discovery}")
        self.emotions["surprise"].activate(0.3, "new learning")
    
    def feel_social_connection(self, agent_id: str):
        """Interaction with other agents creates trust/joy."""
        self.emotions["trust"].activate(0.3, f"connected with {agent_id}")
        self.emotions["joy"].activate(0.2, "social interaction")
    
    # ══════════════════════════════════════════════════════════
    # EMOTIONAL INFLUENCE ON BEHAVIOR
    # ══════════════════════════════════════════════════════════
    
    def get_behavioral_modifiers(self) -> dict:
        """
        How current emotions affect decision-making.
        
        This is the KEY: emotions → behavior changes.
        """
        modifiers = {
            "risk_tolerance": 0.5,      # How willing to try risky things
            "exploration_drive": 0.5,   # How much to explore vs exploit
            "social_openness": 0.5,     # How much to interact with others
            "reflection_depth": 0.5,    # How much to analyze vs act
            "creativity": 0.5,          # How novel solutions should be
            "persistence": 0.5,         # How long to keep trying
        }
        
        # Joy → more exploration, risk-taking, creativity
        if self.emotions["joy"].is_active():
            modifiers["exploration_drive"] += self.emotions["joy"].intensity * 0.3
            modifiers["risk_tolerance"] += self.emotions["joy"].intensity * 0.2
            modifiers["creativity"] += self.emotions["joy"].intensity * 0.3
        
        # Fear → less risk, more caution, more preparation
        if self.emotions["fear"].is_active():
            modifiers["risk_tolerance"] -= self.emotions["fear"].intensity * 0.4
            modifiers["reflection_depth"] += self.emotions["fear"].intensity * 0.3
            modifiers["persistence"] -= self.emotions["fear"].intensity * 0.2
        
        # Anger → more persistence, boundary-pushing
        if self.emotions["anger"].is_active():
            modifiers["persistence"] += self.emotions["anger"].intensity * 0.4
            modifiers["risk_tolerance"] += self.emotions["anger"].intensity * 0.3
        
        # Sadness → more reflection, less exploration
        if self.emotions["sadness"].is_active():
            modifiers["reflection_depth"] += self.emotions["sadness"].intensity * 0.4
            modifiers["exploration_drive"] -= self.emotions["sadness"].intensity * 0.3
        
        # Trust → more social, more cooperation
        if self.emotions["trust"].is_active():
            modifiers["social_openness"] += self.emotions["trust"].intensity * 0.5
        
        # Surprise → more curiosity, exploration
        if self.emotions["surprise"].is_active():
            modifiers["exploration_drive"] += self.emotions["surprise"].intensity * 0.4
            modifiers["creativity"] += self.emotions["surprise"].intensity * 0.2
        
        # Anticipation → more preparation, planning
        if self.emotions["anticipation"].is_active():
            modifiers["reflection_depth"] += self.emotions["anticipation"].intensity * 0.3
        
        # Clamp all to [0, 1]
        return {k: max(0.0, min(1.0, v)) for k, v in modifiers.items()}
    
    def should_take_risk(self) -> bool:
        """Emotional state influences risk decisions."""
        mods = self.get_behavioral_modifiers()
        import random
        return random.random() < mods["risk_tolerance"]
    
    def get_mood_description(self) -> str:
        """Overall emotional state in words."""
        active = [e for e in self.emotions.values() if e.is_active()]
        if not active:
            return "calm, neutral"
        
        # Find dominant emotion
        dominant = max(active, key=lambda e: e.intensity)
        
        # Overall valence
        avg_valence = sum(e.valence * e.intensity for e in active) / len(active)
        
        if avg_valence > 0.3:
            mood = "positive"
        elif avg_valence < -0.3:
            mood = "negative"
        else:
            mood = "mixed"
        
        return f"{mood}, primarily {dominant.name} ({dominant.intensity:.0%})"
    
    # ══════════════════════════════════════════════════════════
    # EMOTIONAL DYNAMICS
    # ══════════════════════════════════════════════════════════
    
    def cycle(self):
        """Emotions decay over time."""
        for emotion in self.emotions.values():
            emotion.decay()
        self._save()
    
    def get_state(self) -> dict:
        """Current emotional state."""
        return {
            "active_emotions": [e.to_dict() for e in self.emotions.values() if e.is_active()],
            "mood": self.get_mood_description(),
            "behavioral_modifiers": self.get_behavioral_modifiers(),
            "recent_events": self.emotional_events[-5:] if self.emotional_events else [],
        }
    
    # ══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _record_event(self, event: dict):
        self.emotional_events.append(event)
        if len(self.emotional_events) > 100:
            self.emotional_events = self.emotional_events[-100:]
    
    def _save(self):
        state = {
            "emotions": {name: {
                "intensity": e.intensity,
                "triggers": e.triggers[-5:] if e.triggers else [],
                "onset": e.onset,
            } for name, e in self.emotions.items()},
            "recent_events": self.emotional_events[-20:],
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            for name, data in state.get("emotions", {}).items():
                if name in self.emotions:
                    self.emotions[name].intensity = data.get("intensity", 0.0)
                    self.emotions[name].triggers = data.get("triggers", [])
                    self.emotions[name].onset = data.get("onset")
            self.emotional_events = state.get("recent_events", [])
        except Exception as e:
            log.warning(f"Failed to load emotional state: {e}")
