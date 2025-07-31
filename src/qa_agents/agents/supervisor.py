from __future__ import annotations
from .base import Agent
from typing import List, Dict, Any
from ..llm.openai_client import LLMClient

class Supervisor(Agent):
    def __init__(self, model: str|None = None) -> None:
        self.llm = LLMClient(model=model)

    def summarize(self, goal: str, log_records: List[Dict[str, Any]]) -> str:
        # Try LLM; if not available, fallback to a deterministic summary
        prompt = (
            "You are the QA supervisor. Summarize the run in 5 bullet points: "
            "goal, plan length, bugs detected, recovery actions, final status."
        )
        text = self.llm.summarize(prompt, log_records, fallback=True)
        return text
