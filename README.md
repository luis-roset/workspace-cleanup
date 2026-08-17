# workspace-cleanup

A small zero-dependency Python CLI (`hcp_cleanup`) for auditing and destroying
every workspace in an HCP Terraform / Terraform Enterprise organization, with
a JSON + Markdown report of what succeeded, what failed, and why.

## Latest run — `luisroset-org`

- Host: `app.terraform.io`
- Generated: 2026-08-17T10:11:42Z · Last rechecked: 2026-08-17T13:32:48Z
- Total workspaces: 40 — **7 succeeded**, **2 remediated**, **1 in progress**, **0 failed**, **30 skipped**

Full report: [`reports/destroy-report-luisroset-org-20260817T101142Z.json`](reports/destroy-report-luisroset-org-20260817T101142Z.json) · [`.md`](reports/destroy-report-luisroset-org-20260817T101142Z.md)

### In progress

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| vault-rds-aws-peering | run-d59oaApK4ScnEHEF | plan_queued | Originally failed to unlock (locked by run-eHL6DLNeayGJheMK, since canceled). On recheck, a new destroy run was queued via the HCP Terraform UI by someone/something else in the org and is actively planning. 2 resources still in state — left alone since it's already being handled elsewhere; re-check later. |

### Remediated (state cleaned up manually — **not** a confirmed real-world destroy)

| Workspace | Root cause | Action taken |
|---|---|---|
| US-Compute-GCP-1 | GCP project `learned-glow-330306`'s billing account is closed, so the Compute API can't be re-enabled and Terraform can never verify or destroy these resources through the provider. | `terraform state rm` on all 3 state entries. Workspace now shows 0 resources. |
| OAuth | The workspace's `tfe` provider token is invalid/expired and is baked into the uploaded config (no VCS repo, no workspace variables) — not fixable via the API. | `terraform state rm` on all 5 state entries. Workspace now shows 0 resources. |

**Caveat:** removing entries from state only stops Terraform from tracking them — it does **not** confirm the underlying GCP compute instances or TFE org/workspace/variables were actually deleted. If they still exist, they are now unmanaged and need manual verification/cleanup outside Terraform (GCP console for the compute resources; the relevant HCP Terraform org for the `tfe_*` resources).

### Succeeded

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| no-code-test-ec2 | run-ovPHGaqybSHtdAUN | applied | destroyed |
| no-code-test | run-4vvUDdeLF7rkytwZ | applied | destroyed |
| RITM0010006 | run-gjoVEDHQLWTXs5uC | applied | destroyed |
| RITM0010005 | run-7KFf4LHGkzwtGqrv | applied | destroyed |
| vault-tfc | run-XkVrQGW3zrJcaten | applied | destroyed |
| HCP-policy-demo | run-kB9WGYR6msFWRTBy | applied | Originally failed to unlock. Rechecked: the run holding the lock was itself a destroy and has since applied — 9 resources gone, workspace now unlocked with 0 resources. Not triggered by this tool. |
| demo-vault-kubernetes-vso | run-sBdxUA52mnj7R7MU | applied | Originally failed to unlock. Rechecked: the run holding the lock was itself a destroy and has since applied — 26 resources gone, 0 remain. Still locked, but now by an unrelated stale run (cost_estimated since 2026-07-30) — cosmetic since nothing's left to destroy; someone should discard that stuck run to fully release the lock. |

### Skipped (no resources in state)

`ec2-test_RITM0010011`, `ec2-test`, `test-1`, `RITM0010010`, `RITM0010010_dev185469`,
`RITM0010011`, `test-ec2-demo`, `test-s3-module`, `test-hashicat-policies`, `api-test1`,
`luis-test`, `Vault-Enterprise`, `no-code-test-Nikita`, `Vault-Splunk`, `test-module`,
`no-code-test-3`, `RITM0010001_dev185469`, `RITM0010002_dev185469`, `RITM0010004`,
`RITM0010003`, `RITM0010002`, `RITM0010001`, `learn-terraform-github-actions`,
`Azure-simple-resource`, `terraform-aws-ec2-instance`,
`learn-hcp-packer-run-tasks-data-source-validation`, `integration_test`,
`aws-securitygroup-vpc-peering`, `test`, `no-code-test-2` (unlocked on recheck — 0 resources)

### Follow-up needed

- `vault-rds-aws-peering`: a destroy run is actively in progress (queued by someone else in the org) — check back to confirm it finishes.
- `demo-vault-kubernetes-vso`: still locked by an unrelated stale run from 2026-07-30 — worth discarding to fully release the lock, though nothing is left to destroy.
- For the 2 remediated workspaces (`US-Compute-GCP-1`, `OAuth`), someone should verify in GCP/HCP Terraform directly whether the underlying resources are actually gone.

## Usage

Auth: run `terraform login <hostname>` (default `app.terraform.io`), or set
`TFE_TOKEN` / `TF_TOKEN_<host>` in your shell.

```bash
# Read-only: list every workspace in the org
python3 -m hcp_cleanup.cli list --org <org> [--hostname app.terraform.io]

# Destroy every workspace with resources in state. Requires both --yes and
# --confirm-org (must exactly match --org) so it can't run by accident.
python3 -m hcp_cleanup.cli destroy --org <org> --yes --confirm-org <org> \
    [--exclude <workspace-name> ...] [--include-locked]
```

By default `destroy` skips workspaces with 0 resources and locked workspaces.
`--include-locked` will attempt to unlock and destroy locked workspaces too —
this only works for manual locks; workspaces locked by another active run
are left alone and reported as failed.

Each `destroy` run writes a timestamped JSON + Markdown report to `reports/`.
