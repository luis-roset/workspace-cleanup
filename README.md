# workspace-cleanup

A small zero-dependency Python CLI (`hcp_cleanup`) for auditing and destroying
every workspace in an HCP Terraform / Terraform Enterprise organization, with
a JSON + Markdown report of what succeeded, what failed, and why.

## Latest run — `luisroset-org`

- Host: `app.terraform.io`
- Generated: 2026-08-17T10:11:42Z
- Total workspaces: 40 — **5 succeeded**, **6 failed**, **29 skipped**

Full report: [`reports/destroy-report-luisroset-org-20260817T101142Z.json`](reports/destroy-report-luisroset-org-20260817T101142Z.json) · [`.md`](reports/destroy-report-luisroset-org-20260817T101142Z.md)

### Failed

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| HCP-policy-demo | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-kB9WGYR6msFWRTBy and may not be unlocked except by them. |
| US-Compute-GCP-1 | run-FTQWfbbuD5UZLKST | errored | errored: plan failed reading google_compute_instance_template.tpl — Compute Engine API is disabled on GCP project 'learned-glow-330306' (SERVICE_DISABLED / accessNotConfigured). Enable it at https://console.developers.google.com/apis/api/compute.googleapis.com/overview?project=learned-glow-330306, or the project/credentials backing this workspace no longer exist. |
| vault-rds-aws-peering | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-eHL6DLNeayGJheMK and may not be unlocked except by them. |
| demo-vault-kubernetes-vso | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-sBdxUA52mnj7R7MU and may not be unlocked except by them. |
| no-code-test-2 | - | - | could not unlock: conflict: Unable to unlock workspace. The workspace is locked by Run run-7Uh9yVcT3DG2TeD3 and may not be unlocked except by them. |
| OAuth | run-GiMvzFPW5VHr3sJi | errored | errored: plan failed refreshing tfe_organization.oauth — 'unauthorized' from the HCP Terraform API. This workspace's own Terraform config uses the 'tfe' provider with a token (workspace variable) that is expired/revoked, unrelated to the token this tool used. |

### Succeeded

| Workspace | Run ID | Status | Detail |
|---|---|---|---|
| no-code-test-ec2 | run-ovPHGaqybSHtdAUN | applied | destroyed |
| no-code-test | run-4vvUDdeLF7rkytwZ | applied | destroyed |
| RITM0010006 | run-gjoVEDHQLWTXs5uC | applied | destroyed |
| RITM0010005 | run-7KFf4LHGkzwtGqrv | applied | destroyed |
| vault-tfc | run-XkVrQGW3zrJcaten | applied | destroyed |

### Skipped (no resources in state)

`ec2-test_RITM0010011`, `ec2-test`, `test-1`, `RITM0010010`, `RITM0010010_dev185469`,
`RITM0010011`, `test-ec2-demo`, `test-s3-module`, `test-hashicat-policies`, `api-test1`,
`luis-test`, `Vault-Enterprise`, `no-code-test-Nikita`, `Vault-Splunk`, `test-module`,
`no-code-test-3`, `RITM0010001_dev185469`, `RITM0010002_dev185469`, `RITM0010004`,
`RITM0010003`, `RITM0010002`, `RITM0010001`, `learn-terraform-github-actions`,
`Azure-simple-resource`, `terraform-aws-ec2-instance`,
`learn-hcp-packer-run-tasks-data-source-validation`, `integration_test`,
`aws-securitygroup-vpc-peering`, `test`

### Follow-up needed

The 4 "locked by another run" failures need a manual decision (cancel someone
else's in-flight run, or leave them) — the tool deliberately won't do that on
its own. The 2 `errored` workspaces need infra/credential fixes unrelated to
this tool before a destroy can succeed.

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
