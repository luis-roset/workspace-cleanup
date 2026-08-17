"""CLI for listing and destroying every workspace in an HCP Terraform organization.

Usage:
    python3 -m hcp_cleanup.cli list --org <org> [--hostname app.terraform.io]

    python3 -m hcp_cleanup.cli destroy --org <org> --yes --confirm-org <org> \\
        [--hostname app.terraform.io] [--exclude ws-name ...]

`destroy` refuses to run unless --yes is given AND --confirm-org exactly
matches --org, so it can't be triggered by accident or by a copy-pasted
command with the wrong target.
"""

from __future__ import annotations

import argparse
import sys

from .api import ApiError, Client
from .auth import AuthError, DEFAULT_HOSTNAME, resolve_token
from .report import WorkspaceOutcome, write_reports
from .runs import destroy_workspace
from .workspaces import Workspace, list_workspaces, unlock_workspace


def _get_client(hostname: str) -> Client:
    try:
        token, source = resolve_token(hostname)
    except AuthError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    print(f"Using token from {source}", file=sys.stderr)
    return Client(hostname, token)


def _print_table(workspaces: list[Workspace]) -> None:
    if not workspaces:
        print("No workspaces found.")
        return
    name_w = max(len(w.name) for w in workspaces) + 2
    print(f"{'NAME':<{name_w}}{'RESOURCES':<11}{'LOCKED':<8}{'EXECUTION MODE'}")
    for w in workspaces:
        print(f"{w.name:<{name_w}}{w.resource_count:<11}{str(w.locked):<8}{w.execution_mode}")
    print(f"\n{len(workspaces)} workspace(s) total.")


def cmd_list(args: argparse.Namespace) -> None:
    client = _get_client(args.hostname)
    try:
        workspaces = list_workspaces(client, args.org)
    except ApiError as e:
        print(f"Failed to list workspaces: {e.detail}", file=sys.stderr)
        sys.exit(1)
    _print_table(workspaces)


def cmd_destroy(args: argparse.Namespace) -> None:
    if not args.yes or args.confirm_org != args.org:
        print(
            "Refusing to run: pass both --yes and --confirm-org <org> "
            "(must exactly match --org) to proceed with a destructive run "
            "against every workspace in the organization.",
            file=sys.stderr,
        )
        sys.exit(2)

    client = _get_client(args.hostname)
    try:
        workspaces = list_workspaces(client, args.org)
    except ApiError as e:
        print(f"Failed to list workspaces: {e.detail}", file=sys.stderr)
        sys.exit(1)

    exclude = set(args.exclude or [])
    outcomes: list[WorkspaceOutcome] = []

    for w in workspaces:
        if w.name in exclude:
            print(f"[skip] {w.name}: excluded via --exclude")
            outcomes.append(WorkspaceOutcome(w.name, w.id, "skipped", None, None, "excluded via --exclude"))
            continue
        if w.locked and not args.include_locked:
            print(f"[skip] {w.name}: workspace is locked (use --include-locked to override)")
            outcomes.append(WorkspaceOutcome(w.name, w.id, "skipped", None, None, "locked"))
            continue
        if w.locked and args.include_locked:
            print(f"[run ] {w.name}: unlocking (was locked)...")
            try:
                unlock_workspace(client, w.id)
            except ApiError as e:
                print(f"[FAIL] {w.name}: could not unlock: {e.detail}")
                outcomes.append(
                    WorkspaceOutcome(w.name, w.id, "failed", None, None, f"could not unlock: {e.detail}")
                )
                continue
        if w.resource_count == 0:
            print(f"[skip] {w.name}: no resources in state")
            outcomes.append(WorkspaceOutcome(w.name, w.id, "skipped", None, None, "no resources in state"))
            continue

        print(f"[run ] {w.name}: creating destroy run ({w.resource_count} resources)...")
        result = destroy_workspace(client, w.id, "Destroy via workspace-cleanup tool")
        outcome = "success" if result.ok else "failed"
        print(f"[{'ok' if result.ok else 'FAIL'}  ] {w.name}: {result.detail} (run {result.run_id})")
        outcomes.append(
            WorkspaceOutcome(w.name, w.id, outcome, result.run_id, result.final_status, result.detail)
        )

    json_path, md_path = write_reports(args.org, args.hostname, outcomes)
    print(f"\nReport written to:\n  {json_path}\n  {md_path}")

    if any(o.outcome == "failed" for o in outcomes):
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hcp_cleanup")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all workspaces in the organization (read-only)")
    p_list.add_argument("--org", required=True, help="HCP Terraform organization name")
    p_list.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    p_list.set_defaults(func=cmd_list)

    p_destroy = sub.add_parser("destroy", help="Run terraform destroy on every workspace in the organization")
    p_destroy.add_argument("--org", required=True, help="HCP Terraform organization name")
    p_destroy.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    p_destroy.add_argument("--yes", action="store_true", help="Required to proceed")
    p_destroy.add_argument(
        "--confirm-org", default="", help="Must exactly match --org to proceed"
    )
    p_destroy.add_argument(
        "--exclude", action="append", metavar="WORKSPACE_NAME",
        help="Workspace name to skip (repeatable)",
    )
    p_destroy.add_argument(
        "--include-locked", action="store_true",
        help="Also attempt to destroy locked workspaces (off by default)",
    )
    p_destroy.set_defaults(func=cmd_destroy)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
