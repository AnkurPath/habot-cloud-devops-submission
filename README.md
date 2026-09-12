# HabotConnect Junior Cloud and DevOps Engineer Submission

Candidate full name: Ankur
Candidate contact: Update this line with the exact email address or phone number before submission.

## Purpose

This submission restores staging integrity for the simulated Django REST Framework and React platform by enforcing three controls:

1. Secure Google Cloud landing and staging resources through Terraform.
2. A fail-closed CI/CD gate that blocks formatting errors and raw secrets.
3. A deterministic Django REST Framework model serializer and DCYN Yes/No validation library for student onboarding data.

## Folder Layout

```text
.
|-- .github/workflows/poka-yoke-gate.yml
|-- backend/
|   |-- student_onboarding/
|   |   |-- dcyn.py
|   |   |-- models.py
|   |   `-- serializers.py
|   `-- tests/
|       |-- test_dcyn.py
|       `-- test_serializer.py
|-- docs/
|   |-- architecture_overview.md
|   |-- fail_closed_demo.md
|   `-- submission_checklist.md
|-- infra/
|   |-- main.tf
|   |-- outputs.tf
|   |-- schema/student_onboarding_schema.json
|   `-- variables.tf
|-- presentation/habot_cloud_devops_submission_slides.md
|-- schema/
|   |-- dcyn_library.csv
|   |-- dcyn_mapping.json
|   `-- student_onboarding_payload.example.json
|-- security/
|   |-- scan_secrets.py
|   `-- tests/test_scan_secrets.py
|-- pyproject.toml
`-- requirements-dev.txt
```

## How The Project Works

1. **Infrastructure is declared first.**
   `infra/main.tf` defines the Google Cloud staging resources: a D0 Raw Landing Cloud Storage bucket, a D1 Staged Enforced BigQuery dataset, a BigQuery table, a Cloud KMS key, IAM bindings, and a row-level access policy. `infra/variables.tf` forces real project, bucket, service account, group, region, and IAM expiry values to be supplied before apply. `infra/outputs.tf` prints the created bucket, dataset, and table identifiers.

2. **Raw files land in the secure bucket.**
   The bucket resource in `infra/main.tf` enables public access prevention, uniform bucket-level access, object versioning, soft delete, and customer-managed encryption. The `google_storage_bucket_iam_member.ingestion_write_only` block allows only the ingestion service account to create objects under `incoming/`. The `google_storage_bucket_iam_member.staging_quarantine_writer` block allows the staging service account to write rejected records under `quarantine/`.

3. **BigQuery accepts only enforced staged data.**
   `infra/schema/student_onboarding_schema.json` defines the analytics table schema expected after validation. The `google_bigquery_dataset.d1_staged_enforced` and `google_bigquery_table.student_onboarding` resources in `infra/main.tf` create the dataset and table. The `google_bigquery_row_access_policy.analytics_eligible_rows` resource exposes only rows where `analytics_consent = TRUE` and `pii_access_tier = 'standard'`.

4. **The CI/CD gate blocks unsafe commits before deployment checks.**
   `.github/workflows/poka-yoke-gate.yml` runs on pull requests and pushes to `main`. Its first validation step calls `security/scan_secrets.py`. If raw API keys, access tokens, passwords, or known token patterns are found, the script exits with status `1`, writes `quarantine/secret-findings.json`, uploads the quarantine artifact, and stops the job before Terraform validation, linting, Bandit, or tests can continue.

5. **The custom secret scanner performs the fail-closed check.**
   `security/scan_secrets.py` scans source files for high-entropy secret assignments and known token formats such as Google API keys, GitHub tokens, Slack tokens, and OpenAI-style keys. `security/tests/test_scan_secrets.py` proves that the scanner rejects hardcoded secrets and allows environment-variable references.

6. **The Django model defines the clean application contract.**
   `backend/student_onboarding/models.py` defines the `StudentOnboarding` database model, field limits, indexed fields, learning-need choices, PII access tiers, and E.164 phone number validation. This model is the source of truth for the serializer fields.

7. **The serializer eliminates manual judgment from onboarding validation.**
   `backend/student_onboarding/serializers.py` defines `StudentOnboardingSerializer`. It validates UUID version, child first name format, student age range, phone format, parent or guardian consent, school authorization, analytics consent, and restricted PII conflicts. Valid records receive computed `dcyn_flags` before being saved or sent downstream.

8. **The DCYN library converts business rules into binary Yes/No checks.**
   `backend/student_onboarding/dcyn.py` contains the executable DCYN rule library. `schema/dcyn_mapping.json` stores the same rule mapping in reviewer-friendly structured form. `schema/dcyn_library.csv` provides the spreadsheet-ready mapping table with full-form labels. `schema/student_onboarding_payload.example.json` shows the incoming JSON payload expected by the serializer.

9. **Tests prove the validation behavior.**
   `backend/tests/test_dcyn.py` checks that DCYN output is binary. `backend/tests/test_serializer.py` checks that a valid onboarding payload passes, missing parent or guardian consent fails, and restricted PII cannot be overridden by analytics consent. `backend/tests/settings.py` provides minimal Django settings for local tests.

10. **Documentation and presentation explain the engineering logic.**
    `docs/architecture_overview.md` explains the cloud, CI/CD, and data validation flow. `docs/fail_closed_demo.md` gives the command-level demo for a passing and failing secret scan. `docs/submission_checklist.md` lists the final review steps. `presentation/habot_cloud_devops_submission_slides.md` is the slide source, and `presentation/habot_cloud_devops_submission.pptx` is the 15-slide PowerPoint deck.

## Local Verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
black --check .
bandit -r backend security
pytest
cd infra
terraform fmt -check
terraform init -backend=false
terraform validate
```

## Terraform Inputs

The Terraform configuration intentionally requires real project, principal, and bucket values at apply time. This prevents accidental deployment of placeholder infrastructure.

Required variables:

- `project_id`
- `region`
- `raw_landing_bucket_name`
- `ingestion_service_account_email`
- `analytics_reader_group_email`
- `staging_service_account_email`
- `iam_condition_expiry_rfc3339`

## Fail-Closed Rule

The CI workflow runs the secret scanner first. If it finds a raw credential, it creates a quarantine artifact and exits non-zero before Terraform, Python linting, or tests continue.
