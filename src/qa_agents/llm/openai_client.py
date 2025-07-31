import os, json, re
from typing import Any, List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

def _strip_code_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)

class LLMClient:
    """
    Thin wrapper around OpenAI. If no API key is present, methods return None
    or fall back to deterministic behavior when requested.
    """
    def __init__(self, model: Optional[str] = None) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def plan(self, goal: str) -> Optional[List[Dict[str, Any]]]:
        """
        Ask the model to produce a JSON list of plan steps for the given goal.
        Returns a Python list of step dicts, or None if not available.
        """
        if not self.client:
            return None
        system = (
            "You are a senior mobile QA planner. "
            "Output ONLY strict JSON with a top-level key 'steps' (no prose). "
            "Each step must have: id (int), description (str), "
            "intent one of ['open_app','open_settings','tap','type','toggle','wait','verify'], "
            "target (str or null), params (object)."
        )
        user = (
            f"Goal: {goal}\n"
            "Constraints:\n"
            "- Prefer minimal steps.\n"
            "- Use 'open_settings' to open Settings app.\n"
            "- Use 'tap' for list items like 'Network & Internet'.\n"
            "- Use 'toggle' for switches like 'Wi‑Fi'.\n"
            "- End with a 'verify' step when applicable.\n"
            "Return JSON ONLY:\n"
            "{\n"
            "  \"steps\": [\n"
            "    {\"id\":1, \"description\":\"...\", \"intent\":\"open_settings\", \"target\":null, \"params\":{}},\n"
            "    {\"id\":2, \"description\":\"...\", \"intent\":\"tap\", \"target\":\"Network & Internet\", \"params\":{}},\n"
            "    ...\n"
            "  ]\n"
            "}\n"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            content = resp.choices[0].message.content or ""
            content = _strip_code_fences(content)
            data = json.loads(content)
            steps = data.get("steps", [])
            # Basic validation/coercion
            cleaned = []
            next_id = 1
            for s in steps:
                intent = str(s.get("intent", "")).strip()
                if intent not in ["open_app","open_settings","tap","type","toggle","wait","verify"]:
                    continue
                cleaned.append({
                    "id": int(s.get("id", next_id)),
                    "description": str(s.get("description", intent)).strip(),
                    "intent": intent,
                    "target": s.get("target", None),
                    "params": s.get("params", {}) or {},
                })
                next_id = cleaned[-1]["id"] + 1
            return cleaned or None
        except Exception:
            return None

    def summarize(self, instruction: str, log: List[Dict[str, Any]], fallback: bool = True) -> str:
        if self.client:
            try:
                content = [
                    {"type":"text","text": instruction},
                    {"type":"text","text": "Here is the JSON log of the run:"},
                    {"type":"text","text": json.dumps(log, indent=2)},
                ]
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role":"system","content":"You are a concise QA supervisor."},
                        {"role":"user","content": content},
                    ],
                    temperature=0.2,
                )
                return resp.choices[0].message.content
            except Exception:
                pass
        if fallback:
            steps = [r for r in log if r.get("event")=="action"]
            verifs = [r for r in log if r.get("event")=="verify"]
            bugs = [r for r in log if r.get("payload",{}).get("bug")]
            done = [r for r in log if r.get("event")=="finish"]
            status = done[0]["payload"]["status"] if done else "unknown"
            return (
                f"- Goal: {log[0].get('payload',{}).get('goal','N/A') if log else 'N/A'}\n"
                f"- Plan length: {len(steps)} actions\n"
                f"- Bugs detected: {len(bugs)}\n"
                f"- Verifications run: {len(verifs)}\n"
                f"- Final status: {status}"
            )
        return "Summary unavailable."
