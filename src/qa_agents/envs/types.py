from __future__ import annotations
from abc import ABC, abstractmethod
from ..utils.schemas import Observation, Action

class EnvLike(ABC):
    @abstractmethod
    def reset(self) -> Observation: ...
    @abstractmethod
    def step(self, action: Action): ...
