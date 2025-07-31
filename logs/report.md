- **Goal**: Toggle WiFi off then back on.
- **Plan Length**: 6 steps, including opening settings, toggling WiFi, and verifying the state.
- **Bugs Detected**: One verification step (step 6) initially reported an unknown intent but ultimately passed.
- **Recovery Actions**: No recovery actions were necessary as all steps eventually passed verification.
- **Final Status**: The run completed successfully with a status of "passed."

### Step Summary

| Step | Intent | Target | Action OK | Verify | Reason |
|---:|---|---|:---:|:---:|---|
| 1 | open_settings |  | ✅ | ✅ | No specific rule |
| 2 | tap | Network & Internet | ✅ | ✅ | No specific rule |
| 3 | toggle | Wi‑Fi | ✅ | ✅ | Toggled Wi‑Fi |
| 4 | wait |  | ✅ | ✅ | No specific rule |
| 5 | toggle | Wi‑Fi | ✅ | ✅ | Toggled Wi‑Fi |
| 6 | verify | Wi‑Fi | ❌ | ✅ | Wi‑Fi desired=True actual=True |

**Final status:** passed
