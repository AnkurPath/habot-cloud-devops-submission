output "d0_raw_landing_bucket_name" {
  description = "Name of the D0 Raw Landing bucket."
  value       = google_storage_bucket.d0_raw_landing.name
}

output "d1_staged_enforced_dataset_id" {
  description = "Identifier of the BigQuery D1 Staged Enforced dataset."
  value       = google_bigquery_dataset.d1_staged_enforced.dataset_id
}

output "student_onboarding_table_id" {
  description = "Fully qualified BigQuery student onboarding table identifier."
  value       = "${var.project_id}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding.table_id}"
}

