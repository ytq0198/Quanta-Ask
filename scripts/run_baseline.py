from __future__ import annotations

import argparse
import json
import os
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    dataset = args.dataset or root / "data" / "generated" / "phase1_cases.jsonl"
    output = args.output or root / "runs" / f"phase1-{args.policy}.json"
    cases = read_cases(dataset)
    if args.policy == "heuristic":
        policy = ContractPolicy()
    elif args.policy == "reckless":
        policy = RecklessPolicy()
    else:
        if not args.model:
            raise SystemExit("--model or QUANTA_ASK_MODEL is required")
        policy = OpenAICompatiblePolicy(args.model, args.base_url, args.api_key)
    result = run_policy(cases, policy, output)
    print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))
    print(f"wrote run to {output}")


if __name__ == "__main__":
    main()

