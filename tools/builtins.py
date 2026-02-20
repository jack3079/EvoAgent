"""
Built-in Tools — starter capabilities for EvoAgent.

These are hand-written, production-quality tools that come pre-loaded.
The agent will add more via code generation. These are just the starting point.

Every tool follows the contract:
    func(**kwargs) -> {"success": bool, "output": Any}
"""

import re
import json
import math
from datetime import datetime


# ── Text ──────────────────────────────────────────────────

def text_analyze(**kwargs) -> dict:
    """Analyze a text string: word count, sentence count, top keywords."""
    try:
        text = kwargs.get("text", "")
        if not text:
            return {"success": False, "output": None, "error": "text is required"}

        words = text.split()
        sentences = [s.strip() for s in re.split(r"[.!?。！？]", text) if s.strip()]
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        freq: dict = {}
        for w in words:
            w = re.sub(r"[^\w]", "", w.lower())
            if len(w) > 3:
                freq[w] = freq.get(w, 0) + 1

        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return {
            "success": True,
            "output": {
                "chars": len(text),
                "words": len(words),
                "sentences": len(sentences),
                "paragraphs": len(paragraphs),
                "avg_words_per_sentence": round(len(words) / max(1, len(sentences)), 1),
                "top_keywords": [{"word": w, "count": c} for w, c in top],
            }
        }
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}


# ── Math ─────────────────────────────────────────────────

def math_eval(**kwargs) -> dict:
    """Evaluate a math expression safely (no exec, no eval of arbitrary code)."""
    try:
        expr = kwargs.get("expression", "")
        if not expr:
            return {"success": False, "output": None, "error": "expression is required"}

        allowed = {
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "log2": math.log2,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
            "floor": math.floor, "ceil": math.ceil, "factorial": math.factorial,
            "pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf,
        }
        result = eval(expr, {"__builtins__": {}}, allowed)  # noqa: S307
        return {"success": True, "output": {"expression": expr, "result": result}}
    except ZeroDivisionError:
        return {"success": False, "output": None, "error": "division by zero"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}


# ── JSON ─────────────────────────────────────────────────

def json_query(**kwargs) -> dict:
    """Parse a JSON string and optionally query a dot-notation path."""
    try:
        raw = kwargs.get("json_string", "")
        query = kwargs.get("query", "")
        data = json.loads(raw)
        if query:
            node = data
            for part in query.split("."):
                if isinstance(node, dict):
                    node = node[part]
                elif isinstance(node, list):
                    node = node[int(part)]
                else:
                    return {"success": False, "output": None, "error": f"cannot traverse {type(node)} at '{part}'"}
            return {"success": True, "output": {"result": node, "query": query}}
        return {
            "success": True,
            "output": {
                "type": type(data).__name__,
                "length": len(data) if isinstance(data, (list, dict)) else None,
                "formatted": json.dumps(data, indent=2),
            }
        }
    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        return {"success": False, "output": None, "error": str(e)}


# ── DateTime ─────────────────────────────────────────────

def datetime_now(**kwargs) -> dict:
    """Return the current UTC datetime in multiple formats."""
    try:
        now = datetime.utcnow()
        fmt = kwargs.get("format", "%Y-%m-%d %H:%M:%S")
        return {
            "success": True,
            "output": {
                "iso": now.isoformat() + "Z",
                "formatted": now.strftime(fmt),
                "timestamp": now.timestamp(),
                "year": now.year, "month": now.month, "day": now.day,
                "weekday": now.strftime("%A"),
            }
        }
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}


def datetime_diff(**kwargs) -> dict:
    """Compute the difference between two ISO datetime strings."""
    try:
        d1 = datetime.fromisoformat(kwargs.get("date1", "").rstrip("Z"))
        d2 = datetime.fromisoformat(kwargs.get("date2", "").rstrip("Z"))
        delta = abs(d2 - d1)
        return {
            "success": True,
            "output": {
                "days": delta.days,
                "hours": delta.seconds // 3600,
                "minutes": (delta.seconds % 3600) // 60,
                "total_seconds": delta.total_seconds(),
            }
        }
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}


# ── String Ops ───────────────────────────────────────────

def string_transform(**kwargs) -> dict:
    """Transform a string: upper, lower, title, reverse, count, split."""
    try:
        text = kwargs.get("text", "")
        op = kwargs.get("operation", "").lower()
        ops = {
            "upper": text.upper,
            "lower": text.lower,
            "title": text.title,
            "strip": text.strip,
            "reverse": lambda: text[::-1],
            "count": lambda: len(text),
            "split": lambda: text.split(kwargs.get("delimiter", " ")),
            "replace": lambda: text.replace(kwargs.get("old", ""), kwargs.get("new", "")),
            "contains": lambda: kwargs.get("substring", "") in text,
        }
        if op not in ops:
            return {"success": False, "output": None, "error": f"unknown operation '{op}'. Available: {list(ops)}"}
        return {"success": True, "output": {"result": ops[op](), "operation": op}}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}


# ── Registry ─────────────────────────────────────────────

BUILTIN_TOOLS = [
    {
        "name": "text-analyze",
        "func_name": "text_analyze",
        "description": "Analyze text: word count, sentence count, top keywords",
        "parameters": {"text": "the text string to analyze"},
        "code": None,   # loaded from this module directly
        "source": "builtin",
        "version": "1.0.0",
    },
    {
        "name": "math-eval",
        "func_name": "math_eval",
        "description": "Evaluate a math expression: supports arithmetic, sqrt, trig, log, etc.",
        "parameters": {"expression": "math expression string e.g. 'sqrt(16) + 2'"},
        "code": None,
        "source": "builtin",
        "version": "1.0.0",
    },
    {
        "name": "json-query",
        "func_name": "json_query",
        "description": "Parse a JSON string and optionally query it with a dot-notation path",
        "parameters": {"json_string": "raw JSON string", "query": "(optional) dot-path e.g. 'data.users.0.name'"},
        "code": None,
        "source": "builtin",
        "version": "1.0.0",
    },
    {
        "name": "datetime-now",
        "func_name": "datetime_now",
        "description": "Get current UTC datetime in ISO, formatted, and timestamp formats",
        "parameters": {"format": "(optional) strftime format string"},
        "code": None,
        "source": "builtin",
        "version": "1.0.0",
    },
    {
        "name": "datetime-diff",
        "func_name": "datetime_diff",
        "description": "Calculate the difference between two ISO datetime strings",
        "parameters": {"date1": "ISO datetime string", "date2": "ISO datetime string"},
        "code": None,
        "source": "builtin",
        "version": "1.0.0",
    },
    {
        "name": "string-transform",
        "func_name": "string_transform",
        "description": "Transform strings: upper, lower, title, reverse, split, replace, contains",
        "parameters": {"text": "input string", "operation": "operation name", "delimiter": "(optional)", "old": "(optional)", "new": "(optional)"},
        "code": None,
        "source": "builtin",
        "version": "1.0.0",
    },
]
