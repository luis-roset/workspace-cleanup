"""Workspace listing for an HCP Terraform / Terraform Enterprise organization."""

from __future__ import annotations

from dataclasses import dataclass

from .api import Client


@dataclass
class Workspace:
    id: str
    name: str
    locked: bool
    resource_count: int
    execution_mode: str
    terraform_version: str

    @classmethod
    def from_json(cls, item: dict) -> "Workspace":
        attrs = item.get("attributes", {})
        return cls(
            id=item["id"],
            name=attrs.get("name", "<unknown>"),
            locked=bool(attrs.get("locked", False)),
            resource_count=int(attrs.get("resource-count", 0) or 0),
            execution_mode=attrs.get("execution-mode", "unknown"),
            terraform_version=attrs.get("terraform-version", "unknown"),
        )


def list_workspaces(client: Client, org: str) -> list[Workspace]:
    path = f"/organizations/{org}/workspaces?page%5Bsize%5D=100"
    return [Workspace.from_json(item) for item in client.paginate(path)]


def unlock_workspace(client: Client, workspace_id: str) -> None:
    """Unlock a workspace. Required before a queued run will actually execute —
    HCP Terraform accepts run creation on a locked workspace via the API but
    leaves it stuck at status 'pending' indefinitely without this."""
    client.post(f"/workspaces/{workspace_id}/actions/unlock", {})
