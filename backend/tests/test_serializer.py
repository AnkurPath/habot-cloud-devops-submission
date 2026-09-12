from datetime import date
from uuid import uuid4

import pytest
from student_onboarding.serializers import StudentOnboardingSerializer


def valid_payload() -> dict:
    return {
        "submission_id": str(uuid4()),
        "student_external_id": "STUDENT-2026-0001",
        "child_first_name": "Aarav",
        "date_of_birth": date(2014, 5, 20).isoformat(),
        "parent_email": "parent@example.com",
        "parent_phone_e164": "+971501234567",
        "primary_learning_need": "dyslexia",
        "support_plan_requested": True,
        "school_authorization_confirmed": True,
        "parent_guardian_consent": True,
        "analytics_consent": True,
        "emergency_contact_available": True,
        "pii_access_tier": "standard",
    }


@pytest.mark.django_db
def test_serializer_accepts_valid_payload_and_adds_dcyn_flags() -> None:
    serializer = StudentOnboardingSerializer(data=valid_payload())

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["dcyn_flags"]["DCYN_001"] is True
    assert serializer.validated_data["dcyn_flags"]["DCYN_003"] is True


@pytest.mark.django_db
def test_serializer_rejects_missing_parent_guardian_consent() -> None:
    payload = valid_payload()
    payload["parent_guardian_consent"] = False

    serializer = StudentOnboardingSerializer(data=payload)

    assert not serializer.is_valid()
    assert "parent_guardian_consent" in serializer.errors


@pytest.mark.django_db
def test_serializer_rejects_restricted_pii_analytics_consent_conflict() -> None:
    payload = valid_payload()
    payload["pii_access_tier"] = "restricted"

    serializer = StudentOnboardingSerializer(data=payload)

    assert not serializer.is_valid()
    assert "analytics_consent" in serializer.errors
