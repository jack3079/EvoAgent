"""
Executor — Runs generated code in subprocesses.

Why subprocess?
    Not restriction. Pure engineering.
    AI-generated code has bugs. When it segfaults, OOMs, or infinite-loops,
    you want that to happen in a child process — not kill the agent itself.
    The subprocess boundary is what lets the agent iterate fast and survive failures.

There is no whitelist, no keyword filter, no "dangerous code" blocking.
The only constraint: a configurable timeout so hung processes don't stall the loop.
"""

import sys
import json
import time
import logging
import textwrap
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)


class Executor:
    """Runs Python code (from tools or raw strings) in a subprocess."""

    def __init__(self, config: dict = None):
        config = config or {}
        self.timeout = config.get("timeout", 30)        # seconds per run
        self.python = config.get("python", sys.executable)

    # ── Public API ───────────────────────────────────────────

    def run_tool(self, tool: dict, task: str = "", kwargs: dict = None) -> dict:
        """
        Execute a stored tool dict against a given task/input.
        The tool's function is called with `kwargs` (or {"task": task} if not provided).

        Returns: {"ok": bool, "output": Any, "error": str|None, "elapsed": float}
        """
        code = tool.get("code", "")
        func_name = tool.get("func_name", "")
        if not code or not func_name:
            return {"ok": False, "output": None, "error": "tool missing code or func_name"}

        call_args = kwargs or ({"task": task} if task else {})
        runner = self._build_runner(code, func_name, call_args)
        return self._run(runner)

    def run_code(self, code: str, func_name: str, kwargs: dict = None) -> dict:
        """
        Execute arbitrary code string. No filtering.
        Returns: {"ok": bool, "output": Any, "error": str|None, "elapsed": float}
        """
        runner = self._build_runner(code, func_name, kwargs or {})
        return self._run(runner)

    def test_tool(self, tool: dict) -> dict:
        """
        Run all test_cases defined in a tool dict.
        Returns: {"passed": bool, "pass_rate": float, "results": [...], "error": str|None}
        """
        code = tool.get("code", "")
        func_name = tool.get("func_name", "")
        test_cases = tool.get("test_cases", [])

        # Syntax check first
        ok, err = _syntax_check(code)
        if not ok:
            return {"passed": False, "pass_rate": 0.0, "results": [], "error": f"SyntaxError: {err}"}

        if not test_cases:
            # No test cases → treat as passing if syntax is ok
            return {"passed": True, "pass_rate": 1.0, "results": [], "error": None}

        results = []
        passed = 0
        for tc in test_cases:
            inp = tc.get("input", {})
            expect_ok = tc.get("expect_success", True)
            label = tc.get("label", "unnamed")

            r = self.run_code(code, func_name, inp)
            actual_ok = r["ok"] and (r.get("output") is not None or expect_ok is False)

            # More precise: check the returned dict's "success" key if present
            if r["ok"] and isinstance(r.get("output"), dict):
                actual_ok = r["output"].get("success", True)

            hit = (actual_ok == expect_ok)
            if hit:
                passed += 1

            results.append({
                "label": label,
                "passed": hit,
                "expected_success": expect_ok,
                "actual_success": actual_ok,
                "output": r.get("output"),
                "error": r.get("error"),
                "elapsed": r.get("elapsed"),
            })

        total = len(test_cases)
        rate = passed / total
        return {
            "passed": rate >= 0.75,   # 75% threshold — be lenient for generated code
            "pass_rate": rate,
            "passed_count": passed,
            "total_count": total,
            "results": results,
            "error": None,
        }

    # ── Internal ─────────────────────────────────────────────

    def _build_runner(self, code: str, func_name: str, kwargs: dict) -> str:
        """Build a self-contained Python script that runs the tool and prints JSON result."""
        safe_kwargs = json.dumps(kwargs, default=str)
        runner = textwrap.dedent(f"""
import json, sys

{code}

try:
    kwargs = {safe_kwargs}
    result = {func_name}(**kwargs)
    print(json.dumps({{"ok": True, "output": result}}, default=str))
except Exception as e:
    print(json.dumps({{"ok": False, "output": None, "error": str(e)}}))
""")
        return runner

    def _run(self, script: str) -> dict:
        """Write script to temp file and run it in subprocess."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(script)
            tmp = f.name

        start = time.time()
        try:
            proc = subprocess.run(
                [self.python, tmp],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            elapsed = time.time() - start

            stdout = proc.stdout.strip()
            if stdout:
                try:
                    data = json.loads(stdout)
                    data["elapsed"] = elapsed
                    return data
                except json.JSONDecodeError:
                    return {"ok": True, "output": stdout, "elapsed": elapsed, "error": None}
            else:
                stderr = proc.stderr.strip()
                return {"ok": False, "output": None, "error": stderr or "no output", "elapsed": elapsed}

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            return {"ok": False, "output": None, "error": f"timed out after {self.timeout}s", "elapsed": elapsed}
        except Exception as e:
            return {"ok": False, "output": None, "error": str(e), "elapsed": time.time() - start}
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _syntax_check(code: str) -> tuple[bool, Optional[str]]:
    try:
        compile(code, "<generated>", "exec")
        return True, None
    except SyntaxError as e:
        return False, str(e)
