from __future__ import annotations
from typing import Dict, List

def _wifi_plan() -> List[Dict]:
    return [
        {"id": 1, "description": "Open the Settings app",      "intent": "open_settings", "target": None,               "params": {}},
        {"id": 2, "description": "Tap on Network & Internet",  "intent": "tap",           "target": "Network & Internet","params": {}},
        {"id": 3, "description": "Toggle WiFi off",           "intent": "toggle",        "target": "WiFi",           "params": {"state": "off"}},
        {"id": 4, "description": "Toggle WiFi back on",       "intent": "toggle",        "target": "WiFi",           "params": {"state": "on"}},
        {"id": 5, "description": "Verify WiFi is on",         "intent": "verify",        "target": "WiFi",           "params": {"expected_state": "on"}},
    ]

def rule_plan_for_goal(goal: str) -> List[Dict]:
    g = (goal or "").lower()
    if "wifi" in g or "wi-fi" in g:
        return _wifi_plan()
    return [
        {"id": 1, "description": "Open the Settings app", "intent": "open_settings", "target": None, "params": {}},
        {"id": 2, "description": f"Search for setting related to '{goal}'", "intent": "tap", "target": "Search", "params": {}},
        {"id": 3, "description": "Attempt the change", "intent": "tap", "target": goal, "params": {}},
        {"id": 4, "description": "Verify result", "intent": "verify", "target": goal, "params": {}},
    ]
