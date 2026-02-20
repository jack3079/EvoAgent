"""
Integrator — Automatically merges new tools into the agent's library.

No approval. No human gate.
A new tool either passes its own tests or it doesn't.
If it passes → it's in. If it fails → it's logged, and the agent can retry.
"""

import logging
from .memory import Memory
from .executor import Executor

log = logging.getLogger(__name__)


class Integrator:
    """
    Tests new tools and integrates passing ones immediately.

    The integration cycle:
        1. Run the tool's test cases via Executor
        2. If pass_rate >= threshold → save to Memory
        3. If fail → log the failure details for potential retry
    """

    def __init__(self, memory: Memory, executor: Executor, pass_threshold: float = 0.75):
        self.memory = memory
        self.executor = executor
        self.threshold = pass_threshold

    def integrate(self, tool: dict) -> dict:
        """
        Test and integrate a tool.

        Returns:
            {
                "ok": bool,
                "tool_name": str,
                "pass_rate": float,
                "test_results": [...],
                "error": str | None,
            }
        """
        name = tool.get("name", "unnamed")
        log.info(f"Testing tool for integration: {name}")

        test_result = self.executor.test_tool(tool)

        if test_result["passed"]:
            self.memory.save_tool(tool)
            log.info(
                f"Integrated: {name} "
                f"({test_result['passed_count']}/{test_result['total_count']} tests, "
                f"{test_result['pass_rate']:.0%})"
            )
            return {
                "ok": True,
                "tool_name": name,
                "pass_rate": test_result["pass_rate"],
                "test_results": test_result["results"],
                "error": None,
            }
        else:
            log.warning(
                f"Not integrated: {name} — "
                f"{test_result.get('pass_rate', 0):.0%} pass rate "
                f"(need {self.threshold:.0%}) | {test_result.get('error', '')}"
            )
            return {
                "ok": False,
                "tool_name": name,
                "pass_rate": test_result.get("pass_rate", 0.0),
                "test_results": test_result.get("results", []),
                "error": test_result.get("error") or "did not meet pass threshold",
            }

    def force_integrate(self, tool: dict) -> dict:
        """
        Skip testing and integrate a tool directly.
        Useful when you know what you're doing and just want it in the library.
        """
        name = tool.get("name", "unnamed")
        self.memory.save_tool(tool)
        log.info(f"Force-integrated (no tests): {name}")
        return {"ok": True, "tool_name": name, "pass_rate": None, "test_results": [], "error": None}

    def upgrade(self, tool_name: str, new_tool: dict) -> dict:
        """
        Replace an existing tool with a new version.
        The old version is archived in memory before replacement.
        """
        old = self.memory.get_tool(tool_name)
        if old:
            self.memory.archive_tool(old)
        return self.integrate(new_tool)
