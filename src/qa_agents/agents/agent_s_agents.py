# src/qa_agents/agents/agent_s_agents.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json, os, io, subprocess, tempfile
from PIL import Image
from qa_agents.agent_s_compat import Message, ShimAgent, AGENTS_AVAILABLE
from qa_agents.planning.rule_planner import rule_plan_for_goal
from qa_agents.planning.llm_planner import llm_plan_for_goal
from qa_agents.envs.mock_env import MockEnv
from qa_agents.envs.android_world_env import AndroidWorldEnv

def get_env(env_name: str, task: Optional[str], enable_render: bool):
    if env_name == "mock":    return MockEnv()
    if env_name == "android": return AndroidWorldEnv(task_name=task or "settings_wifi", enable_render=enable_render)
    raise ValueError(f"Unknown env: {env_name}")

def execute_action(env, step: Dict[str, Any]) -> Dict[str, Any]:
    intent = step.get("intent"); target = step.get("target"); params = step.get("params", {})
    if intent == "open_settings": return env.step({"op": "open_app", "app": "Settings"})
    if intent == "tap":           return env.step({"op": "tap", "target": target})
    if intent == "toggle":        return env.step({"op": "toggle", "target": target, **params})
    if intent == "verify":        return env.step({"op": "verify", "target": target, **params})
    if intent == "scroll":        return env.step({"op": "scroll", "direction": params.get("direction","down")})
    return {"ok": False, "error": f"Unknown intent: {intent}"}

# ----------------------- AGENTS ----------------------------------------------

class PlannerAgent(ShimAgent):
    """
    If gui-agents (Agent‑S) is available, we’ll use it to sanity‑check the first step
    by asking Agent‑S for a suggested immediate action from the current screen.
    Otherwise we fall back to our rule/LLM planner only.
    """
    def __init__(self, use_llm: bool, model: str, goal: str, cache_path: Optional[str], env_name: str):
        super().__init__("planner")
        self.use_llm = use_llm; self.model = model; self.goal = goal; self.cache_path = cache_path
        self.env_name = env_name

    def _screenshot_android(self) -> Optional[bytes]:
        try:
            # Grab emulator screen via adb if available
            out = subprocess.check_output(["adb", "exec-out", "screencap", "-p"], timeout=5)
            return bytes(out)
        except Exception:
            return None

    def _first_action_from_agent_s(self, screenshot_png: bytes) -> Optional[str]:
        if not AGENTS_AVAILABLE:
            return None
        try:
            # Lazy import to avoid hard dependency at import time
            from gui_agents.s2.agent import AgentS2  # class name per README
            import pyautogui  # Agent‑S example uses pyautogui action space

            # Minimal engine params (your keys should already be in env)
            engine_params = {"llm": os.environ.get("OPENAI_MODEL","gpt-4o-mini")}
            agent = AgentS2(
                engine_params=engine_params,
                grounding_agent=None,
                platform="windows",            # we only need action suggestion, not exec
                action_space="pyautogui",
                observation_type="screenshot",
                search_engine=None
            )
            obs = {"screenshot": screenshot_png}
            info, actions = agent.predict(instruction=self.goal, observation=obs)
            # actions is usually a list of pyautogui commands as strings
            return actions[0] if actions else None
        except Exception:
            return None

    def step(self, history: List[Message]) -> Message:
        # Reuse prior plan if present
        for m in reversed(history):
            if m.role == "planner" and m.data.get("plan"):
                return Message("planner", "Reusing prior plan.", {"plan": m.data["plan"]})

        plan = llm_plan_for_goal(self.goal, model=self.model, cache_path=self.cache_path) if self.use_llm \
               else rule_plan_for_goal(self.goal)

        # Optional: Ask Agent‑S for the *first* action suggestion from current screen
        first_action = None
        if self.env_name == "android":
            shot = self._screenshot_android()
            if shot: first_action = self._first_action_from_agent_s(shot)

        if first_action:
            # Prepend a “tap”/”type” etc. based on the suggestion (we do a simple heuristic)
            plan = [{"id": 0, "description": f"Agent‑S suggests: {first_action}", "intent":"tap","target":"(from Agent‑S)"}] + plan

        return Message("planner", f"Planner produced plan with {len(plan)} steps.", {"plan": plan})

class ExecutorAgent(ShimAgent):
    def __init__(self, env_name: str, task: Optional[str], enable_render: bool = False):
        super().__init__("executor"); self._env = get_env(env_name, task, enable_render); self._cursor = 0
    def step(self, history: List[Message]) -> Message:
        plan = next((m.data["plan"] for m in reversed(history) if m.role=="planner" and m.data.get("plan")), None)
        if not plan: return Message("executor","No plan found yet.",{"executed":None})
        if self._cursor >= len(plan): return Message("executor","Plan finished.",{"executed":None,"done":True})
        step = plan[self._cursor]; result = execute_action(self._env, step); self._cursor += 1
        return Message("executor", f"Executed step {step['id']}: {step['description']}", {"executed": step, "result": result, "step_index": self._cursor-1})

class VerifierAgent(ShimAgent):
    def __init__(self, goal: str): super().__init__("verifier"); self.goal = goal
    def step(self, history: List[Message]) -> Message:
        last_exec = next((m for m in reversed(history) if m.role=="executor"), None)
        passed, need_replan, reason = False, False, "Pending"
        if last_exec and isinstance(last_exec.data.get("result"), dict):
            r = last_exec.data["result"]
            if r.get("ok"): passed, reason = True, "Last action ok."
            elif r.get("error"): need_replan, reason = True, f"Executor error: {r['error']}"
        return Message("verifier", f"Verifier: passed={passed}, replan={need_replan}. {reason}", {"passed": passed, "need_replan": need_replan, "reason": reason})

class SupervisorAgent(ShimAgent):
    def __init__(self, logs_dir: str): super().__init__("supervisor"); self.logs_dir = logs_dir
    def step(self, history: List[Message]) -> Message:
        verifier = next((m for m in reversed(history) if m.role=="verifier"), None)
        executor_done = next((m for m in reversed(history) if m.role=="executor" and m.data.get("done")), None)
        verdict, final = ("pass", True) if (verifier and verifier.data.get("passed")) else (("fail", True) if executor_done else ("in_progress", False))
        # Write a tiny report
        try:
            import pathlib, datetime, json
            p = pathlib.Path(self.logs_dir); p.mkdir(parents=True, exist_ok=True)
            with open(p/"agent_s_report.md","w",encoding="utf-8") as f:
                f.write(f"# Agent‑S Run Report\n\nVerdict: **{verdict}**\n\n")
                for m in history:
                    f.write(f"**{m.role}**: {m.content}\n")
                    if m.data: f.write(f"\n```json\n{json.dumps(m.data, indent=2)}\n```\n\n")
                f.write(f"_Generated: {datetime.datetime.now().isoformat()}_\n")
        except Exception: pass
        return Message("supervisor", f"Supervisor verdict: {verdict}", {"final": final, "verdict": verdict})
