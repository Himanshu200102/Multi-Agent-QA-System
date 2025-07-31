from __future__ import annotations
from .base import Agent
from ..utils.schemas import Verification, Observation

class Verifier(Agent):
    def __init__(self, goal: str) -> None:
        self.goal = goal.lower()

    def verify_step(self, intent: str, target: str|None, params: dict, obs: Observation) -> Verification:
        g = self.goal
        if "wifi" in g:
            if intent == "toggle" and target and target.lower() in ["wi‑fi", "wifi"]:
                return Verification(passed=True, reason="Toggled Wi‑Fi")
            if intent == "verify" and target and target.lower() in ["wi‑fi", "wifi"]:
                expected = None
                if isinstance(params, dict) and "expected_state" in params:
                    expected = str(params["expected_state"]).strip().lower() in ("on", "true", "1")
                desired = True if expected is None else expected
                ok = bool(obs.info.get("wifi_on")) == desired
                return Verification(passed=ok, reason=f"Wi‑Fi desired={desired} actual={obs.info.get('wifi_on')}", need_replan=not ok)
        return Verification(passed=True, reason="No specific rule")
