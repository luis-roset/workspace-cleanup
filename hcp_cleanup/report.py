"""Write JSON + Markdown reports summarizing a destroy run across workspaces."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


@dataclass
class WorkspaceOutcome:
    name: str
    workspace_id: str
    outcome: str  # "success", "failed", "skipped"
    run_id: str | None
    final_status: str | None
    detail: str


def write_reports(org: str, hostname: str, outcomes: list[WorkspaceOutcome]) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = REPORTS_DIR / f"destroy-report-{org}-{timestamp}.json"
    md_path = REPORTS_DIR / f"destroy-report-{org}-{timestamp}.md"

    succeeded = [o for o in outcomes if o.outcome == "success"]
    failed = [o for o in outcomes if o.outcome == "failed"]
    skipped = [o for o in outcomes if o.outcome == "skipped"]

    payload = {
        "organization": org,
        "hostname": hostname,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(outcomes),
            "succeeded": len(succeeded),
            "failed": len(failed),
            "skipped": len(skipped),
        },
        "workspaces": [asdict(o) for o in outcomes],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# HCP Terraform destroy report — {org}",
        "",
        f"- Host: `{hostname}`",
        f"- Generated: {payload['generated_at']}",
        f"- Total workspaces: {len(outcomes)}",
        f"- Succeeded: {len(succeeded)}",
        f"- Failed: {len(failed)}",
        f"- Skipped: {len(skipped)}",
        "",
    ]

    def table(title: str, rows: list[WorkspaceOutcome]) -> list[str]:
        if not rows:
            return [f"## {title}", "", "_none_", ""]
        out = [f"## {title}", "", "| Workspace | Run ID | Status | Detail |", "|---|---|---|---|"]
        for o in rows:
            out.append(f"| {o.name} | {o.run_id or '-'} | {o.final_status or '-'} | {o.detail} |")
        out.append("")
        return out

    lines += table("Failed", failed)
    lines += table("Skipped", skipped)
    lines += table("Succeeded", succeeded)

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path
