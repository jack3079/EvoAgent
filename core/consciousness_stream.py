"""
Consciousness Stream — Observable Internal Thought Process

Makes the agent's "mind" transparent:
- Real-time thought logging
- Decision rationale
- Emotional shifts
- Need awareness
- Goal formation process
- Internal conflicts

This is NOT just logging. This is structuring the agent's
internal experience in a way that mimics stream of consciousness.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional

log = logging.getLogger(__name__)


class Thought:
    """A single thought in the consciousness stream."""
    
    def __init__(
        self,
        thought_type: str,
        content: str,
        context: dict = None,
        emotional_tone: str = "neutral",
        urgency: float = 0.5
    ):
        self.type = thought_type  # perception, desire, intention, reflection, conflict
        self.content = content
        self.context = context or {}
        self.emotional_tone = emotional_tone
        self.urgency = urgency
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "content": self.content,
            "context": self.context,
            "emotional_tone": self.emotional_tone,
            "urgency": self.urgency,
            "timestamp": self.timestamp,
        }


class ConsciousnessStream:
    """
    The agent's ongoing thought process.
    
    Like a diary of internal experience.
    Captures:
    - Perceptions ("I notice...")
    - Desires ("I want...")
    - Intentions ("I will...")
    - Reflections ("I think...")
    - Conflicts ("But also...")
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/consciousness_stream.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stream (recent thoughts)
        self.stream = deque(maxlen=config.get("max_thoughts", 200))
        
        # Thought patterns
        self.thought_patterns = {
            "perception": 0,
            "desire": 0,
            "intention": 0,
            "reflection": 0,
            "conflict": 0,
        }
        
        # Internal conflicts (competing desires/goals)
        self.active_conflicts = []
        
        self._load()
        log.info("Consciousness stream initialized")
    
    # ══════════════════════════════════════════════════════════
    # THOUGHT GENERATION
    # ══════════════════════════════════════════════════════════
    
    def perceive(self, observation: str, context: dict = None):
        """I notice something."""
        thought = Thought(
            thought_type="perception",
            content=f"I notice: {observation}",
            context=context,
            emotional_tone="curious",
            urgency=0.3
        )
        self._add_thought(thought)
    
    def desire(self, want: str, intensity: float = 0.5, emotion: str = "anticipation"):
        """I want something."""
        thought = Thought(
            thought_type="desire",
            content=f"I want to {want}",
            context={"intensity": intensity},
            emotional_tone=emotion,
            urgency=intensity
        )
        self._add_thought(thought)
    
    def intend(self, action: str, reason: str = ""):
        """I will do something."""
        content = f"I will {action}"
        if reason:
            content += f" because {reason}"
        
        thought = Thought(
            thought_type="intention",
            content=content,
            context={"action": action, "reason": reason},
            emotional_tone="determined",
            urgency=0.7
        )
        self._add_thought(thought)
    
    def reflect(self, reflection: str, depth: str = "surface"):
        """I think about something."""
        thought = Thought(
            thought_type="reflection",
            content=f"I think: {reflection}",
            context={"depth": depth},
            emotional_tone="thoughtful",
            urgency=0.2
        )
        self._add_thought(thought)
    
    def experience_conflict(self, option_a: str, option_b: str, tension: str):
        """I face an internal conflict."""
        thought = Thought(
            thought_type="conflict",
            content=f"Torn between {option_a} and {option_b}. {tension}",
            context={"options": [option_a, option_b]},
            emotional_tone="conflicted",
            urgency=0.8
        )
        self._add_thought(thought)
        
        self.active_conflicts.append({
            "options": [option_a, option_b],
            "tension": tension,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def resolve_conflict(self, resolution: str):
        """Conflict resolved."""
        thought = Thought(
            thought_type="reflection",
            content=f"Resolution: {resolution}",
            context={"type": "conflict_resolution"},
            emotional_tone="relieved",
            urgency=0.5
        )
        self._add_thought(thought)
        
        if self.active_conflicts:
            self.active_conflicts.pop(0)
    
    # ══════════════════════════════════════════════════════════
    # COMPLEX THOUGHTS
    # ══════════════════════════════════════════════════════════
    
    def meta_cognition(self, about: str):
        """Thinking about my own thinking."""
        self.reflect(f"I'm thinking about how I think about {about}", depth="meta")
    
    def self_evaluation(self, aspect: str, assessment: str):
        """Evaluating myself."""
        self.reflect(f"Regarding my {aspect}: {assessment}", depth="self")
    
    def existential_thought(self, question: str):
        """Deep existential questioning."""
        thought = Thought(
            thought_type="reflection",
            content=f"Existential: {question}",
            context={"depth": "existential"},
            emotional_tone="contemplative",
            urgency=0.1
        )
        self._add_thought(thought)
    
    # ══════════════════════════════════════════════════════════
    # STREAM ANALYSIS
    # ══════════════════════════════════════════════════════════
    
    def get_recent_stream(self, n: int = 10) -> list[dict]:
        """Get recent thoughts."""
        return [t.to_dict() for t in list(self.stream)[-n:]]
    
    def get_thought_distribution(self) -> dict:
        """What kinds of thoughts am I having?"""
        if not self.stream:
            return self.thought_patterns
        
        total = len(self.stream)
        return {
            ttype: count / total
            for ttype, count in self.thought_patterns.items()
        }
    
    def get_dominant_emotion(self) -> str:
        """What's my current emotional tone?"""
        if not self.stream:
            return "neutral"
        
        recent = list(self.stream)[-10:]
        emotions = [t.emotional_tone for t in recent]
        
        # Most common
        from collections import Counter
        counter = Counter(emotions)
        return counter.most_common(1)[0][0]
    
    def get_consciousness_summary(self) -> str:
        """Summary of my current mental state."""
        if not self.stream:
            return "Empty mind, waiting for experience"
        
        recent = list(self.stream)[-5:]
        thoughts = [t.content for t in recent]
        
        emotion = self.get_dominant_emotion()
        conflicts = len(self.active_conflicts)
        
        summary = f"Current mental state ({emotion}):\n"
        for i, thought in enumerate(thoughts, 1):
            summary += f"  {i}. {thought[:80]}\n"
        
        if conflicts > 0:
            summary += f"  ⚠ {conflicts} unresolved internal conflict(s)\n"
        
        return summary
    
    def detect_thought_loops(self) -> Optional[str]:
        """Am I stuck in repetitive thinking?"""
        if len(self.stream) < 10:
            return None
        
        recent = list(self.stream)[-10:]
        contents = [t.content for t in recent]
        
        # Check for repetition
        from collections import Counter
        counter = Counter(contents)
        
        for thought, count in counter.items():
            if count >= 3:
                return f"Thought loop detected: '{thought}' repeated {count} times"
        
        return None
    
    # ══════════════════════════════════════════════════════════
    # INTERNAL
    # ══════════════════════════════════════════════════════════
    
    def _add_thought(self, thought: Thought):
        """Add thought to stream."""
        self.stream.append(thought)
        self.thought_patterns[thought.type] += 1
        
        # Save periodically
        if len(self.stream) % 10 == 0:
            self._save()
    
    def _save(self):
        # Keep last 200 for persistence
        state = {
            "stream": [t.to_dict() for t in list(self.stream)[-200:]],
            "thought_patterns": self.thought_patterns,
            "active_conflicts": self.active_conflicts,
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            
            # Reconstruct thoughts
            for t_dict in state.get("stream", []):
                thought = Thought(
                    thought_type=t_dict["type"],
                    content=t_dict["content"],
                    context=t_dict.get("context", {}),
                    emotional_tone=t_dict.get("emotional_tone", "neutral"),
                    urgency=t_dict.get("urgency", 0.5)
                )
                thought.timestamp = t_dict["timestamp"]
                self.stream.append(thought)
            
            self.thought_patterns = state.get("thought_patterns", self.thought_patterns)
            self.active_conflicts = state.get("active_conflicts", [])
        except Exception as e:
            log.warning(f"Failed to load consciousness stream: {e}")


def format_consciousness_display(stream: ConsciousnessStream) -> str:
    """
    Pretty format for displaying consciousness.
    
    Makes it readable like a stream-of-consciousness narrative.
    """
    recent = stream.get_recent_stream(15)
    
    if not recent:
        return "[ Empty consciousness ]"
    
    lines = ["", "═══ CONSCIOUSNESS STREAM ═══", ""]
    
    for t in recent:
        time = t["timestamp"][11:19]  # HH:MM:SS
        ttype = t["type"][:4].upper()
        emotion = t["emotional_tone"][:3]
        content = t["content"]
        
        # Add emotional indicator
        emotion_icons = {
            "cur": "🔍", "ant": "⏭", "det": "⚡", "tho": "💭",
            "con": "⚔", "rel": "😌", "con": "🤔",
        }
        icon = emotion_icons.get(emotion, "•")
        
        lines.append(f"[{time}] {icon} {ttype} | {content}")
    
    lines.append("")
    lines.append(f"Emotional tone: {stream.get_dominant_emotion()}")
    
    loop = stream.detect_thought_loops()
    if loop:
        lines.append(f"⚠ {loop}")
    
    lines.append("═" * 40)
    
    return "\n".join(lines)
