# HCP Terraform destroy report — luisroset-org

- Host: `app.terraform.io`
- Generated: 2026-08-17T10:11:42.705541+00:00
- Total workspaces: 40
- Succeeded: 5
- Failed: 6
- Skipped: 29

## Failed

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| HCP-policy-demo | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-kB9WGYR6msFWRTBy and may not be unlocked except by them. |
| US-Compute-GCP-1 | run-FTQWfbbuD5UZLKST | errored | errored: plan failed reading google_compute_instance_template.tpl — Compute Engine API is disabled on GCP project 'learned-glow-330306' (SERVICE_DISABLED / accessNotConfigured). Enable it at https://console.developers.google.com/apis/api/compute.googleapis.com/overview?project=learned-glow-330306, or the project/credentials backing this workspace no longer exist. |
| vault-rds-aws-peering | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-eHL6DLNeayGJheMK and may not be unlocked except by them. |
| demo-vault-kubernetes-vso | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-sBdxUA52mnj7R7MU and may not be unlocked except by them. |
| no-code-test-2 | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-7Uh9yVcT3DG2TeD3 and may not be unlocked except by them. |
| OAuth | run-GiMvzFPW5VHr3sJi | errored | errored: plan failed refreshing tfe_organization.oauth — 'unauthorized' from the HCP Terraform API. This workspace's own Terraform config uses the 'tfe' provider with a token (workspace variable) that is expired/revoked, unrelated to the token this tool used. |

## Skipped

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| ec2-test_RITM0010011 | - | - | no resources in state |
| ec2-test | - | - | no resources in state |
| test-1 | - | - | no resources in state |
| RITM0010010 | - | - | no resources in state |
| RITM0010010_dev185469 | - | - | no resources in state |
| RITM0010011 | - | - | no resources in state |
| test-ec2-demo | - | - | no resources in state |
| test-s3-module | - | - | no resources in state |
| test-hashicat-policies | - | - | no resources in state |
| api-test1 | - | - | no resources in state |
| luis-test | - | - | no resources in state |
| Vault-Enterprise | - | - | no resources in state |
| no-code-test-Nikita | - | - | no resources in state |
| Vault-Splunk | - | - | no resources in state |
| test-module | - | - | no resources in state |
| no-code-test-3 | - | - | no resources in state |
| RITM0010001_dev185469 | - | - | no resources in state |
| RITM0010002_dev185469 | - | - | no resources in state |
| RITM0010004 | - | - | no resources in state |
| RITM0010003 | - | - | no resources in state |
| RITM0010002 | - | - | no resources in state |
| RITM0010001 | - | - | no resources in state |
| learn-terraform-github-actions | - | - | no resources in state |
| Azure-simple-resource | - | - | no resources in state |
| terraform-aws-ec2-instance | - | - | no resources in state |
| learn-hcp-packer-run-tasks-data-source-validation | - | - | no resources in state |
| integration_test | - | - | no resources in state |
| aws-securitygroup-vpc-peering | - | - | no resources in state |
| test | - | - | no resources in state |

## Succeeded

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| no-code-test-ec2 | run-ovPHGaqybSHtdAUN | applied | destroyed |
| no-code-test | run-4vvUDdeLF7rkytwZ | applied | destroyed |
| RITM0010006 | run-gjoVEDHQLWTXs5uC | applied | destroyed |
| RITM0010005 | run-7KFf4LHGkzwtGqrv | applied | destroyed |
| vault-tfc | run-XkVrQGW3zrJcaten | applied | destroyed |
