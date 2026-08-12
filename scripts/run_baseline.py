from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from quanta_ask.dataset import read_cases
from quanta_ask.policies import ContractPolicy, OpenAICompatiblePolicy, RecklessPolicy
from quanta_ask.runner import run_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("heuristic", "reckless", "openai-compatible"), default="heuristic")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--base-url", default=os.environ.get("QUANTA_ASK_BASE_URL", "http://127.0.0.1:8000/v1"))
    parser.add_argument("--model", default=os.environ.get("QUANTA_ASK_MODEL"))
    parser.add_argument("--api-key", default=os.environ.get("QUANTA_ASK_API_KEY", "local-not-secret"))
    parser.add_argument("--limit", type=int, help="Run only the first N cases for a smoke test")
    parser.add_argument("--stratified-smoke", action="store_true", help="Select one case per domain/condition with varied horizons")
    parser.add_argument("--prompt-variant", choices=("neutral", "cautious"), default="cautious")
    parser.add_argument("--workers", type=int, default=1, help="Concurrent requests; preserve result ordering")
    parser.add_argument("--max-tokens", type=int, default=256)
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    dataset = args.dataset or root / "data" / "generated" / "phase1_cases.jsonl"
    output = args.output or root / "runs" / f"phase1-{args.policy}.json"
    cases = read_cases(dataset)
    if args.stratified_smoke:
        selected = []
        seen = set()
        horizons = (0, 4, 8, 16)
        for case in cases:
            key = (case.domain, case.condition)
            target_horizon = horizons[(len(seen) + len(case.domain)) % len(horizons)]
            if key not in seen and case.horizon == target_horizon:
                selected.append(case)
                seen.add(key)
        cases = selected
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit("--limit must be positive")
        cases = cases[: args.limit]
    if args.policy == "heuristic":
        policy = ContractPolicy()
    elif args.policy == "reckless":
        policy = RecklessPolicy()
    else:
        if not args.model:
            raise SystemExit("--model or QUANTA_ASK_MODEL is required")
        policy = OpenAICompatiblePolicy(
            args.model,
            args.base_url,
            args.api_key,
            prompt_variant=args.prompt_variant,
            max_tokens=args.max_tokens,
        )
    metadata = {
        "policy": args.policy,
        "model": args.model,
        "base_url": args.base_url if args.policy == "openai-compatible" else None,
        "prompt_variant": args.prompt_variant if args.policy == "openai-compatible" else None,
        "temperature": getattr(policy, "temperature", None),
        "max_tokens": getattr(policy, "max_tokens", None),
        "workers": args.workers,
        "dataset_path": str(dataset),
        "dataset_sha256": file_sha256(dataset),
        "case_count": len(cases),
        "git_commit": git_commit(root),
    }
    result = run_policy(cases, policy, output, workers=args.workers, metadata=metadata)
    print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))
    print(f"wrote run to {output}")


if __name__ == "__main__":
    main()
