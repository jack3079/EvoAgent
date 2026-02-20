"""
ERLAgent — Experiential Reinforcement Learning Agent

Implements the paper's key innovation:
    Task → Attempt 1 → Reflection → Attempt 2 → Policy Internalization

Unlike the basic agent (which just adds tools), this agent:
- Learns from EXPERIENCE, not just from capability gaps
- Internalizes successful patterns into BASE POLICY
- Improves REASONING ITSELF, not just the tool library

Based on:
- Kolb's Experiential Learning Cycle
- The paper: "Kolb-Based Experiential Learning for Generalist Agents..."
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional

from .memory import Memory
from .code_writer import CodeWriter
from .executor import Executor
from .integrator import Integrator
from .evolution import EvolutionLog
from .policy_store import PolicyStore
from .reflection_engine import ReflectionEngine

log = logging.getLogger(__name__)


@dataclass
class AttemptResult:
    """Result of a single attempt at a task."""
    success: bool
    output: Any
    steps: list
    reasoning_trace: str
    elapsed: float
    metadata: dict = field(default_factory=dict)


@dataclass
class ERLSession:
    """Tracks learning within a session."""
    session_id: str
    generation: int = 0
    tasks_done: int = 0
    erl_cycles: int = 0          # How many two-attempt cycles completed
    policy_updates: int = 0      # How many times policy was updated
    principles_learned: int = 0


class ERLAgent:
    """
    Experiential Reinforcement Learning Agent.
    
    Key difference from base agent:
        Base:  fail → add tool → succeed
        ERL:   attempt → reflect → revised attempt → internalize learning
    
    The agent doesn't just grow capabilities — it improves how it THINKS.
    """

    def __init__(self, config: dict, llm=None):
        self.config = config
        self.llm = llm
        self.session = ERLSession(
            session_id=datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        )

        # Core systems
        self.memory = Memory(config.get("memory", {}))
        self.code_writer = CodeWriter(config.get("llm", {}), llm)
        self.executor = Executor(config.get("executor", {}))
        self.integrator = Integrator(self.memory, self.executor)
        self.evo = EvolutionLog(config.get("evolution", {}))
        
        # ERL-specific systems
        self.policy = PolicyStore(config.get("policy", {}))
        self.reflector = ReflectionEngine(llm, config.get("llm", {}))

        log.info(f"ERLAgent ready | session={self.session.session_id}")

    # ═══════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════

    def run(self, task: str, verbose: bool = False) -> dict:
        """
        Execute task with full ERL cycle.
        
        Process:
        1. Attempt 1 with current policy
        2. If fails → deep reflection
        3. Attempt 2 guided by reflection
        4. If succeeds → internalize learned principle
        """
        log.info(f"ERL Task: {task}")
        
        # ── ATTEMPT 1 ────────────────────────────────────────
        attempt_1 = self._attempt(task, attempt_num=1)
        
        if attempt_1.success:
            # First-try success — store but don't update policy aggressively
            self._store_experience(task, attempt_1, reflection_guided=False)
            self.session.tasks_done += 1
            return self._format_result(task, attempt_1, erl_applied=False)
        
        # ── REFLECTION ───────────────────────────────────────
        if verbose:
            print(f"\n  💭 Attempt 1 failed. Beginning deep reflection...")
        
        reflection = self.reflector.deep_reflect(
            task=task,
            attempt_1_output=attempt_1.output,
            attempt_1_success=attempt_1.success,
            attempt_1_steps=attempt_1.steps,
            available_context={
                "tools_available": [t["name"] for t in self.memory.all_tools()],
                "relevant_experience": self.memory.recall(task, k=3),
            }
        )
        
        if verbose:
            self._print_reflection(reflection)
        
        # ── ATTEMPT 2 (Reflection-Guided) ───────────────────
        if verbose:
            print(f"\n  🔄 Attempting task again with refined approach...")
        
        attempt_2 = self._attempt(
            task,
            attempt_num=2,
            guided_by_reflection=reflection
        )
        
        # ── LEARNING INTERNALIZATION ────────────────────────
        if attempt_2.success:
            self._internalize_learning(task, reflection, attempt_2)
            self.session.erl_cycles += 1
            
        self._store_experience(task, attempt_2, reflection_guided=True, reflection=reflection)
        self.session.tasks_done += 1
        
        return self._format_result(task, attempt_2, erl_applied=True, reflection=reflection)

    def get_status(self) -> dict:
        """Agent status including ERL metrics."""
        policy_summary = self.policy.get_summary()
        return {
            "session": self.session.session_id,
            "generation": self.session.generation,
            "tasks_completed": self.session.tasks_done,
            "erl_cycles": self.session.erl_cycles,
            "policy_updates": self.session.policy_updates,
            "tools_available": len(self.memory.all_tools()),
            "principles_learned": len(self.policy.principles),
            "avg_principle_success": policy_summary["avg_success_rate"],
        }

    # ═══════════════════════════════════════════════════════════
    # CORE ERL METHODS
    # ═══════════════════════════════════════════════════════════

    def _attempt(
        self,
        task: str,
        attempt_num: int,
        guided_by_reflection: Optional[dict] = None
    ) -> AttemptResult:
        """
        Make one attempt at the task.
        
        If guided_by_reflection, inject learned patterns into reasoning.
        """
        import time
        start = time.time()
        
        # Build enhanced prompt with policy guidance
        enhanced_prompt = self._build_task_prompt(task, guided_by_reflection)
        
        # Plan
        plan_response = self._call_llm(enhanced_prompt)
        plan = self._parse_json(plan_response) or {}
        
        # Execute
        steps = plan.get("steps", [task])
        results = []
        
        for step in steps:
            tool = self.memory.best_tool_for(step)
            if tool:
                r = self.executor.run_tool(tool, step)
                results.append(r)
            else:
                # Fallback to LLM
                r = {"ok": True, "output": self._call_llm(f"Do: {step}")}
                results.append(r)
        
        overall_success = all(r.get("ok", False) for r in results)
        elapsed = time.time() - start
        
        return AttemptResult(
            success=overall_success,
            output=self._summarize(task, results),
            steps=steps,
            reasoning_trace=plan_response,
            elapsed=elapsed,
            metadata={"attempt": attempt_num, "plan": plan}
        )

    def _internalize_learning(self, task: str, reflection: dict, success: AttemptResult):
        """
        The KEY step: internalize learned pattern into base policy.
        
        This is what makes learning durable — not just adding a tool,
        but updating HOW THE AGENT THINKS.
        """
        if not reflection.get("should_update_policy"):
            return
        
        policy_principle = reflection.get("policy_principle", {})
        if not policy_principle or not policy_principle.get("pattern"):
            return
        
        # Add to policy store
        self.policy.add_principle(policy_principle)
        self.session.policy_updates += 1
        self.session.principles_learned += 1
        
        log.info(f"✓ Policy updated | principle: {policy_principle.get('pattern', '')[:60]}")
        
        # Also record this as an evolution event
        self.session.generation += 1
        self.evo.record(
            generation=self.session.generation,
            trigger=task,
            new_tool="policy_principle",
            description=policy_principle.get("pattern", ""),
            metadata={
                "type": "policy_update",
                "context": policy_principle.get("context", ""),
                "confidence": policy_principle.get("confidence", 0.8),
            }
        )

    def _build_task_prompt(self, task: str, reflection: Optional[dict] = None) -> str:
        """
        Build task prompt with dynamic policy injection.
        
        This is where learned principles guide new attempts.
        """
        # Get relevant principles from policy
        policy_section = self.policy.to_prompt_section(task)
        
        # Get available tools
        tools = [t["name"] for t in self.memory.all_tools()]
        
        base = f"""You are an AI agent with experiential learning capabilities.

{policy_section}

Task: {task}

Available tools: {tools}
"""
        
        if reflection:
            guidance = reflection.get("guidance_for_attempt_2", "")
            learned = reflection.get("learned_pattern", "")
            base += f"""
## Reflection-Guided Approach
Previous attempt failed. Based on reflection:

Learned pattern: {learned}
Specific guidance: {guidance}

Apply this learning to your approach.
"""
        
        base += """
Plan your approach and reply with JSON:
{
  "steps": ["step 1", "step 2", ...],
  "reasoning": "why this approach should work",
  "tools_to_use": ["tool_name"]
}"""
        
        return base

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _store_experience(
        self,
        task: str,
        attempt: AttemptResult,
        reflection_guided: bool,
        reflection: Optional[dict] = None
    ):
        """Store experience in memory."""
        exp = {
            "task": task,
            "success": attempt.success,
            "reflection_guided": reflection_guided,
            "learned": [],
            "ts": datetime.utcnow().isoformat()
        }
        
        if reflection:
            exp["learned"] = [reflection.get("learned_pattern", "")]
        
        self.memory.store(exp)

    def _format_result(
        self,
        task: str,
        attempt: AttemptResult,
        erl_applied: bool,
        reflection: Optional[dict] = None
    ) -> dict:
        """Format final result for caller."""
        return {
            "success": attempt.success,
            "output": attempt.output,
            "erl_applied": erl_applied,
            "generation": self.session.generation,
            "learned_pattern": reflection.get("learned_pattern", "") if reflection else "",
            "policy_updated": reflection.get("should_update_policy", False) if reflection else False,
        }

    def _call_llm(self, prompt: str) -> str:
        if not self.llm:
            return "Mock response"
        try:
            r = self.llm.messages.create(
                model=self.config.get("llm", {}).get("model", "claude-opus-4-5-20251101"),
                max_tokens=self.config.get("llm", {}).get("max_tokens", 4096),
                messages=[{"role": "user", "content": prompt}]
            )
            return r.content[0].text
        except Exception as e:
            log.error(f"LLM error: {e}")
            return "{}"

    def _parse_json(self, text: str) -> Optional[dict]:
        import re
        text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`")
        for pat in [r"\{.*\}", r"\[.*\]"]:
            m = re.search(pat, text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except:
                    pass
        return None

    def _summarize(self, task: str, results: list) -> str:
        if not results:
            return "No results"
        if all(r.get("ok") for r in results):
            return "Task completed successfully"
        return "Task execution encountered issues"

    def _print_reflection(self, reflection: dict):
        """Pretty print reflection for verbose mode."""
        print(f"    Reasoning errors: {reflection.get('reasoning_errors', [])}")
        print(f"    Learned pattern: {reflection.get('learned_pattern', '')[:80]}")
        print(f"    Guidance: {reflection.get('guidance_for_attempt_2', '')[:80]}")
