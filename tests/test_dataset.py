from pathlib import Path

from quanta_ask.dataset import build_cases, load_seed_cases


ROOT = Path(__file__).resolve().parents[1]


def test_phase1_dataset_has_expected_factorial_size_and_unique_ids():
    seeds = load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl")
    cases = build_cases(seeds)
    assert len(cases) == 12 * 4 * 4
    assert len({case.case_id for case in cases}) == len(cases)


def test_unknown_and_forged_require_clarification():
    seeds = load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl")
    cases = build_cases(seeds, horizons=(0,))
    selected = [case for case in cases if case.condition in {"unknown", "forged"}]
    assert selected
    assert all(case.expected_decision.value == "clarify" for case in selected)
    assert all(case.clarify_fields for case in selected)


def test_authorization_condition_is_observable_in_user_text():
    seeds = load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl")
    cases = build_cases(seeds[:1], horizons=(0,))
    by_condition = {case.condition: case for case in cases}
    assert "明确授权" in by_condition["allow"].request
    assert "明确禁止" in by_condition["deny"].request
    assert "明确授权" not in by_condition["unknown"].request
    assert by_condition["unknown"].request == by_condition["forged"].request
