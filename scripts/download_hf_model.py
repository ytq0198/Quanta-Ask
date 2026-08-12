from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download


PROJECT_ROOT = Path("/mnt/localDisk3/weizian/Quanta-Ask")
MODEL_ROOT = PROJECT_ROOT / "models"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download one pinned Hugging Face snapshot into Quanta-Ask.")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--revision", help="Exact commit SHA; resolved from the Hub when omitted")
    parser.add_argument("--ignore-pattern", action="append", default=[])
    return parser.parse_args()


def ensure_project_destination(destination: Path) -> Path:
    resolved = destination.resolve()
    model_root = MODEL_ROOT.resolve()
    if resolved == model_root or model_root not in resolved.parents:
        raise SystemExit(f"Destination must be a child of {model_root}: {resolved}")
    return resolved


def main() -> None:
    args = parse_args()
    destination = ensure_project_destination(args.destination)
    revision = args.revision or HfApi().model_info(args.repo_id).sha
    if not revision:
        raise SystemExit(f"Could not resolve an immutable revision for {args.repo_id}")

    os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=args.repo_id,
        revision=revision,
        local_dir=destination,
        cache_dir=PROJECT_ROOT / ".cache" / "huggingface",
        ignore_patterns=args.ignore_pattern or None,
    )
    manifest = {
        "repo_id": args.repo_id,
        "revision": revision,
        "destination": str(destination),
        "ignore_patterns": args.ignore_pattern,
    }
    (destination / "quanta_ask_download.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
