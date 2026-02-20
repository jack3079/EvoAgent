"""
Meta-Learning System — Learning How to Learn

The agent doesn't just learn content.
It learns HOW to learn effectively.

Tracks:
- Which learning strategies work best
- How fast it learns in different domains
- What conditions optimize learning
- When to explore vs exploit in learning

This is the difference between:
- Learning 100 facts (object-level)
- Learning how to learn any fact efficiently (meta-level)

Based on:
- Meta-learning research (Schmidhuber, Lake, Botvinick)
- Learning-to-learn paradigm
- MAML (Model-Agnostic Meta-Learning)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional, List
import statistics

log = logging.getLogger(__name__)


class LearningEpisode:
    """A single learning experience."""
    
    def __init__(
        self,
        domain: str,
        strategy: str,
        initial_performance: float,
        final_performance: float,
        attempts: int,
        time_elapsed: float
    ):
        self.domain = domain
        self.strategy = strategy
        self.initial_performance = initial_performance
        self.final_performance = final_performance
        self.attempts = attempts
        self.time_elapsed = time_elapsed
        self.timestamp = datetime.utcnow().isoformat()
        
        # Computed metrics
        self.improvement = final_performance - initial_performance
        self.learning_rate = self.improvement / max(1, attempts)
        self.efficiency = self.improvement / max(1, time_elapsed)


class MetaLearningSystem:
    """
    Learns how to learn.
    
    Tracks which learning strategies are most effective
    and adapts the agent's learning approach over time.
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.path = Path(config.get("path", "./autonomy/meta_learning.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Learning history
        self.episodes: List[LearningEpisode] = []
        
        # Strategy effectiveness by domain
        self.strategy_performance = defaultdict(lambda: defaultdict(list))
        
        # Learning rates by domain
        self.domain_learning_rates = defaultdict(list)
        
        # Optimal conditions for learning
        self.learning_conditions = {
            "emotional_state": {},  # Which emotions help learning?
            "time_of_cycle": {},     # When do we learn best?
            "social_vs_solo": {},    # Learn better alone or with others?
        }
        
        # Meta-strategies
        self.meta_strategies = [
            "deliberate_practice",      # Focused, intentional practice
            "spaced_repetition",        # Review at intervals
            "interleaving",             # Mix different topics
            "elaboration",              # Connect to existing knowledge
            "generation",               # Try to recall before learning
            "reflection",               # Think about what you learned
            "social_learning",          # Learn from observing others
            "exploration_first",        # Explore broadly before deep dive
        ]
        
        # Current learning approach (adaptive)
        self.current_approach = {
            "strategy": "deliberate_practice",
            "confidence": 0.5,
            "last_updated": None,
        }
        
        self._load()
        log.info("Meta-learning system initialized")
    
    # ══════════════════════════════════════════════════════════
    # RECORDING LEARNING EPISODES
    # ══════════════════════════════════════════════════════════
    
    def record_episode(
        self,
        domain: str,
        strategy: str,
        initial_performance: float,
        final_performance: float,
        attempts: int,
        time_elapsed: float,
        context: dict = None
    ):
        """
        Record a learning episode.
        
        This is how we learn about learning.
        """
        episode = LearningEpisode(
            domain=domain,
            strategy=strategy,
            initial_performance=initial_performance,
            final_performance=final_performance,
            attempts=attempts,
            time_elapsed=time_elapsed
        )
        
        self.episodes.append(episode)
        
        # Update strategy performance tracking
        self.strategy_performance[domain][strategy].append(episode.learning_rate)
        
        # Update domain learning rates
        self.domain_learning_rates[domain].append(episode.learning_rate)
        
        # Update learning conditions if context provided
        if context:
            self._update_learning_conditions(episode, context)
        
        # Adapt meta-strategy if needed
        self._adapt_meta_strategy()
        
        self._save()
        
        log.info(f"Learning episode recorded: {domain} with {strategy} → {episode.improvement:.2f} improvement")
    
    # ══════════════════════════════════════════════════════════
    # META-STRATEGY SELECTION
    # ══════════════════════════════════════════════════════════
    
    def select_learning_strategy(self, domain: str, context: dict = None) -> str:
        """
        Choose the best learning strategy for this domain/context.
        
        This is meta-learning in action: using past experience
        to guide current learning approach.
        """
        # If we have data for this domain, use it
        if domain in self.strategy_performance:
            # Find best-performing strategy
            best_strategy = None
            best_rate = -float('inf')
            
            for strategy, rates in self.strategy_performance[domain].items():
                if rates:
                    avg_rate = statistics.mean(rates)
                    if avg_rate > best_rate:
                        best_rate = avg_rate
                        best_strategy = strategy
            
            if best_strategy:
                log.info(f"Meta-learning: Using {best_strategy} for {domain} (proven effective)")
                return best_strategy
        
        # If new domain, check similar domains
        similar_domain = self._find_similar_domain(domain)
        if similar_domain and similar_domain in self.strategy_performance:
            # Use strategy from similar domain
            strategies = self.strategy_performance[similar_domain]
            if strategies:
                best = max(strategies.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)
                log.info(f"Meta-learning: Using {best[0]} (works for similar domain: {similar_domain})")
                return best[0]
        
        # If context suggests social learning is possible, try that
        if context and context.get("others_available"):
            log.info("Meta-learning: Trying social_learning (others present)")
            return "social_learning"
        
        # Default to current approach
        return self.current_approach["strategy"]
    
    def get_optimal_learning_conditions(self) -> dict:
        """
        What conditions maximize learning?
        
        Returns recommended:
        - Emotional state
        - Time/cycle
        - Social vs solo
        - Environment factors
        """
        conditions = {}
        
        # Best emotional state for learning
        if self.learning_conditions["emotional_state"]:
            best_emotion = max(
                self.learning_conditions["emotional_state"].items(),
                key=lambda x: x[1]["avg_improvement"]
            )
            conditions["emotion"] = best_emotion[0]
        
        # Best time of cycle
        if self.learning_conditions["time_of_cycle"]:
            best_time = max(
                self.learning_conditions["time_of_cycle"].items(),
                key=lambda x: x[1]["avg_improvement"]
            )
            conditions["cycle_phase"] = best_time[0]
        
        # Social vs solo
        if self.learning_conditions["social_vs_solo"]:
            if len(self.learning_conditions["social_vs_solo"]) >= 2:
                solo_rate = self.learning_conditions["social_vs_solo"].get("solo", {}).get("avg_rate", 0)
                social_rate = self.learning_conditions["social_vs_solo"].get("social", {}).get("avg_rate", 0)
                conditions["mode"] = "social" if social_rate > solo_rate else "solo"
        
        return conditions
    
    # ══════════════════════════════════════════════════════════
    # LEARNING EFFICIENCY ANALYSIS
    # ══════════════════════════════════════════════════════════
    
    def get_learning_profile(self) -> dict:
        """
        Comprehensive profile of how the agent learns.
        
        This is self-knowledge about learning.
        """
        if not self.episodes:
            return {"message": "No learning episodes yet"}
        
        profile = {}
        
        # Overall learning rate
        all_rates = [ep.learning_rate for ep in self.episodes]
        profile["avg_learning_rate"] = statistics.mean(all_rates)
        profile["learning_rate_std"] = statistics.stdev(all_rates) if len(all_rates) > 1 else 0
        
        # Learning by domain
        profile["domain_expertise"] = {}
        for domain, rates in self.domain_learning_rates.items():
            if rates:
                profile["domain_expertise"][domain] = {
                    "avg_rate": statistics.mean(rates),
                    "episodes": len(rates),
                    "total_improvement": sum(ep.improvement for ep in self.episodes if ep.domain == domain)
                }
        
        # Best strategy overall
        all_strategy_rates = defaultdict(list)
        for domain_strategies in self.strategy_performance.values():
            for strategy, rates in domain_strategies.items():
                all_strategy_rates[strategy].extend(rates)
        
        if all_strategy_rates:
            profile["best_strategy"] = max(
                all_strategy_rates.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else 0
            )[0]
        
        # Optimal conditions
        profile["optimal_conditions"] = self.get_optimal_learning_conditions()
        
        # Adaptation over time (are we getting better at learning?)
        if len(self.episodes) >= 10:
            recent = self.episodes[-10:]
            early = self.episodes[:10]
            recent_rate = statistics.mean([ep.learning_rate for ep in recent])
            early_rate = statistics.mean([ep.learning_rate for ep in early])
            profile["meta_learning_improvement"] = recent_rate - early_rate
        
        return profile
    
    def predict_learning_time(self, domain: str, target_performance: float, current_performance: float = 0.0) -> dict:
        """
        Predict how long it will take to reach target performance.
        
        Based on past learning rates in this domain.
        """
        if domain not in self.domain_learning_rates or not self.domain_learning_rates[domain]:
            return {
                "estimated_attempts": "unknown",
                "confidence": 0.0,
                "note": "No prior data for this domain"
            }
        
        avg_rate = statistics.mean(self.domain_learning_rates[domain])
        
        if avg_rate <= 0:
            return {
                "estimated_attempts": "impossible",
                "confidence": 0.5,
                "note": "No learning progress observed in past attempts"
            }
        
        performance_gap = target_performance - current_performance
        estimated_attempts = performance_gap / avg_rate
        
        return {
            "estimated_attempts": int(estimated_attempts),
            "confidence": min(1.0, len(self.domain_learning_rates[domain]) / 10),
            "note": f"Based on {len(self.domain_learning_rates[domain])} prior episodes"
        }
    
    # ══════════════════════════════════════════════════════════
    # ADAPTIVE META-STRATEGY
    # ══════════════════════════════════════════════════════════
    
    def _adapt_meta_strategy(self):
        """
        Adjust the overall learning approach based on results.
        
        This is the "meta" in meta-learning.
        """
        if len(self.episodes) < 5:
            return  # Need more data
        
        # Get recent performance
        recent_episodes = self.episodes[-10:]
        recent_rate = statistics.mean([ep.learning_rate for ep in recent_episodes])
        
        # Compare to overall average
        all_rate = statistics.mean([ep.learning_rate for ep in self.episodes])
        
        # If recent performance is declining, change strategy
        if recent_rate < all_rate * 0.8:
            # Try a different meta-strategy
            current = self.current_approach["strategy"]
            alternatives = [s for s in self.meta_strategies if s != current]
            
            if alternatives:
                import random
                new_strategy = random.choice(alternatives)
                
                self.current_approach = {
                    "strategy": new_strategy,
                    "confidence": 0.5,
                    "last_updated": datetime.utcnow().isoformat(),
                }
                
                log.info(f"Meta-learning: Adapted strategy to {new_strategy}")
    
    def _update_learning_conditions(self, episode: LearningEpisode, context: dict):
        """Track which conditions optimize learning."""
        # Emotional state
        emotion = context.get("emotion", "neutral")
        if emotion not in self.learning_conditions["emotional_state"]:
            self.learning_conditions["emotional_state"][emotion] = {
                "count": 0,
                "total_improvement": 0,
                "avg_improvement": 0,
            }
        
        self.learning_conditions["emotional_state"][emotion]["count"] += 1
        self.learning_conditions["emotional_state"][emotion]["total_improvement"] += episode.improvement
        self.learning_conditions["emotional_state"][emotion]["avg_improvement"] = (
            self.learning_conditions["emotional_state"][emotion]["total_improvement"] /
            self.learning_conditions["emotional_state"][emotion]["count"]
        )
        
        # Social vs solo
        mode = "social" if context.get("others_present") else "solo"
        if mode not in self.learning_conditions["social_vs_solo"]:
            self.learning_conditions["social_vs_solo"][mode] = {
                "count": 0,
                "total_rate": 0,
                "avg_rate": 0,
            }
        
        self.learning_conditions["social_vs_solo"][mode]["count"] += 1
        self.learning_conditions["social_vs_solo"][mode]["total_rate"] += episode.learning_rate
        self.learning_conditions["social_vs_solo"][mode]["avg_rate"] = (
            self.learning_conditions["social_vs_solo"][mode]["total_rate"] /
            self.learning_conditions["social_vs_solo"][mode]["count"]
        )
    
    def _find_similar_domain(self, domain: str) -> Optional[str]:
        """Find a domain similar to the given one."""
        # Simple heuristic: keyword matching
        domain_words = set(domain.lower().split())
        
        best_match = None
        best_score = 0
        
        for known_domain in self.domain_learning_rates.keys():
            known_words = set(known_domain.lower().split())
            overlap = len(domain_words & known_words)
            
            if overlap > best_score:
                best_score = overlap
                best_match = known_domain
        
        return best_match if best_score > 0 else None
    
    # ══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _save(self):
        data = {
            "episodes": [
                {
                    "domain": ep.domain,
                    "strategy": ep.strategy,
                    "improvement": ep.improvement,
                    "learning_rate": ep.learning_rate,
                    "attempts": ep.attempts,
                    "timestamp": ep.timestamp,
                }
                for ep in self.episodes[-100:]  # Keep last 100
            ],
            "current_approach": self.current_approach,
            "learning_conditions": self.learning_conditions,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        self.path.write_text(json.dumps(data, indent=2))
    
    def _load(self):
        if not self.path.exists():
            return
        
        try:
            data = json.loads(self.path.read_text())
            self.current_approach = data.get("current_approach", self.current_approach)
            self.learning_conditions = data.get("learning_conditions", self.learning_conditions)
            # Episodes reconstruction simplified
        except Exception as e:
            log.warning(f"Failed to load meta-learning state: {e}")
    
    def get_meta_learning_status(self) -> dict:
        """Current meta-learning state."""
        return {
            "total_episodes": len(self.episodes),
            "current_strategy": self.current_approach["strategy"],
            "domains_learned": len(self.domain_learning_rates),
            "learning_profile": self.get_learning_profile(),
        }
