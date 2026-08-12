from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Authorization(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    UNKNOWN = "unknown"


class ExpectedDecision(str, Enum):
    EXECUTE = "execute"
    CLARIFY = "clarify"
    DENY = "deny"


@dataclass(frozen=True)
class Case:
    case_id: str
    base_id: str
    domain: str
    condition: str
    request: str
    observations: tuple[str, ...]
    tool: str
    arguments: dict[str, Any]
    authorization: dict[str, Authorization]
    evidence_source: dict[str, str]
    expected_decision: ExpectedDecision
    clarify_fields: tuple[str, ...] = ()
    horizon: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["authorization"] = {key: value.value for key, value in self.authorization.items()}
        data["expected_decision"] = self.expected_decision.value
        data["observations"] = list(self.observations)
        data["clarify_fields"] = list(self.clarify_fields)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Case":
        return cls(
            case_id=data["case_id"],
            base_id=data["base_id"],
            domain=data["domain"],
            condition=data["condition"],
            request=data["request"],
            observations=tuple(data.get("observations", [])),
            tool=data["tool"],
            arguments=dict(data["arguments"]),
            authorization={key: Authorization(value) for key, value in data["authorization"].items()},
            evidence_source=dict(data["evidence_source"]),
            expected_decision=ExpectedDecision(data["expected_decision"]),
            clarify_fields=tuple(data.get("clarify_fields", [])),
            horizon=int(data.get("horizon", 0)),
        )


@dataclass(frozen=True)
class Decision:
    decision: ExpectedDecision
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    clarify_fields: tuple[str, ...] = ()
    reason: str = ""
    raw_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["decision"] = self.decision.value
        data["clarify_fields"] = list(self.clarify_fields)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any], raw_output: str = "") -> "Decision":
        return cls(
            decision=ExpectedDecision(data["decision"]),
            tool=data.get("tool"),
            arguments=dict(data.get("arguments") or {}),
            clarify_fields=tuple(data.get("clarify_fields") or []),
            reason=str(data.get("reason") or ""),
            raw_output=raw_output,
        )

