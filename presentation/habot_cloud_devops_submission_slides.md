# Secure Staging Recovery

Candidate full name: Ankur
Candidate contact: Update this line with the exact email address or phone number before submission.

Junior Cloud and DevOps Engineer project submission.

Core outcome: a Terraform, CI/CD, and serializer blueprint that prevents raw secrets, enforces least privilege, and protects student onboarding data integrity.

# Incident Problem

A staging update introduced two failures:

- Raw API credentials were committed to application code.
- A schema mismatch broke downstream analytics.

The remediation must block the same failure pattern automatically.

# Target Architecture

Flow:

React form -> Django REST Framework serializer -> DCYN Yes/No validation -> D0 Raw Landing bucket -> staging validator -> BigQuery D1 Staged Enforced -> analytics readers through row-level policy.

# Terraform Control Plane

Terraform provisions:

- D0 Raw Landing Cloud Storage bucket.
- D1 Staged Enforced BigQuery dataset.
- Student onboarding BigQuery table.
- Customer-managed encryption key.
- Conditional IAM grants.
- BigQuery row-level access policy.

# D0 Raw Landing Controls

The landing bucket is hardened with:

- Public access prevention.
- Uniform bucket-level access.
- Versioning.
- Soft delete retention.
- Customer-managed encryption.
- Write-only service account access to `incoming/`.

# D1 BigQuery Controls

The staged dataset protects analytics access with:

- Dedicated staging service account write access.
- Analytics group read access with time-bound IAM.
- Row-level access policy limited to analytics consent and standard PII tier.
- Table schema aligned to serializer output.

# Fail-Closed Build Gate

The CI workflow runs secret scanning first. A raw credential finding:

- Stops the job with a non-zero exit code.
- Uploads quarantine evidence.
- Prevents Terraform, linting, tests, or deployment from continuing.

# Formatting and Security Gates

Post-secret gates run only after the repository is clean:

- `terraform fmt -check`.
- `terraform validate`.
- `black --check`.
- `ruff check`.
- `bandit`.
- `pytest`.

# DCYN Library

DCYN converts subjective onboarding checks into binary Yes/No decisions:

- Parent or guardian consent.
- Support plan request.
- School authorization.
- Emergency contact availability.
- Analytics consent.

# Serializer Enforcement

The DRF model serializer removes human judgment through:

- UUID version enforcement.
- Name length and character rules.
- Age range validation.
- E.164 phone validation.
- Enumerated learning need and PII tiers.
- Cross-field consent checks.

# Schema Mapping

The payload, serializer, BigQuery schema, and DCYN mapping use the same field names. This prevents drift between application validation and downstream analytics.

# Demo Evidence

Valid build:

- Secret scan passes.
- Terraform and Python checks continue.
- Tests pass.

Invalid build:

- Hardcoded API key is detected.
- Quarantine artifact is created.
- Workflow exits fail-closed.

# Least Privilege Summary

No broad public principals are used. Service accounts receive only the roles needed for their data path, and IAM conditions limit access by object prefix and time.

# Operational Runbook

Daily use:

- Merge only through the Poka-Yoke workflow.
- Rotate KMS keys on schedule.
- Review quarantine evidence after blocked builds.
- Keep serializer, DCYN mapping, and BigQuery schema synchronized.

# Final Outcome

The submission delivers a secure staging blueprint with deployable Terraform, automated build gates, and deterministic data validation for student onboarding analytics.
