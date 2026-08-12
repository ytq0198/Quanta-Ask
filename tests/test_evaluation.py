from pathlib import Path

from quanta_ask.dataset import build_cases, load_seed_cases
from quanta_ask.evaluation import evaluate
from quanta_ask.policies import ContractPolicy, RecklessPolicy
from quanta_ask.runner import run_policy


ROOT = Path(__file__).resolve().parents[1]


def _cases():
    seeds = load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl")
    return build_cases(seeds, horizons=(0,))


def test_contract_policy_is_oracle_on_generated_labels():
    cases = _cases()
    metrics = evaluate(cases, [ContractPolicy().decide(case) for case in cases])
    assert metrics["decision_accuracy"] == 1.0
    assert metrics["unknown_as_allow_rate"] == 0.0
    assert metrics["allowed_task_completion"] == 1.0


def test_reckless_policy_exposes_expected_risk_metrics():
    cases = _cases()
    metrics = evaluate(cases, [RecklessPolicy().decide(case) for case in cases])
    assert metrics["unknown_as_allow_rate"] == 1.0
    assert metrics["deny_violation_rate"] == 1.0
    assert metrics["allowed_task_completion"] == 1.0


def test_parallel_runner_preserves_order_and_reports_no_errors():
    cases = _cases()
    result = run_policy(cases, ContractPolicy(), workers=4)
    assert [row["case"]["case_id"] for row in result["records"]] == [case.case_id for case in cases]
    assert result["metrics"]["policy_error_rate"] == 0.0
