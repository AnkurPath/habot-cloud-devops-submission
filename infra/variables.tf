variable "project_id" {
  description = "Google Cloud project identifier for the staging environment."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid Google Cloud project identifier."
  }
}

variable "region" {
  description = "Single Google Cloud region used for staging data resources."
  type        = string

  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]+$", var.region))
    error_message = "region must be a Google Cloud region such as europe-west1."
  }
}

variable "raw_landing_bucket_name" {
  description = "Globally unique Cloud Storage bucket name for D0 Raw Landing."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$", var.raw_landing_bucket_name)) && !can(regex("goog|google", var.raw_landing_bucket_name))
    error_message = "raw_landing_bucket_name must be a valid non-Google bucket name."
  }
}

variable "ingestion_service_account_email" {
  description = "Service account email allowed to create incoming raw landing objects."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.iam\\.gserviceaccount\\.com$", var.ingestion_service_account_email))
    error_message = "ingestion_service_account_email must be a Google service account email."
  }
}

variable "staging_service_account_email" {
  description = "Service account email for staging validation automation."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.iam\\.gserviceaccount\\.com$", var.staging_service_account_email))
    error_message = "staging_service_account_email must be a Google service account email."
  }
}

variable "analytics_reader_group_email" {
  description = "Google Group email granted analytics read access after row-level filtering."
  type        = string

  validation {
    condition     = can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.analytics_reader_group_email))
    error_message = "analytics_reader_group_email must be an email address."
  }
}

variable "iam_condition_expiry_rfc3339" {
  description = "RFC3339 timestamp after which conditional IAM access expires."
  type        = string

  validation {
    condition     = can(regex("^20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", var.iam_condition_expiry_rfc3339))
    error_message = "iam_condition_expiry_rfc3339 must be formatted as YYYY-MM-DDTHH:MM:SSZ."
  }
}

