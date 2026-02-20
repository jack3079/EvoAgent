"""
Meta-Learning Engine — Learning How to Learn

The agent doesn't just learn facts. It learns:
- Which learning strategies work best
- How to optimize its own learning process
- When to explore vs exploit
- How much to trust different information sources
- Which memories to prioritize

This is "learning to learn" - the hallmark of advanced intelligence.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional, List

log = logging.getLogger(__name__)


class LearningStrategy:
    """A strategy for learning."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.success_rate = 0.5  # Initially neutral
        self.times_used = 0
        self.recent_outcomes = []  # Last 10 outcomes
    
    def record_outcome(self, success: bool):
        """Update strategy effectiveness."""
        self.times_used += 1
        self.recent_outcomes.append(success)
        if len(self.recent_outcomes) > 10:
            self.recent_outcomes = self.recent_outcomes[-10:]
        
        # Update success rate (exponential moving average)
        alpha = 0.2
        self.success_rate = (
            alpha * (1.0 if success else 0.0) +
            (1 - alpha) * self.success_rate
        )
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "success_rate": round(self.success_rate, 3),
            "times_used": self.times_used,
        }


class MetaLearningEngine:
    """
    Learns how to learn more effectively.
    
    Tracks:
    - Which learning strategies work
    - Optimal learning rate for different tasks
    - When to ask for help vs figure it out
    - Information source reliability
    - Memory retention patterns
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/meta_learning.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Learning strategies
        self.strategies = self._initialize_strategies()
        
        # Learning parameters (self-tuned)
        self.learning_rate = 0.3  # How quickly to update beliefs
        self.exploration_rate = 0.2  # How often to try new strategies
        self.memory_threshold = 0.6  # Importance threshold for memory
        
        # Source reliability tracking
        self.source_reliability = defaultdict(lambda: 0.5)
        
        # Meta-learning history
        self.adaptations = []
        
        self._load()
        log.info("Meta-learning engine initialized")
    
    # ══════════════════════════════════════════════════════════
    # STRATEGY SELECTION
    # ══════════════════════════════════════════════════════════
    
    def select_learning_strategy(
        self,
        task_context: dict,
        current_knowledge: float = 0.5
    ) -> LearningStrategy:
        """
        Choose best learning strategy for current situation.
        
        This is meta-learning: picking HOW to learn based on context.
        """
        # Exploration vs exploitation
        import random
        if random.random() < self.exploration_rate:
            # Try random strategy (exploration)
            return random.choice(list(self.strategies.values()))
        
        # Exploit: use best strategy
        # Filter relevant strategies
        if current_knowledge < 0.3:
            # Low knowledge → use foundational strategies
            relevant = [s for s in self.strategies.values() 
                       if "basic" in s.name or "explore" in s.name]
        elif current_knowledge > 0.7:
            # High knowledge → use advanced strategies
            relevant = [s for s in self.strategies.values()
                       if "refine" in s.name or "optimize" in s.name]
        else:
            # Medium knowledge → use all strategies
            relevant = list(self.strategies.values())
        
        if not relevant:
            relevant = list(self.strategies.values())
        
        # Pick best
        best = max(relevant, key=lambda s: s.success_rate)
        return best
    
    def record_strategy_outcome(
        self,
        strategy: LearningStrategy,
        success: bool,
        task_context: dict
    ):
        """Update strategy effectiveness."""
        strategy.record_outcome(success)
        
        # Meta-adaptation: adjust parameters
        self._adapt_parameters(strategy, success, task_context)
        
        self._save()
    
    # ══════════════════════════════════════════════════════════
    # PARAMETER ADAPTATION
    # ══════════════════════════════════════════════════════════
    
    def _adapt_parameters(
        self,
        strategy: LearningStrategy,
        success: bool,
        context: dict
    ):
        """
        Adjust meta-learning parameters based on outcomes.
        
        This is learning to learn: adjusting HOW you learn.
        """
        adaptations_made = []
        
        # 1. Adapt learning rate
        if strategy.times_used > 5:
            if strategy.success_rate > 0.7:
                # High success → can learn faster
                old_lr = self.learning_rate
                self.learning_rate = min(0.5, self.learning_rate * 1.1)
                if self.learning_rate != old_lr:
                    adaptations_made.append(
                        f"Increased learning rate: {old_lr:.2f} → {self.learning_rate:.2f}"
                    )
            elif strategy.success_rate < 0.3:
                # Low success → learn more cautiously
                old_lr = self.learning_rate
                self.learning_rate = max(0.1, self.learning_rate * 0.9)
                if self.learning_rate != old_lr:
                    adaptations_made.append(
                        f"Decreased learning rate: {old_lr:.2f} → {self.learning_rate:.2f}"
                    )
        
        # 2. Adapt exploration rate
        # If consistently successful, explore less
        recent_success_rate = sum(strategy.recent_outcomes) / max(1, len(strategy.recent_outcomes))
        if recent_success_rate > 0.8:
            old_er = self.exploration_rate
            self.exploration_rate = max(0.05, self.exploration_rate * 0.9)
            if self.exploration_rate != old_er:
                adaptations_made.append(
                    f"Reduced exploration: {old_er:.2f} → {self.exploration_rate:.2f}"
                )
        elif recent_success_rate < 0.3:
            # Need more exploration
            old_er = self.exploration_rate
            self.exploration_rate = min(0.4, self.exploration_rate * 1.1)
            if self.exploration_rate != old_er:
                adaptations_made.append(
                    f"Increased exploration: {old_er:.2f} → {self.exploration_rate:.2f}"
                )
        
        # 3. Adapt memory threshold
        # If learning well, can be more selective about what to remember
        if strategy.success_rate > 0.7:
            old_mt = self.memory_threshold
            self.memory_threshold = min(0.8, self.memory_threshold * 1.05)
            if self.memory_threshold != old_mt:
                adaptations_made.append(
                    f"Raised memory threshold: {old_mt:.2f} → {self.memory_threshold:.2f}"
                )
        
        # Record adaptations
        if adaptations_made:
            self.adaptations.append({
                "timestamp": datetime.utcnow().isoformat(),
                "trigger": f"{strategy.name} ({strategy.success_rate:.2f})",
                "adaptations": adaptations_made,
            })
            log.info(f"Meta-learning adaptation: {', '.join(adaptations_made)}")
    
    # ══════════════════════════════════════════════════════════
    # SOURCE RELIABILITY
    # ══════════════════════════════════════════════════════════
    
    def update_source_reliability(self, source: str, was_correct: bool):
        """
        Track which information sources are reliable.
        
        Meta-learning: know who to trust.
        """
        # Exponential moving average
        alpha = 0.2
        current = self.source_reliability[source]
        self.source_reliability[source] = (
            alpha * (1.0 if was_correct else 0.0) +
            (1 - alpha) * current
        )
        
        self._save()
    
    def get_source_reliability(self, source: str) -> float:
        """How much to trust this source."""
        return self.source_reliability.get(source, 0.5)
    
    def should_trust_source(self, source: str) -> bool:
        """Binary decision: trust or not."""
        return self.get_source_reliability(source) > 0.6
    
    # ══════════════════════════════════════════════════════════
    # LEARNING OPTIMIZATION
    # ══════════════════════════════════════════════════════════
    
    def should_remember(self, experience: dict) -> bool:
        """
        Meta-learning: decide what's worth remembering.
        
        Not everything needs to be stored.
        """
        importance = 0.0
        
        # Success is important
        if experience.get("success"):
            importance += 0.3
        
        # Learning is important
        if experience.get("learned"):
            importance += 0.4
        
        # Novel situations are important
        if experience.get("novelty", 0) > 0.7:
            importance += 0.3
        
        # Emotional salience is important
        if experience.get("emotional_intensity", 0) > 0.7:
            importance += 0.2
        
        return importance >= self.memory_threshold
    
    def optimize_learning_schedule(self, recent_performance: List[float]) -> dict:
        """
        Adjust when and how to learn based on performance.
        
        Meta-learning: optimal timing and intensity.
        """
        if len(recent_performance) < 5:
            return {"recommendation": "continue_current_schedule"}
        
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        if avg_performance > 0.8:
            return {
                "recommendation": "increase_challenge",
                "rationale": "High performance indicates readiness for harder tasks"
            }
        elif avg_performance < 0.4:
            return {
                "recommendation": "consolidate",
                "rationale": "Low performance indicates need for review and consolidation"
            }
        else:
            return {
                "recommendation": "maintain",
                "rationale": "Performance is in optimal learning zone"
            }
    
    # ══════════════════════════════════════════════════════════
    # STRATEGIES
    # ══════════════════════════════════════════════════════════
    
    def _initialize_strategies(self) -> dict:
        """Define available learning strategies."""
        strategies = {
            "explore_then_exploit": LearningStrategy(
                "explore_then_exploit",
                "Try multiple approaches, then focus on best one"
            ),
            "learn_by_doing": LearningStrategy(
                "learn_by_doing",
                "Practice repeatedly until proficient"
            ),
            "learn_from_others": LearningStrategy(
                "learn_from_others",
                "Observe and imitate successful agents"
            ),
            "reflect_deeply": LearningStrategy(
                "reflect_deeply",
                "Analyze failures thoroughly before trying again"
            ),
            "incremental_progress": LearningStrategy(
                "incremental_progress",
                "Break complex tasks into small steps"
            ),
            "creative_experimentation": LearningStrategy(
                "creative_experimentation",
                "Try unconventional approaches"
            ),
        }
        return strategies
    
    # ══════════════════════════════════════════════════════════
    # STATUS & REPORTING
    # ══════════════════════════════════════════════════════════
    
    def get_meta_learning_status(self) -> dict:
        """Current meta-learning state."""
        return {
            "learning_rate": round(self.learning_rate, 3),
            "exploration_rate": round(self.exploration_rate, 3),
            "memory_threshold": round(self.memory_threshold, 3),
            "strategy_performance": {
                name: s.to_dict()
                for name, s in self.strategies.items()
            },
            "best_strategy": max(
                self.strategies.values(),
                key=lambda s: s.success_rate
            ).name,
            "adaptations_made": len(self.adaptations),
            "recent_adaptations": self.adaptations[-3:] if self.adaptations else [],
        }
    
    def get_learning_insights(self) -> List[str]:
        """Insights about how the agent learns."""
        insights = []
        
        # Best strategy
        best = max(self.strategies.values(), key=lambda s: s.success_rate)
        insights.append(
            f"Most effective learning strategy: {best.name} ({best.success_rate:.0%} success)"
        )
        
        # Parameter insights
        if self.learning_rate > 0.4:
            insights.append("Learning quickly (high learning rate)")
        elif self.learning_rate < 0.2:
            insights.append("Learning cautiously (low learning rate)")
        
        if self.exploration_rate > 0.3:
            insights.append("Exploring many options")
        elif self.exploration_rate < 0.1:
            insights.append("Exploiting known strategies")
        
        # Adaptation insights
        if self.adaptations:
            recent_adapt = self.adaptations[-1]
            insights.append(
                f"Recently adapted: {recent_adapt['adaptations'][0] if recent_adapt['adaptations'] else 'none'}"
            )
        
        return insights
    
    # ══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _save(self):
        state = {
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "memory_threshold": self.memory_threshold,
            "strategies": {
                name: s.to_dict() for name, s in self.strategies.items()
            },
            "source_reliability": dict(self.source_reliability),
            "adaptations": self.adaptations[-20:],  # Keep last 20
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.path.write_text(json.dumps(state, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        try:
            state = json.loads(self.path.read_text())
            self.learning_rate = state.get("learning_rate", 0.3)
            self.exploration_rate = state.get("exploration_rate", 0.2)
            self.memory_threshold = state.get("memory_threshold", 0.6)
            
            # Restore strategy stats
            for name, data in state.get("strategies", {}).items():
                if name in self.strategies:
                    self.strategies[name].success_rate = data.get("success_rate", 0.5)
                    self.strategies[name].times_used = data.get("times_used", 0)
            
            self.source_reliability = defaultdict(
                lambda: 0.5,
                state.get("source_reliability", {})
            )
            self.adaptations = state.get("adaptations", [])
        except Exception as e:
            log.warning(f"Failed to load meta-learning state: {e}")
