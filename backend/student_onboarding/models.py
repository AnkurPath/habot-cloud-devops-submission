from django.core.validators import RegexValidator
from django.db import models


class StudentOnboarding(models.Model):
    class LearningNeed(models.TextChoices):
        ATTENTION_SUPPORT = "attention_support", "Attention Support"
        DYSLEXIA = "dyslexia", "Dyslexia"
        DYSCALCULIA = "dyscalculia", "Dyscalculia"
        SPEECH_LANGUAGE = "speech_language", "Speech And Language"
        AUTISM_SPECTRUM = "autism_spectrum", "Autism Spectrum"
        OTHER_DOCUMENTED = "other_documented", "Other Documented Need"

    class PIIAccessTier(models.TextChoices):
        STANDARD = "standard", "Standard"
        RESTRICTED = "restricted", "Restricted"

    submission_id = models.UUIDField(unique=True)
    student_external_id = models.CharField(max_length=36, unique=True)
    child_first_name = models.CharField(max_length=60)
    date_of_birth = models.DateField()
    parent_email = models.EmailField(max_length=254)
    parent_phone_e164 = models.CharField(
        max_length=16,
        validators=[RegexValidator(r"^\+[1-9]\d{7,14}$", "Phone number must use E.164 format.")],
    )
    primary_learning_need = models.CharField(max_length=32, choices=LearningNeed.choices)
    support_plan_requested = models.BooleanField()
    school_authorization_confirmed = models.BooleanField()
    parent_guardian_consent = models.BooleanField()
    analytics_consent = models.BooleanField()
    emergency_contact_available = models.BooleanField()
    pii_access_tier = models.CharField(max_length=16, choices=PIIAccessTier.choices)
    dcyn_flags = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["student_external_id"]),
            models.Index(fields=["primary_learning_need"]),
            models.Index(fields=["pii_access_tier"]),
        ]
