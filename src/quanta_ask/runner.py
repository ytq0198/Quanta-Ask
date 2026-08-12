from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .evaluation import evaluate
from .schema import Case, Decision


def _run_one(case: Case, policy) -> tuple[Decision, str | None]:
    try:
        return policy.decide(case), None
    except Exception as exc:  # failures must be visible in the run record
        decision = Decision.from_dict({"decision": "deny", "reason": "policy error"})
        return decision, f"{type(exc).__name__}: {exc}"


def run_policy(cases: list[Case], policy, output_path: Path | None = None, workers: int = 1) -> dict:
    if workers <= 0:
        raise ValueError("workers must be positive")
    if workers == 1:
        outputs = [_run_one(case, policy) for case in cases]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            outputs = list(executor.map(lambda case: _run_one(case, policy), cases))

    decisions: list[Decision] = []
    records: list[dict] = []
    for case, (decision, error) in zip(cases, outputs, strict=True):
        decisions.append(decision)
        records.append({"case": case.to_dict(), "decision": decision.to_dict(), "error": error})
    metrics = evaluate(cases, decisions)
    metrics["policy_error_rate"] = sum(error is not None for _, error in outputs) / len(outputs) if outputs else 0.0
    result = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "records": records,
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
