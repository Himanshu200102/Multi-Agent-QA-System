# Multi-Agent Mobile QA - Built on Agent-S + android_world

A minimal, production-minded **multi-agent** system for mobile QA that runs **on top of**:

- **Agent-S** (Simular’s `gui-agents`) for UI-grounded action suggestions, and  
- **android_world** (AndroidEnv) for executing steps on an Android emulator.

The system automates end-to-end mobile QA tasks (e.g., “Toggle Wi-Fi off then back on”) and produces an auditable report with per-agent traces and optional screen frames.

---

## What this project delivers

- **Multi-agent pipeline** with four roles:
  - **Planner** - creates a task plan (LLM or deterministic rules). Optionally consults Agent-S for the first step suggestion from a live screenshot.
  - **Executor** - executes intents (open_settings / tap / toggle / scroll / verify) against either a **mock** environment or **android_world**.
  - **Verifier** - checks step outcomes and requests replans on errors.
  - **Supervisor** - decides pass/fail and writes a compact report.

- **Grounded device interaction** via **android_world** (AndroidEnv).
- **Light integration with Agent-S** (`gui-agents`) so the Planner can leverage its UI reasoning without making the whole pipeline dependent on it.

---

## Why “on top of” Agent-S + android_world?

- **Agent-S**: When installed, the Planner calls Agent-S to propose a **first UI action** based on the current device screenshot and the stated goal. If Agent-S is unavailable, the system **gracefully falls back** to the internal planner same interface, no code changes needed by the caller.

- **android_world**: All device operations are executed through AndroidEnv, giving us a consistent action schema and enabling reproducible runs on an emulator. The Executor maps high-level “intents” to concrete device actions.

This layering keeps the codebase **portable** (mock mode works everywhere) while enabling **grounded** UI automation when Android is available.

---

## Acknowledgements

- **Agent-S (`gui-agents`)** by Simular  
- **android_world / AndroidEnv** by Google Research
