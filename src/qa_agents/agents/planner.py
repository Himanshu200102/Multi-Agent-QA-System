from __future__ import annotations
from typing import List, Optional
import os

from .base import Agent
from ..utils.schemas import Plan, PlanStep
from ..utils.cache import JsonCache
from ..llm.openai_client import LLMClient

class Planner(Agent):
    """Planner with LLM-first strategy and rule-based fallback."""

    def __init__(self, use_llm: bool = False, model: Optional[str] = None) -> None:
        self.use_llm = use_llm
        self.llm = LLMClient(model=model) if use_llm else None
        self.cache = JsonCache(os.path.join(".", "logs", "plan_cache.json"))

    def _normalize_goal(self, goal: str) -> str:
        g = goal.lower()
        g = g.replace("‑", "-").replace("–", "-").replace("—", "-")
        g = g.replace("-", "").replace(" ", "")
        return g

    def _rule_plan(self, goal: str) -> Plan:
        g_norm = self._normalize_goal(goal)
        steps: List[PlanStep] = []
        sid = 1

        def add(intent, target=None, **params):
            nonlocal sid
            steps.append(PlanStep(
                id=sid,
                description=f"{intent} {target or ''}".strip(),
                intent=intent,
                target=target,
                params=params
            ))
            sid += 1

        if "wifi" in g_norm:
            add("open_settings")
            add("tap", "Network & Internet")
            add("toggle", "Wi‑Fi")
            add("wait", seconds=1)
            add("toggle", "Wi‑Fi")
            add("verify", target="Wi‑Fi")
        else:
            add("open_settings")
            add("verify")

        plan = Plan(goal=goal, steps=steps)
        self.log("Created rule-based plan with", len(steps), "steps")
        return plan

    def plan(self, goal: str) -> Plan:
        # Try cache first
        key = self.cache.key_from("plan", goal)
        cached = self.cache.get(key)
        if cached:
            steps = [PlanStep(**s) for s in cached.get("steps", [])]
            plan = Plan(goal=goal, steps=steps)
            self.log("Loaded plan from cache with", len(steps), "steps")
            return plan

        # Try LLM
        if self.use_llm and self.llm:
            steps = self.llm.plan(goal)
            if steps:
                steps_models = [PlanStep(**s) for s in steps]
                plan = Plan(goal=goal, steps=steps_models)
                self.cache.set(key, {"goal": goal, "steps": [s.model_dump() for s in steps_models]})
                self.log("Created LLM plan with", len(steps_models), "steps")
                return plan

        # Fallback
        plan = self._rule_plan(goal)
        self.cache.set(key, {"goal": goal, "steps": [s.model_dump() for s in plan.steps]})
        return plan
