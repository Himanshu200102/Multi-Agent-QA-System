from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol

@dataclass
class Message:
    role: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(Protocol):
    name: str
    def step(self, history: List[Message]) -> Message: ...

try:
    import gui_agents  # noqa: F401
    AGENTS_AVAILABLE = True
except Exception:
    AGENTS_AVAILABLE = False

class ShimAgent:
    def __init__(self, name: str): self.name = name
    def step(self, history: List[Message]) -> Message: raise NotImplementedError

class Router:
    def __init__(self, agents: Dict[str, BaseAgent]): self.agents = agents
    def run(self, start_with: str, history: List[Message], max_turns: int = 50) -> List[Message]:
        order = ["planner", "executor", "verifier", "supervisor"]
        i = order.index(start_with)
        for _ in range(max_turns):
            role = order[i % len(order)]
            msg = self.agents[role].step(history)
            history.append(msg)
            if role == "supervisor" and msg.data.get("final", False): break
            i += 1
        return history
