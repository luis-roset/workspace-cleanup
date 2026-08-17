# HCP Terraform destroy report — luisroset-org

- Host: `app.terraform.io`
- Generated: 2026-08-17T10:11:42.705541+00:00
- Last rechecked: 2026-08-17T13:32:48Z
- Total workspaces: 40
- Succeeded: 7
- Remediated (state cleaned up manually): 2
- In progress (being handled by another actor): 1
- Failed: 0
- Skipped: 30

## Failed

_none_

## In Progress

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| vault-rds-aws-peering | run-d59oaApK4ScnEHEF | plan_queued | Originally failed to unlock (locked by run-eHL6DLNeayGJheMK, which has since been canceled). Rechecked: a new destroy run (run-d59oaApK4ScnEHEF, is-destroy=true) was queued via the HCP Terraform UI at 2026-08-17T13:29:46Z by someone/something else in the org and is actively planning. 2 resources still in state as of this recheck. Left alone since it's already being handled by another actor — re-check later. |

## Remediated

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| US-Compute-GCP-1 | run-FTQWfbbuD5UZLKST | state-rm | Root cause: GCP project 'learned-glow-330306' has its billing account closed, so the Compute API can't be re-enabled and Terraform can never verify or destroy these resources through the provider. Ran `terraform state rm` on all 3 state entries (google_compute_instance_template.tpl, google_compute_instance_from_template.compute_instance, data.google_compute_zones.available) — workspace now shows 0 resources. CAVEAT: this only removed Terraform's tracking; it did NOT confirm or perform deletion of any underlying GCP resources. If real compute instances exist, they are now unmanaged and must be checked/cleaned up directly in the GCP console — Terraform will never touch them again. |
| OAuth | run-GiMvzFPW5VHr3sJi | state-rm | Root cause: this workspace's 'tfe' provider token is invalid/expired and isn't a workspace variable (0 vars set, config uploaded via tfe-ui with no VCS repo) — the token is baked into the uploaded config itself, not fixable via the API. Ran `terraform state rm` on all 5 state entries (tfe_oauth_client.gitlab, tfe_organization.oauth, tfe_variable.oauth_token, tfe_variable.tfe_token, tfe_workspace.dynamic_vcs) — workspace now shows 0 resources. CAVEAT: this only removed Terraform's tracking; it did NOT confirm or perform deletion of the underlying TFE org/workspace/variables those resources pointed to. If they still exist, they are now unmanaged and must be checked/cleaned up directly in whatever HCP Terraform org they belonged to. |

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
| no-code-test-2 | - | - | Originally failed to unlock (locked by run-7Uh9yVcT3DG2TeD3). Rechecked: that run was discarded (not a destroy, is-destroy=false) and the workspace is now unlocked with 0 resources — nothing to destroy here regardless. |
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
| HCP-policy-demo | run-kB9WGYR6msFWRTBy | applied | Originally failed to unlock (locked by an active run outside this tool's control). Rechecked later: that run was itself a destroy (is-destroy=true) and has since applied successfully. Workspace is now unlocked with 0 resources — destroyed, just not by this tool's run. |
| demo-vault-kubernetes-vso | run-sBdxUA52mnj7R7MU | applied | Originally failed to unlock (locked by an active run outside this tool's control). Rechecked later: that run was itself a destroy (is-destroy=true) and has since applied successfully — 0 resources remain. Note: the workspace is still locked, but now by an unrelated stale run (run-1RScRAEmRW4AmpgK, status cost_estimated, created 2026-07-30, is-destroy=false) that predates this cleanup. Since there's nothing left to destroy here, the lock is cosmetic at this point, but someone should discard that stuck run to fully release it. |
| no-code-test-ec2 | run-ovPHGaqybSHtdAUN | applied | destroyed |
| no-code-test | run-4vvUDdeLF7rkytwZ | applied | destroyed |
| RITM0010006 | run-gjoVEDHQLWTXs5uC | applied | destroyed |
| RITM0010005 | run-7KFf4LHGkzwtGqrv | applied | destroyed |
| vault-tfc | run-XkVrQGW3zrJcaten | applied | destroyed |
