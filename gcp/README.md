# GCP IAM Roles

This document lists the project-level GCP IAM roles required to onboard Sedai, by resource type and Sedai operation mode. Grant these roles to the service account Sedai uses to integrate with the GCP project.
## Compute Engine (VMs & Disks)

| Sedai Operation Mode | Required Roles |
|---|---|
| Data Pilot | `roles/compute.viewer`<br>`roles/monitoring.viewer`<br>`roles/logging.viewer` |
| Co-Pilot / Auto-Pilot | `roles/compute.instanceAdmin.v1`<br>`roles/monitoring.viewer`<br>`roles/logging.viewer`<br>`roles/iam.serviceAccountUser` |

## Cloud Storage

| Sedai Operation Mode | Required Roles |
|---|---|
| Data Pilot | `roles/storage.bucketViewer` |
| Co-Pilot / Auto-Pilot | `roles/storage.admin` |

## Dataflow

Sedai does not have a Co-Pilot/Auto-Pilot mode for Dataflow — read-only access only.

| Sedai Operation Mode | Required Roles | Permissions Needed |
|---|---|---|
| Data Pilot | `roles/dataflow.viewer` | `dataflow.jobs.get`<br>`dataflow.jobs.list` |
