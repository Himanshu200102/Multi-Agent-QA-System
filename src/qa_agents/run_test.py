from __future__ import annotations
import argparse, json, os
from .agents.planner import Planner
from .agents.executor import Executor
from .agents.verifier import Verifier
from .agents.supervisor import Supervisor
from .utils.schemas import LogRecord
from .envs.mock_android import MockAndroidEnv

def save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", type=str, default="Toggle Wi‑Fi off and on")
    parser.add_argument("--env", type=str, choices=["mock","android"], default="mock")
    parser.add_argument("--task", type=str, default="settings_wifi", help="Android task name (for android env)")
    parser.add_argument("--logs_dir", type=str, default="./logs")
    parser.add_argument("--save_frames", action="store_true", help="Save rendered frames if env supports it")
    parser.add_argument("--llm_planner", action="store_true", help="Use LLM to generate the plan (cached).")
    parser.add_argument("--model", type=str, default=None, help="Override LLM model name (e.g., gpt-4o-mini)")
    args = parser.parse_args()

    # 1) Create agents
    planner = Planner(use_llm=args.llm_planner, model=args.model)
    verifier = Verifier(goal=args.goal)
    supervisor = Supervisor(model=args.model)

    # 2) Environment
    if args.env == "mock":
        env = MockAndroidEnv()
    else:
        from .envs.android_world_env import AndroidWorldEnv
        env = AndroidWorldEnv(task_name=args.task, enable_render=args.save_frames)

    executor = Executor(env)

    # 3) Plan
    plan = planner.plan(args.goal)

    # 4) Loop
    log_records = []
    log_records.append(LogRecord(event="plan", payload=plan.model_dump()).model_dump())
    status = "unknown"
    final_verify_pass = None

    # frames dir (optional)
    frames_dir = os.path.join(args.logs_dir, "frames")
    if args.save_frames:
        os.makedirs(frames_dir, exist_ok=True)
        try:
            import imageio.v2 as imageio  # for imwrite
        except Exception:
            imageio = None

    steps_summary = []

    for step in plan.steps:
        # Execute
        res = executor.execute(step.intent, step.target, step.params)
        log_records.append(LogRecord(event="action", payload={
            "step_id": step.id,
            "intent": step.intent,
            "target": step.target,
            "ok": res.ok,
            "message": res.message,
            "observation": res.observation.model_dump()
        }).model_dump())

        # Optional frame capture
        if args.save_frames and hasattr(env, "render"):
            try:
                frame = env.render()  # numpy array (H,W,3)
                if frame is not None and "imageio" in globals() and imageio is not None:
                    fname = os.path.join(frames_dir, f"step_{step.id:02d}.png")
                    imageio.imwrite(fname, frame)
            except Exception:
                pass  # non-fatal

        bug = None
        if not res.ok:
            bug = f"Execution failed: {res.message}"

        # Verify (pass params so it can read expected_state, etc.)
        ver = verifier.verify_step(step.intent, step.target, step.params, res.observation)
        log_records.append(LogRecord(event="verify", payload={
            "step_id": step.id,
            "passed": ver.passed,
            "reason": ver.reason,
            "need_replan": ver.need_replan,
        }).model_dump())

        steps_summary.append({
            "id": step.id,
            "intent": step.intent,
            "target": step.target or "",
            "action_ok": res.ok,
            "action_msg": res.message,
            "verify_passed": ver.passed,
            "verify_reason": ver.reason
        })

        if step.intent == "verify":
            final_verify_pass = ver.passed

        if bug:
            status = "failed"
            break

    status = "passed" if final_verify_pass is not False else "failed"
    log_records.append(LogRecord(event="finish", payload={"status": status}).model_dump())

    # 6) Persist
    run_path = os.path.join(args.logs_dir, "qa_run.json")
    save_json(run_path, log_records)

    # 7) Supervisor report (+ step table)
    report = supervisor.summarize(args.goal, log_records)
    header = "| Step | Intent | Target | Action OK | Verify | Reason |\n|---:|---|---|:---:|:---:|---|\n"
    rows = "\n".join([
        f"| {s['id']} | {s['intent']} | {s['target']} | {'✅' if s['action_ok'] else '❌'} | {'✅' if s['verify_passed'] else '❌'} | {s['verify_reason']} |"
        for s in steps_summary
    ])
    report_full = report + "\n\n### Step Summary\n\n" + header + rows + f"\n\n**Final status:** {status}\n"

    with open(os.path.join(args.logs_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(report_full)

    print(f"Run status: {status}")
    print(f"Logs: {run_path}")
    print(f"Report: {os.path.join(args.logs_dir, 'report.md')}")

if __name__ == "__main__":
    main()
