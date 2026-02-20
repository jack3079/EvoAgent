"""
CodeWriter — LLM-driven code generation

Turns natural language descriptions into working Python tool functions.
The generated tools follow a simple contract:
    func(**kwargs) -> {"success": bool, "output": Any}
"""

import re
import json
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

# System prompt for all code generation
SYSTEM = """You are an expert Python code generator for an autonomous self-evolving AI agent.

Your job: write clean, working Python functions that tools can call.

CONTRACT every function must follow:
- Accept keyword arguments
- Return dict: {"success": True/False, "output": <result>}
- Handle all exceptions internally (never raise)
- Be self-contained (imports inside the function body)

STYLE:
- Write real, working code — not pseudocode or stubs
- Keep it concise but complete
- Use Python stdlib when possible; pip packages only if essential
"""


class CodeWriter:
    """Writes tool code using the LLM backend."""

    def __init__(self, llm_config: dict, llm=None):
        self.config = llm_config
        self.llm = llm
        self.model = llm_config.get("model", "claude-opus-4-5-20251101")
        self.max_tokens = llm_config.get("max_tokens", 4096)

    def write_tool(self, description: str, context: str = "") -> Optional[dict]:
        """
        Generate a complete tool from a natural language description.

        Returns a tool dict:
        {
            "name": "tool-name",
            "func_name": "tool_name",
            "description": "...",
            "parameters": {"param": "description"},
            "code": "def tool_name(**kwargs): ...",
            "test_cases": [{"input": {}, "expect_success": true}],
        }
        """
        prompt = f"""Write a Python tool function for this capability:

DESCRIPTION: {description}
CONTEXT (when this will be used): {context}

Return JSON only — no markdown, no explanation:
{{
  "name": "kebab-case-name",
  "func_name": "snake_case_name",
  "description": "one sentence describing what it does and returns",
  "parameters": {{"param_name": "what it is"}},
  "code": "def snake_case_name(**kwargs):\\n    import ...\\n    try:\\n        ...\\n        return {{\"success\": True, \"output\": result}}\\n    except Exception as e:\\n        return {{\"success\": False, \"output\": None, \"error\": str(e)}}",
  "test_cases": [
    {{"input": {{}}, "expect_success": true, "label": "basic usage"}},
    {{"input": {{"bad": "input"}}, "expect_success": false, "label": "error handling"}}
  ]
}}

IMPORTANT: The "code" field must be real, complete, working Python — not a placeholder."""

        raw = self._call(prompt)
        tool = self._parse(raw)

        if not tool:
            log.warning(f"Failed to parse tool from LLM response for: {description[:50]}")
            return None

        tool["created_at"] = datetime.utcnow().isoformat()
        tool["source"] = "generated"
        log.info(f"Tool written: {tool.get('name', '?')}")
        return tool

    def rewrite_tool(self, tool: dict, problem: str) -> Optional[dict]:
        """
        Rewrite a failing tool to fix a specific problem.
        Bumps the version and preserves the original code as previous_code.
        """
        prompt = f"""This tool has a problem. Fix it.

ORIGINAL TOOL:
name: {tool.get('name')}
description: {tool.get('description')}
code:
{tool.get('code', '')}

PROBLEM: {problem}

Return the complete fixed tool as JSON (same schema as before, with corrected "code").
Return JSON only."""

        raw = self._call(prompt)
        fixed = self._parse(raw)
        if not fixed:
            return None

        # Preserve version history
        fixed["previous_code"] = tool.get("code")
        v = tool.get("version", "1.0.0").split(".")
        v[-1] = str(int(v[-1]) + 1)
        fixed["version"] = ".".join(v)
        fixed["fixed_at"] = datetime.utcnow().isoformat()
        return fixed

    def write_improvement(self, capability_gap: str, agent_context: dict) -> Optional[dict]:
        """
        Given a capability gap identified through reflection,
        generate the best tool to fill it.
        """
        existing_tools = agent_context.get("tools", [])
        prompt = f"""An AI agent identified this capability gap after failing a task:

GAP: {capability_gap}

Existing tools (don't duplicate): {existing_tools}

Design and write the best Python tool to fill this gap.
Return JSON only (same tool schema as always)."""

        raw = self._call(prompt)
        return self._parse(raw)

    # ── Internal ────────────────────────────────────────────

    def _call(self, prompt: str) -> str:
        if not self.llm:
            return "{}"
        try:
            r = self.llm.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return r.content[0].text
        except Exception as e:
            log.error(f"LLM call failed: {e}")
            return "{}"

    def _parse(self, text: str) -> Optional[dict]:
        text = re.sub(r"```(?:json|python)?\n?", "", text).strip().rstrip("`")
        # Try direct parse
        try:
            d = json.loads(text)
            if isinstance(d, dict) and "code" in d:
                return d
        except Exception:
            pass
        # Try to find JSON object
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                d = json.loads(m.group())
                if isinstance(d, dict) and "code" in d:
                    return d
            except Exception:
                pass
        return None
