from __future__ import annotations
import argparse, os, json, pathlib
from qa_agents.pipeline.agent_s_orchestrator import run_agents

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", required=True)
    ap.add_argument("--env", choices=["mock","android"], default="mock")
    ap.add_argument("--task", default="settings_wifi")
    ap.add_argument("--logs_dir", default="./logs")
    ap.add_argument("--save_frames", action="store_true")
    ap.add_argument("--llm_planner", action="store_true")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--plan_cache", default="./logs/plan_cache.json")
    args = ap.parse_args()

    os.makedirs(args.logs_dir, exist_ok=True)
    history = run_agents(args.goal, args.env, args.task, args.logs_dir, args.llm_planner, args.model, args.plan_cache, args.save_frames)
    with open(pathlib.Path(args.logs_dir) / "agent_s_trace.json", "w", encoding="utf-8") as f:
        json.dump([m.__dict__ for m in history], f, indent=2)

if __name__ == "__main__":
    main()
    