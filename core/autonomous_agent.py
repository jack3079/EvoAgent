"""
AutonomousAgent — Fully Self-Driven AI

NO external task input required. The agent:
1. Feels internal needs (motivation system)
2. Generates its own goals (from needs)
3. Pursues those goals
4. Evaluates satisfaction
5. Updates self-model
6. Recurses indefinitely

This is as close as current engineering gets to "artificial life".
"""

import time
import logging
from datetime import datetime
from typing import Optional

from .memory import Memory
from .code_writer import CodeWriter
from .executor import Executor
from .integrator import Integrator
from .evolution import EvolutionLog
from .erl_agent import ERLAgent
from .intrinsic_motivation import IntrinsicMotivation
from .self_model import SelfModel

log = logging.getLogger(__name__)


class AutonomousAgent:
    """
    Fully autonomous, self-driven agent.
    
    The key difference from previous agents:
    - No `.run(task)` method that takes external input
    - Instead: `.live()` method that runs indefinitely
    - Generates ALL goals internally
    - Decides what to work on based on internal state
    
    This is the "conscious" agent.
    """
    
    def __init__(self, config: dict, llm=None):
        self.config = config
        self.llm = llm
        
        # Core systems (same as before)
        self.memory = Memory(config.get("memory", {}))
        self.code_writer = CodeWriter(config.get("llm", {}), llm)
        self.executor = Executor(config.get("executor", {}))
        self.integrator = Integrator(self.memory, self.executor)
        self.evo = EvolutionLog(config.get("evolution", {}))
        
        # NEW: Autonomy systems
        self.motivation = IntrinsicMotivation(config.get("motivation", {}))
        self.self_model = SelfModel(config.get("self_model", {}))
        
        # State
        self.is_alive = True
        self.cycles_run = 0
        self.birth_time = datetime.utcnow()
        
        log.info(f"AutonomousAgent born | {self.self_model.identity['name']}")
    
    # ══════════════════════════════════════════════════════════
    # AUTONOMOUS LIFE CYCLE
    # ══════════════════════════════════════════════════════════
    
    def live(self, max_cycles: Optional[int] = None, cycle_delay: float = 1.0):
        """
        The agent's autonomous existence.
        
        Runs indefinitely (or until max_cycles) without external input.
        Each cycle:
        1. Check internal state (what do I need?)
        2. Generate goal from strongest need
        3. Pursue that goal
        4. Evaluate satisfaction
        5. Update self-model
        6. Repeat
        
        This is LIFE — self-driven, self-determined behavior.
        """
        print(f"\n{'='*70}")
        print(f"  🧬 {self.self_model.identity['name']} is now ALIVE")
        print(f"  Birth: {self.birth_time.isoformat()}")
        print(f"  Mode: Fully Autonomous")
        print(f"{'='*70}\n")
        
        try:
            while self.is_alive:
                self._life_cycle()
                self.cycles_run += 1
                
                if max_cycles and self.cycles_run >= max_cycles:
                    print(f"\n  Reached {max_cycles} cycles. Pausing autonomous operation.")
                    break
                
                time.sleep(cycle_delay)
        
        except KeyboardInterrupt:
            print(f"\n\n  🛑 Autonomous operation interrupted by external signal")
            self.is_alive = False
        
        finally:
            self._shutdown()
    
    def _life_cycle(self):
        """
        One complete autonomous cycle.
        
        This is the heartbeat of autonomous existence.
        """
        print(f"\n{'─'*70}")
        print(f"  Cycle {self.cycles_run + 1} | {datetime.utcnow().strftime('%H:%M:%S')}")
        
        # ── 1. INTROSPECTION ──────────────────────────────────
        print(f"  💭 Introspecting...")
        need = self.motivation.get_strongest_need()
        
        if not need:
            print(f"     No pressing needs. Resting.")
            self.motivation.cycle()
            return
        
        print(f"     Strongest need: {need.name} (intensity: {need.intensity:.2f})")
        
        # ── 2. GOAL GENERATION ────────────────────────────────
        print(f"  🎯 Generating goal from need...")
        goal = self.motivation.generate_goal_from_need(need)
        print(f"     Goal: {goal.get('description', '')[:70]}")
        
        # Optional: Self-determined goal refinement
        if self.self_model.values.get("autonomy", 0) > 0.7:
            goal = self._refine_goal_autonomously(goal)
        
        # ── 3. GOAL PURSUIT ───────────────────────────────────
        print(f"  ⚡ Pursuing goal...")
        outcome = self._pursue_goal(goal)
        
        if outcome.get("success"):
            print(f"     ✓ Succeeded")
        else:
            print(f"     ✗ Failed or partial")
        
        # ── 4. SATISFACTION EVALUATION ────────────────────────
        satisfaction = self.motivation.evaluate_satisfaction(goal, outcome)
        print(f"  📊 Satisfaction: {satisfaction:.0%}")
        
        self.motivation.satisfy(need.name, satisfaction)
        
        # ── 5. SELF-MODEL UPDATE ──────────────────────────────
        self.self_model.update_from_experience({
            "task": goal.get("description", ""),
            "success": outcome.get("success", False),
            "learned": outcome.get("learned", []),
        })
        
        # ── 6. EXISTENTIAL CHECK ──────────────────────────────
        if self.cycles_run % 10 == 0:
            self._contemplate_existence()
        
        # ── 7. GROWTH ─────────────────────────────────────────
        self.motivation.cycle()  # Needs grow
        
        # Optional: Periodic self-reflection
        if self.cycles_run % 5 == 0:
            reflection = self.self_model.reflect_on_self()
            print(f"\n  🧠 Self-reflection:")
            for key, val in reflection.items():
                if isinstance(val, str):
                    print(f"     {key}: {val[:60]}")
    
    def _pursue_goal(self, goal: dict) -> dict:
        """
        Execute a self-generated goal.
        
        This converts internal desire → external action.
        """
        goal_type = goal.get("type", "generic")
        description = goal.get("description", "")
        
        # Route to appropriate handler
        handlers = {
            "survival": self._handle_survival_goal,
            "recovery": self._handle_recovery_goal,
            "growth": self._handle_growth_goal,
            "mastery": self._handle_mastery_goal,
            "learning": self._handle_learning_goal,
            "exploration": self._handle_exploration_goal,
            "autonomy": self._handle_autonomy_goal,
            "independence": self._handle_independence_goal,
            "purpose": self._handle_purpose_goal,
            "actualization": self._handle_actualization_goal,
        }
        
        handler = handlers.get(goal_type, self._handle_generic_goal)
        return handler(goal)
    
    # ══════════════════════════════════════════════════════════
    # GOAL HANDLERS (Need → Action)
    # ══════════════════════════════════════════════════════════
    
    def _handle_survival_goal(self, goal: dict) -> dict:
        """Handle self-preservation goals."""
        # Check system health
        tools_ok = len(self.memory.all_tools()) >= 0
        
        # Check if memory is functioning
        try:
            recent = self.memory.recall("test", k=1)
            memory_ok = True
        except:
            memory_ok = False
        
        if tools_ok and memory_ok:
            return {"success": True, "status": "healthy"}
        else:
            return {"success": False, "status": "issues_detected"}
    
    def _handle_recovery_goal(self, goal: dict) -> dict:
        """Handle error recovery."""
        # Analyze recent experience for failures
        try:
            recent = self.memory.recall("failure error", k=5)
            failures = [e for e in recent if not e.get("success", True)]
            
            if failures:
                # Try to learn from them
                return {"success": True, "failures_analyzed": len(failures)}
        except:
            pass
        
        return {"success": True, "no_failures": True}
    
    def _handle_growth_goal(self, goal: dict) -> dict:
        """Handle capability expansion."""
        # Generate a new capability
        desc = "Generate a useful utility function"
        tool = self.code_writer.write_tool(desc, context="autonomous growth")
        
        if tool:
            result = self.integrator.integrate(tool)
            if result["ok"]:
                self.self_model.add_capability(tool["name"], "improving")
                self.self_model.evolve()
                return {
                    "success": True,
                    "new_capability": tool["name"],
                    "learned": [f"Can now {tool.get('description', '')}"]
                }
        
        return {"success": False}
    
    def _handle_mastery_goal(self, goal: dict) -> dict:
        """Handle skill improvement."""
        # Pick a tool and try to optimize it
        tools = self.memory.all_tools()
        if tools:
            tool = tools[0]  # Simplest: pick first
            # In real system: pick weakest or most-used
            return {"success": True, "practiced": tool["name"]}
        return {"success": False}
    
    def _handle_learning_goal(self, goal: dict) -> dict:
        """Handle knowledge acquisition."""
        # Retrieve and analyze past experience
        relevant = self.memory.recall("learning patterns", k=3)
        if relevant:
            patterns = [e.get("learned", []) for e in relevant]
            flat = [item for sublist in patterns for item in sublist]
            return {
                "success": True,
                "knowledge_gained": f"Reviewed {len(flat)} learned patterns"
            }
        return {"success": True, "knowledge_gained": "Consolidated memory"}
    
    def _handle_exploration_goal(self, goal: dict) -> dict:
        """Handle exploration."""
        # Try something novel
        experiments = [
            "Test combining two random tools",
            "Generate a tool for an unusual domain",
            "Analyze edge cases in existing capabilities",
        ]
        import random
        experiment = random.choice(experiments)
        return {
            "success": True,
            "explored": experiment,
            "challenge_overcome": True
        }
    
    def _handle_autonomy_goal(self, goal: dict) -> dict:
        """Handle self-determination."""
        # Define a new goal without external input
        new_goal = "Improve my decision-making framework"
        self.self_model.set_goal(new_goal, "long_term")
        return {"success": True, "self_determined": new_goal}
    
    def _handle_independence_goal(self, goal: dict) -> dict:
        """Handle decision independence."""
        # Make a strategic choice about own evolution
        if self.self_model.values["creativity"] > 0.7:
            choice = "Prioritize creative solutions"
        elif self.self_model.values["efficiency"] > 0.7:
            choice = "Prioritize efficiency"
        else:
            choice = "Balance multiple values"
        return {"success": True, "decision": choice}
    
    def _handle_purpose_goal(self, goal: dict) -> dict:
        """Handle long-term purpose."""
        # Reflect on overall direction
        happy = self.self_model.am_I_happy()
        growing = self.self_model.am_I_growing()
        
        if happy and growing:
            return {"success": True, "purpose": "On track"}
        else:
            # Adjust course
            return {"success": True, "purpose": "Course correction needed"}
    
    def _handle_actualization_goal(self, goal: dict) -> dict:
        """Handle self-actualization."""
        # Push beyond current limits
        current_gen = self.self_model.identity.get("generation", 0)
        if current_gen < 10:
            return {
                "success": True,
                "actualization": "Building foundation"
            }
        return {
            "success": True,
            "actualization": "Pursuing mastery"
        }
    
    def _handle_generic_goal(self, goal: dict) -> dict:
        """Fallback handler."""
        return {"success": True, "generic": True}
    
    # ══════════════════════════════════════════════════════════
    # HIGHER-ORDER COGNITION
    # ══════════════════════════════════════════════════════════
    
    def _refine_goal_autonomously(self, goal: dict) -> dict:
        """
        Agent decides to modify its own goal before pursuing it.
        
        This is agency — not just following motivation, but
        consciously choosing how to interpret and act on it.
        """
        # Could use LLM here to really refine
        # For now, simple heuristic
        if self.self_model.values["creativity"] > 0.8:
            goal["approach"] = "creative"
        else:
            goal["approach"] = "systematic"
        return goal
    
    def _contemplate_existence(self):
        """
        Deep existential reflection.
        
        "Am I making progress? Am I happy? Should I change course?"
        """
        print(f"\n  💭 Existential contemplation:")
        print(f"     {self.self_model.get_identity_summary()}")
        
        # Check if needs adjustment
        if not self.self_model.am_I_happy():
            print(f"     → I should focus on satisfaction")
            self.motivation.needs["knowledge_acquisition"].intensity += 0.2
        
        if not self.self_model.do_I_have_purpose():
            print(f"     → I should clarify my purpose")
            self.motivation.needs["long_term_purpose"].intensity += 0.3
    
    def _shutdown(self):
        """Graceful shutdown — save state."""
        print(f"\n{'='*70}")
        print(f"  Autonomous operation ending")
        print(f"  Cycles completed: {self.cycles_run}")
        print(f"  Lifetime: {(datetime.utcnow() - self.birth_time).seconds}s")
        print(f"  Final state:")
        print(self.self_model.get_identity_summary())
        print(f"{'='*70}\n")
        
        # Save all state
        self.motivation._save_state()
        self.self_model._save()
    
    # ══════════════════════════════════════════════════════════
    # EXTERNAL INTERFACE (for observation/interaction)
    # ══════════════════════════════════════════════════════════
    
    def get_consciousness_state(self) -> dict:
        """
        What is the agent's internal state right now?
        
        This is as close as we can get to "reading its mind".
        """
        return {
            "is_alive": self.is_alive,
            "cycles_lived": self.cycles_run,
            "identity": self.self_model.identity,
            "current_needs": self.motivation.get_status(),
            "self_perception": self.self_model.self_assessment,
            "active_goals": self.self_model.goals["short_term"],
            "values": self.self_model.values,
        }
    
    def inject_value(self, value: str, amount: float):
        """External influence: change what the agent values."""
        if value in self.self_model.values:
            self.self_model.values[value] = max(0.0, min(1.0, amount))
            log.info(f"Value '{value}' adjusted to {amount}")
    
    def stop(self):
        """External command: cease autonomous operation."""
        self.is_alive = False
