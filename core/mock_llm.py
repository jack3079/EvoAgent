"""
MockLLM — Simulates a real LLM for offline demo and testing.

Returns realistic, varied responses based on prompt content.
This lets you run the full evolution loop without an API key.
"""

import json
import random
import re
from datetime import datetime


class MockLLM:
    """Drop-in replacement for the Anthropic client. No API key needed."""

    def __init__(self, simulate_failures: bool = False):
        self.calls = 0
        self.simulate_failures = simulate_failures
        self.failed_tasks = set()  # Track which tasks have failed once
        self.messages = _MockMessages(self)

    def _respond(self, prompt: str) -> str:
        self.calls += 1
        p = prompt.lower()

        # ── Plan responses ───────────────────────────────────
        if '"steps"' in prompt or "execution plan" in p or "create a concise" in p:
            if "csv" in p:
                return json.dumps({
                    "steps": ["Read the CSV file", "Parse rows into structured data", "Summarize the contents"],
                    "tools_to_use": ["csv-reader"],
                    "need_new_tool": True,
                    "new_tool_description": "Read a CSV file and return its rows and column headers as structured data",
                    "confidence": 0.85
                })
            elif "weather" in p or "temperature" in p:
                return json.dumps({
                    "steps": ["Fetch current weather data", "Format the result"],
                    "tools_to_use": ["http-get"],
                    "need_new_tool": True,
                    "new_tool_description": "Fetch weather data from a public API given a city name",
                    "confidence": 0.78
                })
            elif "sort" in p or "list" in p or "array" in p:
                return json.dumps({
                    "steps": ["Parse the input list", "Apply sorting algorithm", "Return sorted result"],
                    "tools_to_use": ["list-sorter"],
                    "need_new_tool": True,
                    "new_tool_description": "Sort a list of items with configurable order (asc/desc) and key function",
                    "confidence": 0.92
                })
            elif "file" in p or "read" in p or "write" in p:
                return json.dumps({
                    "steps": ["Open the target file", "Process contents", "Return result"],
                    "tools_to_use": ["file-reader"],
                    "need_new_tool": True,
                    "new_tool_description": "Read a file from disk and return its contents with metadata",
                    "confidence": 0.88
                })
            elif "count" in p or "statistics" in p or "average" in p:
                return json.dumps({
                    "steps": ["Collect the numbers", "Compute statistics", "Format output"],
                    "tools_to_use": ["stats-calculator"],
                    "need_new_tool": True,
                    "new_tool_description": "Calculate descriptive statistics (mean, median, std, min, max) for a list of numbers",
                    "confidence": 0.95
                })
            else:
                return json.dumps({
                    "steps": ["Analyze the task requirements", "Execute with available tools", "Summarize results"],
                    "tools_to_use": [],
                    "need_new_tool": False,
                    "new_tool_description": "",
                    "confidence": 0.70
                })

        # ── Tool generation responses ────────────────────────
        elif '"func_name"' in prompt or "write a python tool" in p or "python tool function" in p:
            if "csv" in p:
                return json.dumps({
                    "name": "csv-reader",
                    "func_name": "csv_reader",
                    "description": "Read a CSV file and return its rows and column headers",
                    "parameters": {"filepath": "path to the CSV file", "delimiter": "column delimiter (default: comma)"},
                    "code": '''def csv_reader(**kwargs):
    import csv
    import os
    filepath = kwargs.get("filepath", "")
    delimiter = kwargs.get("delimiter", ",")
    try:
        if not filepath:
            return {"success": False, "output": None, "error": "filepath is required"}
        if not os.path.exists(filepath):
            # Demo mode: return fake data
            return {"success": True, "output": {
                "columns": ["name", "age", "city"],
                "rows": [{"name": "Alice", "age": "30", "city": "NYC"},
                         {"name": "Bob", "age": "25", "city": "LA"}],
                "row_count": 2
            }}
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
        return {"success": True, "output": {
            "columns": list(rows[0].keys()) if rows else [],
            "rows": rows,
            "row_count": len(rows)
        }}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}''',
                    "test_cases": [
                        {"input": {"filepath": "nonexistent.csv"}, "expect_success": True, "label": "demo mode fallback"},
                        {"input": {}, "expect_success": False, "label": "missing filepath"}
                    ]
                })
            elif "sort" in p or "list" in p:
                return json.dumps({
                    "name": "list-sorter",
                    "func_name": "list_sorter",
                    "description": "Sort a list of items with configurable order",
                    "parameters": {"items": "list to sort", "reverse": "sort descending if true"},
                    "code": '''def list_sorter(**kwargs):
    try:
        items = kwargs.get("items", [])
        reverse = kwargs.get("reverse", False)
        if not isinstance(items, list):
            return {"success": False, "output": None, "error": "items must be a list"}
        sorted_items = sorted(items, reverse=reverse)
        return {"success": True, "output": {
            "sorted": sorted_items,
            "length": len(sorted_items),
            "order": "descending" if reverse else "ascending"
        }}
    except TypeError as e:
        return {"success": False, "output": None, "error": f"Cannot sort mixed types: {e}"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}''',
                    "test_cases": [
                        {"input": {"items": [3, 1, 4, 1, 5, 9, 2, 6]}, "expect_success": True, "label": "sort numbers"},
                        {"input": {"items": ["banana", "apple", "cherry"], "reverse": True}, "expect_success": True, "label": "sort strings desc"},
                        {"input": {"items": "not a list"}, "expect_success": False, "label": "invalid input"}
                    ]
                })
            elif "stat" in p or "average" in p or "mean" in p:
                return json.dumps({
                    "name": "stats-calculator",
                    "func_name": "stats_calculator",
                    "description": "Calculate descriptive statistics for a list of numbers",
                    "parameters": {"numbers": "list of numeric values"},
                    "code": '''def stats_calculator(**kwargs):
    import math
    try:
        nums = kwargs.get("numbers", [])
        if not nums:
            return {"success": False, "output": None, "error": "numbers list is empty"}
        nums = [float(n) for n in nums]
        n = len(nums)
        mean = sum(nums) / n
        sorted_nums = sorted(nums)
        mid = n // 2
        median = sorted_nums[mid] if n % 2 else (sorted_nums[mid-1] + sorted_nums[mid]) / 2
        variance = sum((x - mean) ** 2 for x in nums) / n
        std = math.sqrt(variance)
        return {"success": True, "output": {
            "count": n,
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std": round(std, 4),
            "min": min(nums),
            "max": max(nums),
            "range": max(nums) - min(nums),
            "sum": sum(nums)
        }}
    except ValueError as e:
        return {"success": False, "output": None, "error": f"Non-numeric value: {e}"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}''',
                    "test_cases": [
                        {"input": {"numbers": [1, 2, 3, 4, 5]}, "expect_success": True, "label": "basic stats"},
                        {"input": {"numbers": [100, 200, 300]}, "expect_success": True, "label": "larger numbers"},
                        {"input": {"numbers": []}, "expect_success": False, "label": "empty list"}
                    ]
                })
            elif "file" in p or "read" in p:
                return json.dumps({
                    "name": "file-reader",
                    "func_name": "file_reader",
                    "description": "Read a file and return its contents with metadata",
                    "parameters": {"filepath": "path to file", "encoding": "file encoding (default: utf-8)"},
                    "code": '''def file_reader(**kwargs):
    import os
    filepath = kwargs.get("filepath", "")
    encoding = kwargs.get("encoding", "utf-8")
    try:
        if not filepath:
            return {"success": False, "output": None, "error": "filepath is required"}
        if not os.path.exists(filepath):
            return {"success": False, "output": None, "error": f"File not found: {filepath}"}
        size = os.path.getsize(filepath)
        with open(filepath, "r", encoding=encoding) as f:
            content = f.read()
        lines = content.splitlines()
        return {"success": True, "output": {
            "content": content,
            "lines": len(lines),
            "size_bytes": size,
            "encoding": encoding,
            "filepath": filepath
        }}
    except UnicodeDecodeError:
        return {"success": False, "output": None, "error": f"Cannot decode file with {encoding} encoding"}
    except PermissionError:
        return {"success": False, "output": None, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}''',
                    "test_cases": [
                        {"input": {"filepath": "/nonexistent/path.txt"}, "expect_success": False, "label": "missing file"},
                        {"input": {}, "expect_success": False, "label": "no filepath"}
                    ]
                })
            elif "weather" in p or "http" in p:
                return json.dumps({
                    "name": "http-get",
                    "func_name": "http_get",
                    "description": "Make an HTTP GET request and return the response",
                    "parameters": {"url": "target URL", "timeout": "timeout in seconds (default: 10)"},
                    "code": '''def http_get(**kwargs):
    import urllib.request
    import json as _json
    url = kwargs.get("url", "")
    timeout = kwargs.get("timeout", 10)
    try:
        if not url:
            return {"success": False, "output": None, "error": "url is required"}
        with urllib.request.urlopen(url, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            status = response.status
            try:
                body = _json.loads(raw)
            except Exception:
                body = raw
        return {"success": True, "output": {
            "status": status,
            "body": body,
            "url": url
        }}
    except urllib.error.HTTPError as e:
        return {"success": False, "output": None, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}''',
                    "test_cases": [
                        {"input": {}, "expect_success": False, "label": "missing url"},
                        {"input": {"url": "not-a-url"}, "expect_success": False, "label": "invalid url"}
                    ]
                })
            else:
                # Generic tool generation
                task_word = re.search(r'description["\s:]+([a-z\-]+)', p)
                name = task_word.group(1) if task_word else "generic-tool"
                return json.dumps({
                    "name": name,
                    "func_name": name.replace("-", "_"),
                    "description": f"Performs the requested operation: {name}",
                    "parameters": {"input": "input data"},
                    "code": f'''def {name.replace("-", "_")}(**kwargs):
    try:
        data = kwargs.get("input", kwargs)
        return {{"success": True, "output": {{"processed": str(data), "tool": "{name}"}}}}
    except Exception as e:
        return {{"success": False, "output": None, "error": str(e)}}''',
                    "test_cases": [
                        {"input": {"input": "test"}, "expect_success": True, "label": "basic"},
                    ]
                })

        # ── Reflection responses ─────────────────────────────
        elif '"should_evolve"' in prompt or "reflect on this" in p:
            if "failed" in p or "false" in p:
                return json.dumps({
                    "worked": "Agent understood the task and attempted execution",
                    "gap": "Missing specialized tool for this operation",
                    "should_evolve": True,
                    "evolution_description": "Create a new tool to handle this class of task automatically",
                    "learned": [
                        "This type of task requires a dedicated tool",
                        "Will be faster on next attempt with proper tooling"
                    ],
                    "priority": "high"
                })
            else:
                insights = [
                    ["Task completed successfully using available tools",
                     "Pattern recognized: this approach works well for similar inputs"],
                    ["Direct LLM reasoning was sufficient for this task",
                     "No new tools needed for this category"],
                    ["Existing tools handled the request efficiently",
                     "Performance improves with repeated similar tasks"],
                ]
                choice = random.choice(insights)
                return json.dumps({
                    "worked": "Execution went smoothly",
                    "gap": None,
                    "should_evolve": random.random() > 0.6,
                    "evolution_description": "Optimize tool matching for faster capability discovery",
                    "learned": choice,
                    "priority": "medium"
                })

        # ── Summary/output responses ─────────────────────────
        elif "summarize what was accomplished" in p or "summarize" in p:
            if "csv" in p:
                return "Successfully parsed CSV data: found 2 rows with columns [name, age, city]. Data is clean and ready for analysis."
            elif "sort" in p:
                return "Sorted the list successfully. Items arranged in ascending order."
            elif "stat" in p or "average" in p:
                return "Calculated descriptive statistics: mean, median, standard deviation, min, max computed successfully."
            elif "file" in p:
                return "File operation completed. Contents retrieved and metadata extracted."
            else:
                return "Task executed successfully. Results processed and formatted."

        # ── Default ──────────────────────────────────────────
        else:
            return "Task completed. EvoAgent processed the request using available capabilities."


class _MockMessages:
    def __init__(self, parent):
        self._p = parent

    def create(self, model="", max_tokens=0, messages=None, system="", **kwargs):
        messages = messages or []
        prompt = ""
        for m in messages:
            if isinstance(m.get("content"), str):
                prompt += m["content"] + "\n"
        response = self._p._respond(prompt)
        return _MockResponse(response)


class _MockResponse:
    def __init__(self, text):
        self.content = [_MockContent(text)]


class _MockContent:
    def __init__(self, text):
        self.text = text
        self.type = "text"
