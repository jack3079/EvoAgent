"""
Dream System — Offline Memory Consolidation & Creative Synthesis

Based on neuroscience research on sleep and memory:
- Memory consolidation (hippocampus → cortex)
- Pattern extraction from experiences
- Creative recombination of concepts
- Emotional processing
- Problem incubation

When agent "sleeps", it:
- Replays experiences
- Extracts patterns
- Forms new associations
- Resolves emotional conflicts
- Generates novel insights
"""

import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

log = logging.getLogger(__name__)


class Dream:
    """A single dream episode."""
    
    def __init__(self, dream_type: str, content: dict):
        self.type = dream_type  # consolidation, creative, problem_solving, emotional
        self.content = content
        self.insights = []
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "content": self.content,
            "insights": self.insights,
            "timestamp": self.timestamp,
        }


class DreamSystem:
    """
    Offline learning through dream-like processing.
    
    Dreams serve multiple functions:
    1. Memory Consolidation - strengthen important memories
    2. Pattern Extraction - find common patterns across experiences
    3. Creative Synthesis - combine unrelated concepts
    4. Emotional Processing - resolve emotional conflicts
    5. Problem Incubation - unconscious problem-solving
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/dreams.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Dream journal
        self.dreams: List[Dream] = []
        self.total_sleep_cycles = 0
        
        # Sleep parameters
        self.rem_ratio = 0.25  # 25% of sleep is REM (dreaming)
        self.consolidation_threshold = 0.7  # Importance threshold for consolidation
        
        self._load()
        log.info("Dream system initialized")
    
    # ══════════════════════════════════════════════════════════
    # SLEEP CYCLE
    # ══════════════════════════════════════════════════════════
    
    def enter_sleep(
        self,
        experiences: List[dict],
        emotions: dict,
        knowledge_gaps: List[str],
        active_goals: List[dict]
    ) -> dict:
        """
        Agent enters sleep mode for memory consolidation.
        
        Args:
            experiences: Recent experiences from memory
            emotions: Current emotional state
            knowledge_gaps: Things agent knows it doesn't know
            active_goals: Current goals
        
        Returns:
            Sleep session results
        """
        log.info("Entering sleep cycle for memory consolidation")
        
        self.total_sleep_cycles += 1
        session = {
            "cycle": self.total_sleep_cycles,
            "started_at": datetime.utcnow().isoformat(),
            "dreams": [],
            "insights_gained": [],
            "patterns_discovered": [],
        }
        
        # ─── Phase 1: NREM Sleep (Memory Consolidation) ───────
        consolidation_dream = self._consolidate_memories(experiences)
        if consolidation_dream:
            session["dreams"].append(consolidation_dream.to_dict())
            session["insights_gained"].extend(consolidation_dream.insights)
        
        # ─── Phase 2: REM Sleep (Creative Dreaming) ───────────
        if random.random() < self.rem_ratio:
            creative_dream = self._creative_dreaming(experiences, knowledge_gaps)
            if creative_dream:
                session["dreams"].append(creative_dream.to_dict())
                session["insights_gained"].extend(creative_dream.insights)
        
        # ─── Phase 3: Emotional Processing ────────────────────
        if emotions.get("active_emotions"):
            emotional_dream = self._process_emotions(emotions, experiences)
            if emotional_dream:
                session["dreams"].append(emotional_dream.to_dict())
                session["insights_gained"].extend(emotional_dream.insights)
        
        # ─── Phase 4: Problem Incubation ──────────────────────
        if knowledge_gaps or active_goals:
            problem_dream = self._incubate_problems(knowledge_gaps, active_goals, experiences)
            if problem_dream:
                session["dreams"].append(problem_dream.to_dict())
                session["insights_gained"].extend(problem_dream.insights)
        
        session["ended_at"] = datetime.utcnow().isoformat()
        session["dreams_count"] = len(session["dreams"])
        
        self._save()
        
        log.info(f"Sleep cycle complete | {len(session['dreams'])} dreams | {len(session['insights_gained'])} insights")
        
        return session
    
    # ══════════════════════════════════════════════════════════
    # DREAM TYPES
    # ══════════════════════════════════════════════════════════
    
    def _consolidate_memories(self, experiences: List[dict]) -> Optional[Dream]:
        """
        Memory consolidation (NREM sleep).
        
        Strengthens important memories, weakens unimportant ones.
        Extracts patterns across experiences.
        """
        if not experiences:
            return None
        
        # Score memories by importance
        important = [
            exp for exp in experiences
            if exp.get("success") or exp.get("learned")
        ]
        
        if not important:
            important = experiences[:3]  # At least consolidate recent
        
        # Extract patterns
        patterns = self._extract_patterns(important)
        
        # Create consolidation dream
        dream = Dream(
            dream_type="consolidation",
            content={
                "memories_processed": len(experiences),
                "memories_consolidated": len(important),
                "patterns": patterns,
            }
        )
        
        # Insights from patterns
        for pattern in patterns:
            dream.insights.append({
                "type": "pattern",
                "insight": f"Pattern discovered: {pattern}",
                "confidence": 0.7,
            })
        
        self.dreams.append(dream)
        return dream
    
    def _creative_dreaming(
        self,
        experiences: List[dict],
        knowledge_gaps: List[str]
    ) -> Optional[Dream]:
        """
        Creative synthesis (REM sleep).
        
        Combines unrelated concepts to generate novel ideas.
        "What if X could be used for Y?"
        """
        if len(experiences) < 2:
            return None
        
        # Random recombination of experiences
        sample_size = min(3, len(experiences))
        sampled = random.sample(experiences, sample_size)
        
        # Extract concepts
        concepts = []
        for exp in sampled:
            task = exp.get("task", "")
            if task:
                concepts.append(task.split()[0] if task.split() else "")
        
        # Generate creative combinations
        novel_ideas = []
        if len(concepts) >= 2:
            for i in range(len(concepts)):
                for j in range(i+1, len(concepts)):
                    if concepts[i] and concepts[j]:
                        novel_ideas.append(
                            f"What if {concepts[i]} could enhance {concepts[j]}?"
                        )
        
        dream = Dream(
            dream_type="creative",
            content={
                "concepts_combined": concepts,
                "novel_ideas": novel_ideas,
                "synthesis_count": len(novel_ideas),
            }
        )
        
        # Creative insights
        for idea in novel_ideas[:2]:  # Top 2
            dream.insights.append({
                "type": "creative",
                "insight": idea,
                "confidence": 0.5,  # Creative ideas are speculative
            })
        
        self.dreams.append(dream)
        return dream
    
    def _process_emotions(
        self,
        emotions: dict,
        experiences: List[dict]
    ) -> Optional[Dream]:
        """
        Emotional processing (REM sleep).
        
        Resolves emotional conflicts, reduces intensity of negative emotions.
        """
        active = emotions.get("active_emotions", [])
        if not active:
            return None
        
        # Find emotionally charged experiences
        emotional_experiences = [
            exp for exp in experiences
            if not exp.get("success") or exp.get("challenge_level", 0) > 0.7
        ]
        
        # Process each active emotion
        processed = []
        for emotion in active:
            emotion_name = emotion.get("name", "")
            intensity = emotion.get("intensity", 0)
            
            if intensity > 0.5:
                # High intensity emotions need processing
                processed.append({
                    "emotion": emotion_name,
                    "initial_intensity": intensity,
                    "processed_intensity": intensity * 0.7,  # Reduce by 30%
                    "mechanism": "emotional dream processing"
                })
        
        dream = Dream(
            dream_type="emotional",
            content={
                "emotions_processed": processed,
                "emotional_experiences_reviewed": len(emotional_experiences),
            }
        )
        
        # Emotional insights
        for proc in processed:
            dream.insights.append({
                "type": "emotional",
                "insight": f"Processed {proc['emotion']} emotion, reduced intensity",
                "confidence": 0.8,
            })
        
        self.dreams.append(dream)
        return dream
    
    def _incubate_problems(
        self,
        knowledge_gaps: List[str],
        active_goals: List[dict],
        experiences: List[dict]
    ) -> Optional[Dream]:
        """
        Problem incubation (REM sleep).
        
        "Sleep on it" - unconscious problem-solving.
        Makes unexpected connections that solve problems.
        """
        if not knowledge_gaps and not active_goals:
            return None
        
        # Select a problem to incubate
        problem = None
        if knowledge_gaps:
            problem = random.choice(knowledge_gaps)
        elif active_goals:
            problem = active_goals[0].get("goal", "")
        
        if not problem:
            return None
        
        # Find related experiences
        problem_words = set(problem.lower().split())
        related = [
            exp for exp in experiences
            if any(word in str(exp).lower() for word in problem_words)
        ]
        
        # Generate potential solution paths
        solution_paths = []
        if related:
            for exp in related[:2]:
                if exp.get("success"):
                    solution_paths.append(
                        f"Apply strategy from '{exp.get('task', '')}' to this problem"
                    )
        
        # Add creative leap
        solution_paths.append(
            f"Try approaching from completely different angle"
        )
        
        dream = Dream(
            dream_type="problem_solving",
            content={
                "problem": problem,
                "related_experiences": len(related),
                "solution_paths": solution_paths,
            }
        )
        
        # Problem-solving insights
        for path in solution_paths[:2]:
            dream.insights.append({
                "type": "problem_solving",
                "insight": path,
                "confidence": 0.6,
            })
        
        self.dreams.append(dream)
        return dream
    
    # ══════════════════════════════════════════════════════════
    # PATTERN EXTRACTION
    # ══════════════════════════════════════════════════════════
    
    def _extract_patterns(self, experiences: List[dict]) -> List[str]:
        """
        Find common patterns across experiences.
        
        This is simplified - real system would use clustering, etc.
        """
        patterns = []
        
        # Pattern 1: Success conditions
        successes = [e for e in experiences if e.get("success")]
        if len(successes) >= 2:
            # Find commonalities
            common_learned = set()
            for exp in successes:
                learned = exp.get("learned", [])
                common_learned.update(learned)
            
            if common_learned:
                patterns.append(f"Success often involves: {', '.join(list(common_learned)[:3])}")
        
        # Pattern 2: Failure conditions
        failures = [e for e in experiences if not e.get("success")]
        if len(failures) >= 2:
            patterns.append("Multiple failures detected - may need new approach")
        
        # Pattern 3: Task types
        tasks = [e.get("task", "") for e in experiences if e.get("task")]
        if tasks:
            # Simple clustering by first word
            from collections import Counter
            first_words = [t.split()[0] for t in tasks if t.split()]
            common = Counter(first_words).most_common(1)
            if common:
                patterns.append(f"Frequently working on: {common[0][0]}-related tasks")
        
        return patterns
    
    # ══════════════════════════════════════════════════════════
    # UTILITIES
    # ══════════════════════════════════════════════════════════
    
    def get_dream_summary(self, last_n: int = 5) -> str:
        """Narrative summary of recent dreams."""
        recent = self.dreams[-last_n:] if self.dreams else []
        
        if not recent:
            return "No dreams recorded yet"
        
        lines = [f"Recent Dreams (last {len(recent)} sleep cycles):"]
        
        for i, dream in enumerate(recent, 1):
            lines.append(f"\n{i}. {dream.type.upper()} Dream:")
            
            if dream.type == "consolidation":
                memories = dream.content.get("memories_consolidated", 0)
                patterns = dream.content.get("patterns", [])
                lines.append(f"   Consolidated {memories} memories")
                if patterns:
                    lines.append(f"   Patterns: {patterns[0]}")
            
            elif dream.type == "creative":
                ideas = dream.content.get("novel_ideas", [])
                if ideas:
                    lines.append(f"   Novel idea: {ideas[0]}")
            
            elif dream.type == "emotional":
                processed = dream.content.get("emotions_processed", [])
                if processed:
                    lines.append(f"   Processed {len(processed)} emotions")
            
            elif dream.type == "problem_solving":
                problem = dream.content.get("problem", "")
                lines.append(f"   Incubated: {problem[:60]}")
        
        return "\n".join(lines)
    
    def get_consolidated_insights(self) -> List[dict]:
        """All insights from all dreams."""
        all_insights = []
        for dream in self.dreams:
            all_insights.extend(dream.insights)
        return all_insights
    
    def get_status(self) -> dict:
        """Dream system statistics."""
        return {
            "total_sleep_cycles": self.total_sleep_cycles,
            "total_dreams": len(self.dreams),
            "dream_types": {
                "consolidation": len([d for d in self.dreams if d.type == "consolidation"]),
                "creative": len([d for d in self.dreams if d.type == "creative"]),
                "emotional": len([d for d in self.dreams if d.type == "emotional"]),
                "problem_solving": len([d for d in self.dreams if d.type == "problem_solving"]),
            },
            "total_insights": sum(len(d.insights) for d in self.dreams),
        }
    
    # ══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _save(self):
        state = {
            "total_sleep_cycles": self.total_sleep_cycles,
            "dreams": [d.to_dict() for d in self.dreams[-50:]],  # Keep last 50
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            self.total_sleep_cycles = state.get("total_sleep_cycles", 0)
            # Would reconstruct dreams, keeping simple for now
        except Exception as e:
            log.warning(f"Failed to load dreams: {e}")
