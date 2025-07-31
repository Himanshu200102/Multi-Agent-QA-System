from __future__ import annotations
from typing import Dict, Any
from .types import EnvLike
from ..utils.schemas import Observation, Action

class MockAndroidEnv(EnvLike):
    """A tiny mock of Android UI for a Wi‑Fi toggle task.
    Screens: home -> settings -> network
    State: wifi_on: bool
    """
    def __init__(self) -> None:
        self.state = {"screen":"home", "wifi_on": True}

    def reset(self) -> Observation:
        self.state = {"screen":"home", "wifi_on": True}
        return self._observe()

    def _observe(self) -> Observation:
        screen = self.state["screen"]
        ui = {}
        if screen == "home":
            ui = {"buttons":["Settings"]}
        elif screen == "settings":
            ui = {"list":["Network & Internet","Display","Battery"]}
        elif screen == "network":
            ui = {"toggles":{"Wi‑Fi": self.state["wifi_on"]}}
        return Observation(screen=screen, ui_tree=ui, info={"wifi_on": self.state["wifi_on"]})

    def step(self, action: Action):
        ok = True
        msg = ""
        if action.name == "open_settings":
            self.state["screen"] = "settings"
            msg = "Opened Settings"
        elif action.name == "tap":
            target = (action.target or "").lower()
            if self.state["screen"] == "home" and target == "settings":
                self.state["screen"] = "settings"
                msg = "Tapped Settings"
            elif self.state["screen"] == "settings" and target in ["network & internet","network","internet"]:
                self.state["screen"] = "network"
                msg = "Opened Network & Internet"
            else:
                ok = False
                msg = f"Tap failed on screen={self.state['screen']} target={action.target}"
        elif action.name == "toggle":
            if self.state["screen"] == "network" and (action.target or "").lower() in ["wifi","wi‑fi"]:
                self.state["wifi_on"] = not self.state["wifi_on"]
                msg = f"Wi‑Fi set to {self.state['wifi_on']}"
            else:
                ok = False
                msg = "Toggle failed"
        elif action.name == "type":
            msg = "Type has no effect in mock"
        elif action.name == "wait":
            msg = "Waited"
        else:
            ok = False
            msg = f"Unknown action {action.name}"

        return ok, self._observe(), msg
