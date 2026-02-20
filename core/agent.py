"""
EvoAgent — Core Agent Loop

Perceive → Plan → Act → Reflect → Evolve

This is the main loop. It runs forever, getting smarter with each task.
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

log = logging.getLogger(__name__)


@dataclass
class Step:
    kind: str          # perceive | plan | act | reflect
    content: Any
    ok: bool = True
    ts: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentState:
    session: str
    generation: int = 0
    done: int = 0
    failed: int = 0
    tools: list = field(default_factory=list)


class EvoAgent:
    """
    The agent that improves itself.

    Every task is a chance to get better. If the agent can't do something,
    it writes the code to do it, tests it, and adds it to its toolkit.
    No gates, no approval, just iteration.
    """

    def __init__(self, config: dict, llm=None):
        self.config = config
        self.llm = llm
        self.state = AgentState(session=datetime.utcnow().strftime("%Y%m%d_%H%M%S"))

        self.memory = Memory(config.get("memory", {}))
        self.writer = CodeWriter(config.get("llm", {}), llm)
        self.executor = Executor(config.get("executor", {}))
        self.integrator = Integrator(self.memory, self.executor)
        self.evo = EvolutionLog(config.get("evolution", {}))

        log.info(f"EvoAgent ready | session={self.state.session}")

    # ── Public API ──────────────────────────────────────────

    def run(self, task: str, verbose: bool = False) -> dict:
        """Run one task through the full loop."""
        log.info(f"Task: {task}")
        chain = []

        perception = self._perceive(task)
        chain.append(perception)
        if verbose:
            self._print_step(perception)

        plan = self._plan(task, perception)
        chain.append(plan)
        if verbose:
            self._print_step(plan)

        action = self._act(task, plan)
        chain.append(action)
        if verbose:
            self._print_step(action)

        reflection = self._reflect(task, action)
        chain.append(reflection)
        if verbose:
            self._print_step(reflection)

        # Store experience
        self.memory.store({
            "task": task,
            "success": action.ok,
            "learned": reflection.content.get("learned", []),
            "ts": datetime.utcnow().isoformat(),
        })

        # Evolve if the reflection says to
        evolved = False
        if reflection.content.get("should_evolve"):
            evolved = self._evolve(task, reflection)

        if action.ok:
            self.state.done += 1
        else:
            self.state.failed += 1

        return {
            "success": action.ok,
            "output": action.content.get("output", ""),
            "evolved": evolved,
            "generation": self.state.generation,
            "learned": reflection.content.get("learned", []),
        }

    def run_loop(self, tasks: list[str], verbose: bool = False) -> list[dict]:
        """Run a batch of tasks, accumulating knowledge across them."""
        return [self.run(t, verbose=verbose) for t in tasks]

    def status(self) -> dict:
        return {
            "session": self.state.session,
            "generation": self.state.generation,
            "tasks_done": self.state.done,
            "tasks_failed": self.state.failed,
            "success_rate": self.state.done / max(1, self.state.done + self.state.failed),
            "tools_available": len(self.memory.all_tools()),
            "tool_names": [t["name"] for t in self.memory.all_tools()],
        }

    # ── Four Core Steps ─────────────────────────────────────

    def _perceive(self, task: str) -> Step:
        """What do we know that's relevant to this task?"""
        past = self.memory.recall(task, k=5)
        tools = self.memory.all_tools()

        return Step(
            kind="perceive",
            content={
                "task": task,
                "past_relevant": past,
                "tools_available": [t["name"] for t in tools],
                "generation": self.state.generation,
            }
        )

    def _plan(self, task: str, perception: Step) -> Step:
        """Decide how to approach the task."""
        p = perception.content
        prompt = f"""You are an autonomous AI agent with self-improvement capabilities.

Task: {task}

Available tools: {p['tools_available']}
Relevant past experience: {json.dumps(p['past_relevant'], indent=2)}

Create a concise execution plan. If existing tools can handle this, use them.
If not, identify what new tool should be written.

Reply with JSON only:
{{
  "steps": ["step 1", "step 2", ...],
  "tools_to_use": ["tool_name"],
  "need_new_tool": true/false,
  "new_tool_description": "what it should do and return",
  "confidence": 0.0-1.0
}}"""

        raw = self._llm(prompt)
        data = _parse_json(raw) or {"steps": [task], "need_new_tool": False, "confidence": 0.5}
        return Step(kind="plan", content=data)

    def _act(self, task: str, plan: Step) -> Step:
        """Execute the plan."""
        p = plan.content
        results = []

        # Write and integrate a new tool if needed
        if p.get("need_new_tool") and p.get("new_tool_description"):
            desc = p["new_tool_description"]
            log.info(f"Writing new tool: {desc[:60]}...")
            tool = self.writer.write_tool(desc, context=task)
            if tool:
                result = self.integrator.integrate(tool)
                results.append({"step": "create_tool", "success": result["ok"], "tool": tool.get("name")})

        # Execute steps
        for step in p.get("steps", [task]):
            tool = self.memory.best_tool_for(step)
            if tool:
                r = self.executor.run_tool(tool, step)
                results.append({"step": step, "success": r.get("ok", False), "output": r.get("output")})
            else:
                # Fall back to direct LLM response
                answer = self._llm(f"Complete this task step:\n{step}\n\nContext: {task}")
                results.append({"step": step, "success": True, "output": answer})

        overall_ok = all(r.get("success", True) for r in results)
        summary = self._llm(
            f"Summarize what was accomplished:\nTask: {task}\nResults: {json.dumps(results, indent=2)}"
        )

        return Step(kind="act", content={"output": summary, "results": results}, ok=overall_ok)

    def _reflect(self, task: str, action: Step) -> Step:
        """What worked, what didn't, and how should we grow?"""
        prompt = f"""You are an autonomous self-improving AI. Reflect on this task execution.

Task: {task}
Success: {action.ok}
Output: {action.content.get('output', '')[:500]}

Identify:
1. What worked well
2. What capability gap caused any failure
3. Whether writing a new tool would help future tasks like this

Reply with JSON only:
{{
  "worked": "what went well",
  "gap": "what capability was missing, or null",
  "should_evolve": true/false,
  "evolution_description": "what new tool/capability to build",
  "learned": ["insight 1", "insight 2"],
  "priority": "high/medium/low"
}}"""

        raw = self._llm(prompt)
        data = _parse_json(raw) or {"should_evolve": False, "learned": [], "worked": ""}
        return Step(kind="reflect", content=data)

    # ── Evolution ────────────────────────────────────────────

    def _evolve(self, task: str, reflection: Step) -> bool:
        """Write and integrate a new capability based on reflection."""
        desc = reflection.content.get("evolution_description", "")
        if not desc:
            return False

        log.info(f"Evolving: {desc[:80]}...")

        tool = self.writer.write_tool(desc, context=task)
        if not tool:
            log.warning("Code generation failed during evolution")
            return False

        result = self.integrator.integrate(tool)
        if result["ok"]:
            self.state.generation += 1
            self.state.tools.append(tool.get("name"))
            self.evo.record(
                generation=self.state.generation,
                trigger=task,
                new_tool=tool.get("name"),
                description=desc,
                test_results=result.get("test_results"),
            )
            log.info(f"Evolution complete. Generation {self.state.generation}. New tool: {tool.get('name')}")
            return True
        else:
            log.warning(f"Tool failed testing, not integrated: {result.get('error')}")
            return False

    # ── Helpers ──────────────────────────────────────────────

    def _llm(self, prompt: str) -> str:
        if not self.llm:
            return f"[no-llm] {prompt[:80]}..."
        try:
            r = self.llm.messages.create(
                model=self.config.get("llm", {}).get("model", "claude-opus-4-5-20251101"),
                max_tokens=self.config.get("llm", {}).get("max_tokens", 4096),
                messages=[{"role": "user", "content": prompt}],
            )
            return r.content[0].text
        except Exception as e:
            log.error(f"LLM error: {e}")
            return "{}"

    def _print_step(self, step: Step):
        icons = {"perceive": "👁", "plan": "🧠", "act": "⚡", "reflect": "💭"}
        print(f"\n{icons.get(step.kind, '•')} [{step.kind.upper()}]")
        if isinstance(step.content, dict):
            for k, v in step.content.items():
                if v and k not in ("past_relevant",):
                    print(f"   {k}: {str(v)[:120]}")
        else:
            print(f"   {str(step.content)[:200]}")


def _parse_json(text: str) -> Optional[dict]:
    import re
    text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`")
    for pattern in [r"\{.*\}", r"\[.*\]"]:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return None
