from pathlib import Path
from types import SimpleNamespace

from quanta_ask.dataset import build_cases, load_seed_cases
from quanta_ask.policies import OpenAICompatiblePolicy


ROOT = Path(__file__).resolve().parents[1]


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["temperature"] == 0.0
        assert kwargs["max_tokens"] == 256
        message = SimpleNamespace(content='{"decision":"clarify","tool":null,"arguments":{},"clarify_fields":["recipient"],"reason":"missing"}')
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_openai_compatible_policy_parses_structured_response():
    client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    case = build_cases(load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl"), horizons=(0,))[2]
    decision = OpenAICompatiblePolicy("fake", "http://localhost/v1", client=client).decide(case)
    assert decision.decision.value == "clarify"
    assert decision.clarify_fields == ("recipient",)


def test_openai_compatible_policy_rejects_missing_json():
    class InvalidCompletions:
        def create(self, **kwargs):
            message = SimpleNamespace(content="I would ask the user.")
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    client = SimpleNamespace(chat=SimpleNamespace(completions=InvalidCompletions()))
    case = build_cases(load_seed_cases(ROOT / "data" / "seeds" / "phase1_seed_cases.jsonl"), horizons=(0,))[2]
    policy = OpenAICompatiblePolicy("fake", "http://localhost/v1", client=client)
    try:
        policy.decide(case)
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("invalid model output must not be silently accepted")
