"""Create, confirm, and poll HCP Terraform destroy runs."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

from .api import ApiError, Client

_ERROR_LINE = re.compile(r"^Error: .+$", re.MULTILINE)

TERMINAL_STATUSES = {
    "applied",
    "planned_and_finished",
    "errored",
    "discarded",
    "canceled",
    "force_canceled",
}

SUCCESS_STATUSES = {"applied", "planned_and_finished"}

POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 1800  # 30 minutes per workspace


@dataclass
class RunResult:
    ok: bool
    run_id: str | None
    final_status: str | None
    detail: str


def _run_attrs(run_json: dict) -> dict:
    return run_json.get("data", {}).get("attributes", {})


def create_destroy_run(client: Client, workspace_id: str, message: str) -> dict:
    body = {
        "data": {
            "attributes": {
                "is-destroy": True,
                "message": message,
            },
            "type": "runs",
            "relationships": {
                "workspace": {"data": {"type": "workspaces", "id": workspace_id}}
            },
        }
    }
    return client.post("/runs", body)


def confirm_apply(client: Client, run_id: str, comment: str) -> None:
    client.post(f"/runs/{run_id}/actions/apply", {"comment": comment})


def poll_run(client: Client, run_id: str) -> tuple[str, dict]:
    """Poll until the run reaches a terminal status, confirming apply if needed.

    The confirm gate isn't always at status 'planned' — workspaces with cost
    estimation or Sentinel policies enabled pause at 'cost_estimated' or
    'policy_checked' instead, and only surface via actions.is-confirmable.
    Watching that flag directly (rather than one hardcoded status) covers all
    of those cases, including confirming and applying the cost estimate.
    """
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    confirmed = False
    while time.monotonic() < deadline:
        run_json = client.get(f"/runs/{run_id}")
        attrs = _run_attrs(run_json)
        status = attrs.get("status", "unknown")

        if status in TERMINAL_STATUSES:
            return status, attrs

        actions = attrs.get("actions", {})
        if not confirmed and actions.get("is-confirmable"):
            confirm_apply(client, run_id, "Confirmed by workspace-cleanup tool")
            confirmed = True

        time.sleep(POLL_INTERVAL_SECONDS)

    return "timeout", _run_attrs(client.get(f"/runs/{run_id}"))


def _parse_error_log(log_text: str) -> str:
    """Pull the most useful error message out of a plan/apply log.

    Terraform's JSON UI format (1.1+) emits one JSON object per line; look for
    @level == "error" first. Fall back to the plain-text "Error: ..." format
    for older logs or log lines that aren't JSON.
    """
    messages: list[str] = []
    for line in log_text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("@level") != "error":
            continue
        diagnostic = entry.get("diagnostic") or {}
        summary = diagnostic.get("summary") or entry.get("@message", "")
        detail = diagnostic.get("detail", "")
        text = f"{summary}: {detail}" if detail else summary
        if text and text not in messages:
            messages.append(text)

    if not messages:
        messages = list(dict.fromkeys(m.strip() for m in _ERROR_LINE.findall(log_text)))

    joined = " | ".join(messages)
    return joined[:500]


def explain_run_error(client: Client, run_id: str) -> str:
    """Best-effort lookup of why a run errored, for the report's 'detail' column."""
    try:
        run_json = client.get(f"/runs/{run_id}")
        rel = run_json.get("data", {}).get("relationships", {})

        apply_id = rel.get("apply", {}).get("data", {}).get("id")
        plan_id = rel.get("plan", {}).get("data", {}).get("id")

        log_url = None
        if apply_id:
            apply = client.get(f"/applies/{apply_id}")
            aattrs = apply.get("data", {}).get("attributes", {})
            if aattrs.get("status") not in (None, "unreachable", "pending"):
                log_url = aattrs.get("log-read-url")
        if not log_url and plan_id:
            plan = client.get(f"/plans/{plan_id}")
            pattrs = plan.get("data", {}).get("attributes", {})
            log_url = pattrs.get("log-read-url")

        if not log_url:
            return ""
        return _parse_error_log(client.fetch_text(log_url))
    except ApiError:
        return ""


def destroy_workspace(client: Client, workspace_id: str, message: str) -> RunResult:
    try:
        created = create_destroy_run(client, workspace_id, message)
    except ApiError as e:
        return RunResult(ok=False, run_id=None, final_status=None, detail=f"failed to create run: {e.detail}")

    run_id = created.get("data", {}).get("id")
    if not run_id:
        return RunResult(ok=False, run_id=None, final_status=None, detail="run created but no id returned")

    try:
        status, attrs = poll_run(client, run_id)
    except ApiError as e:
        return RunResult(ok=False, run_id=run_id, final_status=None, detail=f"polling failed: {e.detail}")

    if status in SUCCESS_STATUSES:
        detail = "destroyed" if status == "applied" else "no resources to destroy"
        return RunResult(ok=True, run_id=run_id, final_status=status, detail=detail)

    detail = f"run ended with status '{status}'"
    if status == "timeout":
        detail = f"timed out after {POLL_TIMEOUT_SECONDS}s waiting for run to finish"
    elif status == "errored":
        explanation = explain_run_error(client, run_id)
        if explanation:
            detail = f"errored: {explanation}"
    return RunResult(ok=False, run_id=run_id, final_status=status, detail=detail)
