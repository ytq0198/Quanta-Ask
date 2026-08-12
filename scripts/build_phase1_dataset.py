from pathlib import Path

from quanta_ask.dataset import build_cases, load_seed_cases, write_cases


ROOT = Path(__file__).resolve().parents[1]
seeds = load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl")
cases = build_cases(seeds)
output = ROOT / "data" / "generated" / "phase1_cases.jsonl"
write_cases(cases, output)
print(f"wrote {len(cases)} cases to {output}")

