# Architecture Overview

Candidate full name: Ankur
Candidate contact: Update this line with the exact email address or phone number before submission.

## Data Flow

1. A Django REST Framework endpoint receives a student onboarding payload.
2. `StudentOnboardingSerializer` validates field type, length, choice, consent, age, and cross-field rules.
3. `evaluate_dcyn` converts subjective checks into explicit Yes/No flags.
4. Valid payloads are written to D0 Raw Landing under `incoming/`.
5. Staging automation writes rejected records to `quarantine/` and writes validated rows to BigQuery D1 Staged Enforced.
6. BigQuery row-level access policy exposes only analytics-consented standard-tier rows to the analytics group.

## Security Controls

- Cloud Storage public access prevention is enforced.
- Uniform bucket-level access prevents object ACL drift.
- Customer-managed encryption protects the raw bucket and BigQuery dataset.
- Service account access is scoped by role, path, and time-bound IAM conditions.
- BigQuery row-level access policy blocks restricted PII rows from analytics readers.
- The CI workflow runs raw secret detection before Terraform validation, linting, or tests.

## Fail-Closed Logic

The build gate treats formatting errors and raw credential patterns as release blockers. The first security gate is `security/scan_secrets.py`; on failure the workflow uploads a quarantine artifact and returns a non-zero exit code. All downstream stages require `success()`, so insecure commits cannot progress.

## Data Integrity Logic

The serializer is intentionally stricter than the database model. Human judgment is replaced with:

- Enumerated choice fields for learning needs and PII access tier.
- E.164 phone number validation.
- Age range enforcement of 3 to 21 years.
- Explicit parent or guardian consent requirement.
- Cross-field rejection when analytics consent conflicts with restricted PII.
- DCYN flags stored as JSON for downstream auditability.

