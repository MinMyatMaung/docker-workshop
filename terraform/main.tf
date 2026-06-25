terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
        }
    }
}

provider "google" {
    project = "innate-buckeye-499807-q3"
    region = "us-west1"
}

resource "google_storage_bucket" "data_lake" {
    name = "innate-buckeye-499807-q3-lake"
    location = "US"
    force_destroy = true

    uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "trips_data_all" {
    dataset_id = "trips_data_all"
    location = "US"
}
