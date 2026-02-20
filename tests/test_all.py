"""
Tests for EvoAgent.

Run: pytest tests/ -v
Run fast (skip slow executor tests): pytest tests/ -v -m "not slow"
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Built-in Tool Tests ─────────────────────────────────

class TestBuiltins:

    def test_text_analyze_basic(self):
        from tools.builtins import text_analyze
        r = text_analyze(text="Hello world. This is EvoAgent. It learns.")
        assert r["success"]
        assert r["output"]["words"] == 7
        assert r["output"]["sentences"] == 3

    def test_text_analyze_empty(self):
        from tools.builtins import text_analyze
        r = text_analyze(text="")
        assert not r["success"]

    def test_math_eval_basic(self):
        from tools.builtins import math_eval
        r = math_eval(expression="2 + 3 * 4")
        assert r["success"]
        assert r["output"]["result"] == 14

    def test_math_eval_sqrt(self):
        from tools.builtins import math_eval
        r = math_eval(expression="sqrt(144)")
        assert r["success"]
        assert r["output"]["result"] == 12.0

    def test_math_eval_trig(self):
        from tools.builtins import math_eval
        import math
        r = math_eval(expression="round(sin(pi/2), 5)")
        assert r["success"]
        assert r["output"]["result"] == 1.0

    def test_math_eval_division_by_zero(self):
        from tools.builtins import math_eval
        r = math_eval(expression="1/0")
        assert not r["success"]
        assert "zero" in r["error"].lower()

    def test_math_eval_no_expr(self):
        from tools.builtins import math_eval
        r = math_eval()
        assert not r["success"]

    def test_json_query_parse(self):
        from tools.builtins import json_query
        r = json_query(json_string='{"name":"EvoAgent","version":2}')
        assert r["success"]
        assert r["output"]["type"] == "dict"

    def test_json_query_path(self):
        from tools.builtins import json_query
        raw = '{"data":{"users":[{"name":"Alice"},{"name":"Bob"}]}}'
        r = json_query(json_string=raw, query="data.users.1.name")
        assert r["success"]
        assert r["output"]["result"] == "Bob"

    def test_json_query_invalid(self):
        from tools.builtins import json_query
        r = json_query(json_string="{invalid}")
        assert not r["success"]

    def test_datetime_now(self):
        from tools.builtins import datetime_now
        r = datetime_now()
        assert r["success"]
        assert "iso" in r["output"]
        assert r["output"]["iso"].endswith("Z")

    def test_datetime_diff(self):
        from tools.builtins import datetime_diff
        r = datetime_diff(date1="2024-01-01T00:00:00", date2="2024-01-15T00:00:00")
        assert r["success"]
        assert r["output"]["days"] == 14

    def test_string_transform_upper(self):
        from tools.builtins import string_transform
        r = string_transform(text="hello", operation="upper")
        assert r["success"]
        assert r["output"]["result"] == "HELLO"

    def test_string_transform_reverse(self):
        from tools.builtins import string_transform
        r = string_transform(text="abc", operation="reverse")
        assert r["success"]
        assert r["output"]["result"] == "cba"

    def test_string_transform_contains(self):
        from tools.builtins import string_transform
        r = string_transform(text="EvoAgent is cool", operation="contains", substring="cool")
        assert r["success"]
        assert r["output"]["result"] is True

    def test_string_transform_bad_op(self):
        from tools.builtins import string_transform
        r = string_transform(text="x", operation="nonexistent")
        assert not r["success"]


# ── Memory Tests ────────────────────────────────────────

class TestMemory:

    @pytest.fixture
    def mem(self, tmp_path):
        from core.memory import Memory
        return Memory({"base_path": str(tmp_path / "memory")})

    def test_save_and_get_tool(self, mem):
        tool = {"name": "my-tool", "func_name": "my_tool", "description": "does stuff"}
        mem.save_tool(tool)
        assert mem.get_tool("my-tool") is not None

    def test_all_tools(self, mem):
        mem.save_tool({"name": "t1", "description": "a"})
        mem.save_tool({"name": "t2", "description": "b"})
        assert len(mem.all_tools()) == 2

    def test_recall_relevant(self, mem):
        mem.store({"task": "analyze CSV file", "success": True, "learned": ["CSV parsing works"]})
        mem.store({"task": "parse JSON response", "success": True, "learned": []})
        hits = mem.recall("CSV data analysis")
        assert any("CSV" in h["task"] for h in hits)

    def test_best_tool_for(self, mem):
        mem.save_tool({"name": "csv-parser", "description": "parse CSV files into rows"})
        mem.save_tool({"name": "json-parser", "description": "parse JSON strings"})
        t = mem.best_tool_for("parse a CSV file into rows")
        assert t is not None
        assert t["name"] == "csv-parser"

    def test_delete_tool(self, mem):
        mem.save_tool({"name": "temp-tool", "description": "temp"})
        mem.delete_tool("temp-tool")
        assert mem.get_tool("temp-tool") is None


# ── Executor Tests ──────────────────────────────────────

class TestExecutor:

    @pytest.fixture
    def ex(self):
        from core.executor import Executor
        return Executor({"timeout": 10})

    def test_run_simple_code(self, ex):
        code = """
def add(**kwargs):
    a, b = kwargs.get('a', 0), kwargs.get('b', 0)
    return {"success": True, "output": a + b}
"""
        r = ex.run_code(code, "add", {"a": 3, "b": 4})
        assert r["ok"]
        assert r["output"]["output"] == 7

    def test_run_code_exception(self, ex):
        code = """
def crash(**kwargs):
    raise ValueError("intentional crash")
"""
        r = ex.run_code(code, "crash", {})
        assert not r["ok"] or (r["ok"] and r["output"].get("success") is False)

    @pytest.mark.slow
    def test_timeout(self, ex):
        ex.timeout = 2
        code = """
def hang(**kwargs):
    import time
    time.sleep(999)
    return {"success": True, "output": "done"}
"""
        r = ex.run_code(code, "hang", {})
        assert not r["ok"]
        assert "timed out" in r.get("error", "").lower()

    def test_test_tool_passes(self, ex):
        tool = {
            "name": "adder",
            "func_name": "add",
            "code": "def add(**kwargs):\n    a, b = kwargs.get('a',0), kwargs.get('b',0)\n    return {'success': True, 'output': a+b}",
            "test_cases": [
                {"input": {"a": 2, "b": 3}, "expect_success": True, "label": "basic add"},
            ]
        }
        r = ex.test_tool(tool)
        assert r["passed"]
        assert r["pass_rate"] == 1.0

    def test_syntax_check_fail(self, ex):
        tool = {
            "name": "broken",
            "func_name": "broken",
            "code": "def broken(\n    pass",
            "test_cases": [{"input": {}, "expect_success": True, "label": "t1"}]
        }
        r = ex.test_tool(tool)
        assert not r["passed"]
        assert "SyntaxError" in r.get("error", "")


# ── Evolution Log Tests ─────────────────────────────────

class TestEvolutionLog:

    @pytest.fixture
    def evo(self, tmp_path):
        from core.evolution import EvolutionLog
        return EvolutionLog({"log_path": str(tmp_path / "history.json")})

    def test_record(self, evo):
        evo.record(1, "failed on CSV task", "csv-reader", "reads CSV files")
        assert len(evo.history) == 1
        assert evo.history[0]["generation"] == 1

    def test_timeline(self, evo):
        evo.record(1, "trigger A", "tool-a", "desc a")
        evo.record(2, "trigger B", "tool-b", "desc b")
        tl = evo.timeline()
        assert len(tl) == 2
        assert tl[1]["gen"] == 2

    def test_report(self, evo):
        evo.record(1, "some trigger task", "my-tool", "does something")
        r = evo.report()
        assert "my-tool" in r
        assert "Gen   1" in r


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
