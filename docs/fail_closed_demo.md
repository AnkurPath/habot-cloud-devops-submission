# Fail-Closed Demo

Candidate full name: Ankur
Candidate contact: Update this line with the exact email address or phone number before submission.

## Secure Commit

Command:

```bash
python security/scan_secrets.py --paths . --quarantine-dir quarantine
```

Expected result:

```text
Secret scan passed for N files.
```

The workflow continues to Terraform formatting, Terraform validation, Python formatting, Python linting, Bandit, and tests.

## Insecure Commit

Create a temporary file outside version control for demonstration:

```bash
mkdir -p quarantine-demo
DEMO_VALUE="abc1234567890""XYZTOKENVALUE"
printf 'API_KEY = "%s"\n' "$DEMO_VALUE" > quarantine-demo/insecure_settings.py
python security/scan_secrets.py --paths quarantine-demo/insecure_settings.py --quarantine-dir quarantine
```

Expected result:

```text
quarantine-demo/insecure_settings.py:1: hardcoded-secret-assignment: API_KEY=abc1...ALUE
```

The command exits with status `1`, writes `quarantine/secret-findings.json`, and blocks every downstream deployable step.
