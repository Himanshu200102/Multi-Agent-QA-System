from __future__ import annotations
from typing import Dict, List, Optional
import hashlib, json, os, pathlib
from .rule_planner import rule_plan_for_goal

def _cache_key(goal: str, model: str) -> str:
    return hashlib.sha256(f"{goal}::{model}".encode("utf-8")).hexdigest()

def _load_cache(cache_path: Optional[str]) -> dict:
    if not cache_path or not os.path.exists(cache_path): return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        return {}

def _save_cache(cache_path: Optional[str], key: str, plan: List[Dict]) -> None:
    if not cache_path: return
    p = pathlib.Path(cache_path); p.parent.mkdir(parents=True, exist_ok=True)
    data = _load_cache(cache_path); data[key] = {"steps": plan}
    with open(p, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

def llm_plan_for_goal(goal: str, model: str = "gpt-4o-mini", cache_path: Optional[str] = None) -> List[Dict]:
    key = _cache_key(goal, model); cache = _load_cache(cache_path)
    if key in cache and "steps" in cache[key]: return cache[key]["steps"]
    plan = rule_plan_for_goal(goal)
    _save_cache(cache_path, key, plan)
    return plan
