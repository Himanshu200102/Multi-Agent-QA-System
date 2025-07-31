import hashlib, json, os
from typing import Any, Dict, Optional

class JsonCache:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)

    def _load(self) -> Dict[str, Any]:
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def get(self, key: str) -> Optional[Any]:
        return self._load().get(key)

    def set(self, key: str, value: Any) -> None:
        d = self._load()
        d[key] = value
        self._save(d)

    @staticmethod
    def key_from(*parts: str) -> str:
        m = hashlib.sha256()
        for p in parts:
            m.update(p.encode("utf-8"))
        return m.hexdigest()
