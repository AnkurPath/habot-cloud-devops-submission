from __future__ import annotations

import re
from datetime import date
from uuid import UUID

from rest_framework import serializers

from .dcyn import evaluate_dcyn, failed_dcyn_messages
from .models import StudentOnboarding

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{0,59}$")


class StudentOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentOnboarding
        fields = (
            "submission_id",
            "student_external_id",
            "child_first_name",
            "date_of_birth",
            "parent_email",
            "parent_phone_e164",
            "primary_learning_need",
            "support_plan_requested",
            "school_authorization_confirmed",
            "parent_guardian_consent",
            "analytics_consent",
            "emergency_contact_available",
            "pii_access_tier",
            "dcyn_flags",
            "created_at",
        )
        read_only_fields = ("dcyn_flags", "created_at")

    def validate_submission_id(self, value: UUID) -> UUID:
        if value.version != 4:
            raise serializers.ValidationError("submission_id must be a version 4 UUID.")
        return value

    def validate_child_first_name(self, value: str) -> str:
        normalized = value.strip()
        if not NAME_PATTERN.fullmatch(normalized):
            raise serializers.ValidationError(
                "child_first_name must be 1 to 60 alphabetic characters "
                "with simple punctuation only."
            )
        return normalized

    def validate_date_of_birth(self, value: date) -> date:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 3 or age > 21:
            raise serializers.ValidationError("Student age must be between 3 and 21 years.")
        return value

    def validate(self, attrs: dict) -> dict:
        dcyn_flags = evaluate_dcyn(attrs)
        failed_rules = failed_dcyn_messages(attrs)

        if not attrs["parent_guardian_consent"]:
            raise serializers.ValidationError({"parent_guardian_consent": failed_rules["DCYN_001"]})

        if (
            attrs["analytics_consent"]
            and attrs["pii_access_tier"] == StudentOnboarding.PIIAccessTier.RESTRICTED
        ):
            raise serializers.ValidationError(
                {"analytics_consent": "Analytics consent cannot override restricted PII access."}
            )

        if attrs["support_plan_requested"] and not attrs["school_authorization_confirmed"]:
            raise serializers.ValidationError(
                {
                    "school_authorization_confirmed": (
                        "School authorization must be confirmed when support_plan_requested is Yes."
                    )
                }
            )

        attrs["dcyn_flags"] = dcyn_flags
        return attrs
