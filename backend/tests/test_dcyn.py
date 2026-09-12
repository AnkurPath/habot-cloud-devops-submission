from student_onboarding.dcyn import evaluate_dcyn


def test_evaluate_dcyn_returns_binary_flags() -> None:
    payload = {
        "parent_guardian_consent": True,
        "support_plan_requested": False,
        "school_authorization_confirmed": True,
        "emergency_contact_available": True,
        "analytics_consent": False,
    }

    result = evaluate_dcyn(payload)

    assert result == {
        "DCYN_001": True,
        "DCYN_002": False,
        "DCYN_003": True,
        "DCYN_004": True,
        "DCYN_005": False,
    }
    assert all(isinstance(value, bool) for value in result.values())
