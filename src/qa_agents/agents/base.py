from __future__ import annotations
from typing import Any, Dict

class Agent:
    def name(self) -> str:
        return self.__class__.__name__

    def log(self, *args: Any) -> None:
        print(f"[{self.name()}]", *args)
