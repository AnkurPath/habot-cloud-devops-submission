from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DCYNRule:
    code: str
    question: str
    payload_field: str
    expected_type: type
    failure_message: str

    def evaluate(self, payload: dict[str, Any]) -> bool:
        value = payload.get(self.payload_field)
        return isinstance(value, self.expected_type) and bool(value)


DCYN_LIBRARY: tuple[DCYNRule, ...] = (
    DCYNRule(
        code="DCYN_001",
        question="Does the record include verified parent or guardian consent?",
        payload_field="parent_guardian_consent",
        expected_type=bool,
        failure_message="Parent or guardian consent is required before onboarding.",
    ),
    DCYNRule(
        code="DCYN_002",
        question="Does the record include a requested learning support plan?",
        payload_field="support_plan_requested",
        expected_type=bool,
        failure_message="A support plan request must be explicitly Yes or No.",
    ),
    DCYNRule(
        code="DCYN_003",
        question="Does the school authorization gate pass?",
        payload_field="school_authorization_confirmed",
        expected_type=bool,
        failure_message="School authorization must be confirmed before matching an assistant.",
    ),
    DCYNRule(
        code="DCYN_004",
        question="Does the record include an emergency contact?",
        payload_field="emergency_contact_available",
        expected_type=bool,
        failure_message="Emergency contact availability must be confirmed.",
    ),
    DCYNRule(
        code="DCYN_005",
        question="Does the parent or guardian allow analytics use?",
        payload_field="analytics_consent",
        expected_type=bool,
        failure_message="Analytics consent must be explicit and cannot be inferred.",
    ),
)


def evaluate_dcyn(payload: dict[str, Any]) -> dict[str, bool]:
    return {rule.code: rule.evaluate(payload) for rule in DCYN_LIBRARY}


def failed_dcyn_messages(payload: dict[str, Any]) -> dict[str, str]:
    flags = evaluate_dcyn(payload)
    return {
        rule.code: rule.failure_message
        for rule in DCYN_LIBRARY
        if rule.code in flags and flags[rule.code] is False
    }
