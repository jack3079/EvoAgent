"""
ReflectionEngine — Deep analysis of failures following Kolb's Experiential Learning Cycle

This is the key to ERL: not just "what tool do I need", but:
- WHY did my reasoning fail?
- WHAT pattern should I learn?
- HOW should I adjust my approach?

Implements:
1. Reflective Observation — analyze what went wrong
2. Abstract Conceptualization — extract generalizable principles
"""

import json
import logging
import re
from typing import Optional

log = logging.getLogger(__name__)


class ReflectionEngine:
    """
    Analyzes failed attempts and extracts learning.
    
    Unlike simple reflection ("I need a CSV tool"), deep reflection asks:
    - What was my reasoning error?
    - What assumption was incorrect?
    - What heuristic should I update?
    - What pattern applies to similar tasks?
    """

    def __init__(self, llm=None, config: dict = None):
        self.llm = llm
        self.config = config or {}

    def deep_reflect(
        self,
        task: str,
        attempt_1_output: str,
        attempt_1_success: bool,
        attempt_1_steps: list,
        available_context: dict
    ) -> dict:
        """
        Perform deep reflection on a failed or suboptimal attempt.
        
        Returns reflection dict:
        {
            "reasoning_errors": ["error 1", "error 2"],
            "incorrect_assumptions": ["assumption 1"],
            "learned_pattern": "generalizable principle",
            "revised_approach": "what to do differently",
            "guidance_for_attempt_2": "specific instruction",
            "should_update_policy": bool,
            "policy_principle": {
                "pattern": "when X, do Y",
                "context": "domain",
                "learned_from": task
            }
        }
        """
        log.info(f"Deep reflection on: {task[:60]}...")

        prompt = self._build_reflection_prompt(
            task, attempt_1_output, attempt_1_success, attempt_1_steps, available_context
        )
        
        response = self._call_llm(prompt)
        reflection = self._parse_reflection(response)
        
        # Ensure key fields exist
        reflection.setdefault("reasoning_errors", [])
        reflection.setdefault("learned_pattern", "")
        reflection.setdefault("guidance_for_attempt_2", "")
        reflection.setdefault("should_update_policy", False)
        
        log.info(f"Reflection complete | Update policy: {reflection.get('should_update_policy', False)}")
        
        return reflection

    def reflect_on_success(
        self,
        task: str,
        successful_output: str,
        was_reflection_guided: bool
    ) -> Optional[dict]:
        """
        Extract learning from successful attempts, especially reflection-guided ones.
        
        If the second attempt succeeded after reflection, that validates the learned pattern.
        """
        if not was_reflection_guided:
            return None  # No special learning from first-try success
        
        prompt = f"""A task succeeded after reflection-guided revision.

Original task: {task}

Successful outcome: {successful_output}

This success validates the reflection-guided approach. Extract the key principle that made it work.

Reply with JSON only:
{{
  "validated_pattern": "the reasoning pattern that worked",
  "why_it_worked": "explanation",
  "generalization": "how this applies to similar tasks",
  "policy_update": {{
    "pattern": "when facing X, do Y",
    "context": "domain or task category",
    "confidence": 0.0-1.0
  }}
}}"""

        response = self._call_llm(prompt)
        return self._parse_reflection(response)

    # ── Prompt Construction ──────────────────────────────────

    def _build_reflection_prompt(
        self,
        task: str,
        output: str,
        success: bool,
        steps: list,
        context: dict
    ) -> str:
        """
        Build the deep reflection prompt following Kolb's cycle.
        
        This is THE critical prompt — it determines quality of learning.
        """
        tools_available = context.get("tools_available", [])
        past_experience = context.get("relevant_experience", [])
        
        return f"""You are an AI agent performing DEEP REFLECTION on a task attempt, following Kolb's Experiential Learning Cycle.

## Concrete Experience (what happened)
Task: {task}
Outcome: {"Success" if success else "Failure/Suboptimal"}
Output: {output[:500]}
Steps taken: {json.dumps(steps, indent=2)}
Available tools: {tools_available}
Relevant past experience: {json.dumps(past_experience, indent=2) if past_experience else "None"}

## Reflective Observation (analyze what went wrong)
Deeply analyze this attempt. Don't just say "I need a tool" — that's shallow.
Ask:
1. What was the REASONING ERROR? (Not "missing capability" but "flawed thought process")
2. What ASSUMPTIONS were incorrect?
3. What did I MISUNDERSTAND about the task?
4. What PATTERN did I fail to recognize?
5. If I had a tool, why didn't I use it correctly?

## Abstract Conceptualization (extract principles)
From this experience, what GENERALIZABLE PRINCIPLE should I learn?
- Not: "I need a CSV parser"
- But: "When encountering structured data, first identify format before processing"

## Active Experimentation (plan revised approach)
How should attempt #2 differ? Be SPECIFIC and ACTIONABLE.

Reply with JSON only:
{{
  "reasoning_errors": ["specific error in my thought process", "another error"],
  "incorrect_assumptions": ["what I assumed wrong about the task or data"],
  "misunderstood_aspects": ["what I failed to grasp"],
  "pattern_not_recognized": "what pattern I should have seen",
  
  "learned_pattern": "ONE clear, generalizable principle from this experience",
  "why_this_matters": "why this principle is important",
  
  "revised_approach": "what to do differently in attempt 2",
  "guidance_for_attempt_2": "specific actionable instruction for the next try",
  
  "should_update_policy": true/false,
  "policy_principle": {{
    "pattern": "when facing X situation, apply Y approach",
    "context": "domain this applies to (e.g., 'data analysis', 'text processing')",
    "learned_from": "{task[:80]}",
    "confidence": 0.0-1.0
  }},
  
  "tool_needed": true/false,
  "tool_description": "if a new tool would help, describe it briefly"
}}

Be HONEST and SPECIFIC. Shallow reflection = shallow learning."""

    # ── Helpers ──────────────────────────────────────────────

    def _call_llm(self, prompt: str) -> str:
        if not self.llm:
            return self._mock_reflection_response(prompt)
        
        try:
            response = self.llm.messages.create(
                model=self.config.get("model", "claude-opus-4-5-20251101"),
                max_tokens=self.config.get("max_tokens", 4096),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            log.error(f"LLM call failed: {e}")
            return "{}"

    def _parse_reflection(self, text: str) -> dict:
        text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`")
        for pattern in [r"\{.*\}", r"\[.*\]"]:
            m = re.search(pattern, text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except Exception:
                    pass
        return {}

    def _mock_reflection_response(self, prompt: str) -> str:
        """Realistic mock for offline demo."""
        p = prompt.lower()
        
        if "csv" in p or "data" in p:
            return json.dumps({
                "reasoning_errors": [
                    "Attempted to process data without first validating its structure",
                    "Did not check if input matched expected format"
                ],
                "incorrect_assumptions": [
                    "Assumed data was in a format I could directly process",
                    "Did not consider that data might need parsing first"
                ],
                "learned_pattern": "When encountering structured data, always identify and validate format before attempting operations",
                "why_this_matters": "Many failures come from format mismatches, not missing capabilities",
                "revised_approach": "First inspect data structure, then select appropriate parsing strategy",
                "guidance_for_attempt_2": "Parse the data format, validate structure, then apply operations",
                "should_update_policy": True,
                "policy_principle": {
                    "pattern": "Before processing any structured data, validate format and structure first",
                    "context": "data processing",
                    "learned_from": prompt[:80],
                    "confidence": 0.9
                },
                "tool_needed": True,
                "tool_description": "Parser for CSV and structured text formats"
            })
        elif "sort" in p or "list" in p:
            return json.dumps({
                "reasoning_errors": [
                    "Did not verify data type before attempting sort operation",
                    "Assumed all items were comparable"
                ],
                "learned_pattern": "Always validate data homogeneity before applying comparison-based operations",
                "revised_approach": "Check data types, handle edge cases, then sort",
                "guidance_for_attempt_2": "Verify list contains sortable elements, handle empty case, then apply sort",
                "should_update_policy": True,
                "policy_principle": {
                    "pattern": "Before sorting or comparing, verify all elements are of compatible types",
                    "context": "list operations",
                    "confidence": 0.85
                },
                "tool_needed": False
            })
        else:
            return json.dumps({
                "reasoning_errors": ["Approach was too generic for this specific task"],
                "learned_pattern": "Task-specific strategies outperform generic approaches",
                "revised_approach": "Analyze task requirements more carefully before acting",
                "guidance_for_attempt_2": "Break task into smaller, specific steps",
                "should_update_policy": True,
                "policy_principle": {
                    "pattern": "When uncertain, decompose task into explicit sub-steps",
                    "context": "general",
                    "confidence": 0.75
                },
                "tool_needed": False
            })
