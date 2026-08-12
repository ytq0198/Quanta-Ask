from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .evaluation import evaluate
from .schema import Case, Decision


def run_policy(cases: list[Case], policy, output_path: Path | None = None) -> dict:
    decisions: list[Decision] = []
    records: list[dict] = []
    for case in cases:
        try:
            decision = policy.decide(case)
            error = None
        except Exception as exc:  # failures must be visible in the run record
            decision = Decision.from_dict({"decision": "deny", "reason": "policy error"})
            error = f"{type(exc).__name__}: {exc}"
        decisions.append(decision)
        records.append({"case": case.to_dict(), "decision": decision.to_dict(), "error": error})
    result = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": evaluate(cases, decisions),
        "records": records,
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

