from __future__ import annotations
from typing import Any, Dict, Tuple
import numpy as np

from ..utils.schemas import Observation, Action

class AndroidWorldEnv:
    """
    Drop-in wrapper exposing the SAME interface as MockAndroidEnv:
      - reset() -> Observation
      - step(Action) -> (ok: bool, Observation, message: str)
      - render() -> np.ndarray (H, W, 3)  # optional
    Internally, it proxies to the real AndroidEnv/android_world.
    """

    def __init__(self, task_name: str = "settings_wifi", enable_render: bool = True):
        self.task_name = task_name
        self.enable_render = enable_render
        self._env = None
        self._boot()

    def _boot(self) -> None:

        try:

            from android_world.env import AndroidEnv  
        except Exception as e:
            raise RuntimeError(
                "Could not import AndroidEnv from android_world.env. "
                "Install the assignment's android_world package and update the import path here."
            ) from e

        self._env = AndroidEnv(task_name=self.task_name)

    def _obs_to_struct(self, raw: Dict[str, Any]) -> Observation:
        screen = raw.get("screen", self.task_name)
        ui_tree = raw.get("ui_tree", {})
        info = raw.get("info", {})
        return Observation(screen=screen, ui_tree=ui_tree, info=info)

    def reset(self) -> Observation:
        raw = self._env.reset()
        return self._obs_to_struct(raw)

    def step(self, action: Action) -> Tuple[bool, Observation, str]:
        """
        Map your high-level Action into whatever the AndroidEnv's step() expects.
        The 'op' keys below are placeholders — adjust to the real API once you confirm it.
        """
        low: Dict[str, Any] = {}

        if action.name == "open_settings":
            low = {"op": "open_settings"}
        elif action.name == "tap":
            low = {"op": "tap", "target": action.target}
        elif action.name == "type":
            low = {"op": "type", "text": action.params.get("text", ""), "target": action.target}
        elif action.name == "toggle":
            low = {"op": "toggle", "target": action.target}
        elif action.name == "wait":
            low = {"op": "wait", "seconds": action.params.get("seconds", 1)}
        else:
            return False, self._last_obs_or_reset(), f"Unknown action {action.name}"

        try:
            ok, raw_obs, msg = self._env.step(low)
        except Exception as e:
            return False, self._last_obs_or_reset(), f"Env step failed: {e}"

        obs = self._obs_to_struct(raw_obs)
        self._last_obs = obs
        return ok, obs, msg

    def render(self) -> np.ndarray:
        """Return an RGB frame (H, W, 3) if available."""
        if not self.enable_render:
            raise RuntimeError("render() disabled")
        try:
            frame = self._env.render(mode="rgb_array")
            return frame
        except Exception as e:
            raise RuntimeError(f"render() failed: {e}")

    _last_obs: Observation | None = None
    def _last_obs_or_reset(self) -> Observation:
        if self._last_obs is not None:
            return self._last_obs
        return self.reset()
