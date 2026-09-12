# Submission Checklist

- Replace candidate contact metadata in `README.md`, `docs/*.md`, and `presentation/habot_cloud_devops_submission_slides.md`.
- Run `ruff check .`.
- Run `black --check .`.
- Run `bandit -r backend security -x backend/tests,security/tests`.
- Run `pytest`.
- Run `terraform fmt -check -recursive` from `infra/`.
- Run `terraform init -backend=false` from `infra/`.
- Run `terraform validate` from `infra/`.
- Upload the repository or link it from the presentation.
- Convert `presentation/habot_cloud_devops_submission_slides.md` into a Google Slides or PowerPoint deck with no more than 15 slides.

