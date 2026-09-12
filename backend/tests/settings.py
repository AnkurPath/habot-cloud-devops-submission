SECRET_KEY = "".join(["test", "-only", "-django", "-secret", "-key"])
USE_TZ = True
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "student_onboarding",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
