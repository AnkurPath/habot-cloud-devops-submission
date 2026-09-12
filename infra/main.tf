terraform {
  required_version = ">= 1.7.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 7.43.0, < 9.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_storage_project_service_account" "gcs_service_account" {
  project = var.project_id

  depends_on = [google_project_service.required]
}

data "google_bigquery_default_service_account" "bigquery_service_account" {
  project = var.project_id

  depends_on = [google_project_service.required]
}

locals {
  required_services = toset([
    "bigquery.googleapis.com",
    "cloudkms.googleapis.com",
    "storage.googleapis.com",
  ])

  common_labels = {
    application     = "habotconnect"
    environment     = "staging"
    data_class      = "student_onboarding"
    managed_by      = "terraform"
    control_surface = "poka_yoke"
  }
}

resource "google_project_service" "required" {
  for_each           = local.required_services
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_kms_key_ring" "staging" {
  project  = var.project_id
  name     = "habot-staging-data-ring"
  location = var.region

  depends_on = [google_project_service.required]
}

resource "google_kms_crypto_key" "student_data" {
  name            = "student-onboarding-cmek"
  key_ring        = google_kms_key_ring.staging.id
  rotation_period = "7776000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key_iam_member" "gcs_cmek_access" {
  crypto_key_id = google_kms_crypto_key.student_data.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_storage_project_service_account.gcs_service_account.email_address}"
}

resource "google_kms_crypto_key_iam_member" "bigquery_cmek_access" {
  crypto_key_id = google_kms_crypto_key.student_data.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_bigquery_default_service_account.bigquery_service_account.email}"
}

resource "google_storage_bucket" "d0_raw_landing" {
  project                     = var.project_id
  name                        = var.raw_landing_bucket_name
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  labels                      = local.common_labels

  encryption {
    default_kms_key_name = google_kms_crypto_key.student_data.id
  }

  versioning {
    enabled = true
  }

  soft_delete_policy {
    retention_duration_seconds = 604800
  }

  lifecycle_rule {
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age            = 365
      matches_prefix = ["quarantine/"]
    }
  }

  depends_on = [google_kms_crypto_key_iam_member.gcs_cmek_access]
}

resource "google_storage_bucket_iam_member" "ingestion_write_only" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.ingestion_service_account_email}"

  condition {
    title       = "D0_Incoming_Write_Only_Before_Expiry"
    description = "Ingestion may create raw objects only in the incoming path until the approved access expiry."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.d0_raw_landing.name}/objects/incoming/\") && request.time < timestamp(\"${var.iam_condition_expiry_rfc3339}\")"
  }
}

resource "google_storage_bucket_iam_member" "staging_quarantine_writer" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.staging_service_account_email}"

  condition {
    title       = "D0_Quarantine_Write_Before_Expiry"
    description = "Staging automation can write quarantine records but cannot overwrite existing raw objects."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.d0_raw_landing.name}/objects/quarantine/\") && request.time < timestamp(\"${var.iam_condition_expiry_rfc3339}\")"
  }
}

resource "google_bigquery_dataset" "d1_staged_enforced" {
  project                    = var.project_id
  dataset_id                 = "d1_staged_enforced"
  friendly_name              = "D1 Staged Enforced Student Onboarding"
  description                = "Validated student onboarding records after DCYN and serializer enforcement."
  location                   = var.region
  delete_contents_on_destroy = false
  labels                     = local.common_labels

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.student_data.id
  }

  depends_on = [google_kms_crypto_key_iam_member.bigquery_cmek_access]
}

resource "google_bigquery_table" "student_onboarding" {
  project             = var.project_id
  dataset_id          = google_bigquery_dataset.d1_staged_enforced.dataset_id
  table_id            = "student_onboarding"
  description         = "One validated row per submitted student onboarding form."
  deletion_protection = true
  schema              = file("${path.module}/schema/student_onboarding_schema.json")
  labels              = local.common_labels
}

resource "google_bigquery_dataset_iam_member" "staging_data_editor" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.staging_service_account_email}"

  condition {
    title       = "D1_Service_Write_Before_Expiry"
    description = "Only staging automation can write validated records during the approved access window."
    expression  = "request.time < timestamp(\"${var.iam_condition_expiry_rfc3339}\")"
  }
}

resource "google_bigquery_dataset_iam_member" "analytics_data_viewer" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "group:${var.analytics_reader_group_email}"

  condition {
    title       = "D1_Analytics_Read_Before_Expiry"
    description = "Analytics readers receive dataset access only during the approved access window."
    expression  = "request.time < timestamp(\"${var.iam_condition_expiry_rfc3339}\")"
  }
}

resource "google_bigquery_row_access_policy" "analytics_eligible_rows" {
  project          = var.project_id
  dataset_id       = google_bigquery_dataset.d1_staged_enforced.dataset_id
  table_id         = google_bigquery_table.student_onboarding.table_id
  policy_id        = "analytics_eligible_rows"
  filter_predicate = "analytics_consent = TRUE AND pii_access_tier = 'standard'"
  grantees         = ["group:${var.analytics_reader_group_email}"]
}
