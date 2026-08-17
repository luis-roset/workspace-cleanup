"""Minimal JSON:API client for the HCP Terraform / Terraform Enterprise API.

Uses only the standard library so the tool has zero external dependencies.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator


class ApiError(Exception):
    """Raised for any non-2xx response, with the JSON:API error detail extracted."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"HTTP {status}: {detail}")


class Client:
    def __init__(self, hostname: str, token: str):
        self.base_url = f"https://{hostname}/api/v2"
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self._headers)
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read()
            detail = raw.decode("utf-8", errors="replace")
            try:
                parsed = json.loads(detail)
                errors = parsed.get("errors", [])
                if errors:
                    detail = "; ".join(
                        f"{err.get('title', 'error')}: {err.get('detail', '')}".strip(": ")
                        for err in errors
                    )
            except json.JSONDecodeError:
                pass
            raise ApiError(e.code, detail) from None
        except urllib.error.URLError as e:
            raise ApiError(0, str(e.reason)) from None

    def get(self, path: str) -> dict:
        return self._request("GET", path)

    @staticmethod
    def fetch_text(url: str) -> str:
        """Fetch a plain-text resource (e.g. a plan/apply log) that isn't a JSON:API path."""
        try:
            with urllib.request.urlopen(url) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.HTTPError, urllib.error.URLError):
            return ""

    def post(self, path: str, body: dict) -> dict:
        return self._request("POST", path, body)

    def paginate(self, path: str) -> Iterator[dict]:
        """Yield every item in `data` across all pages of a JSON:API list endpoint."""
        next_path: str | None = path
        while next_path:
            page = self.get(next_path)
            yield from page.get("data", [])
            next_link = page.get("links", {}).get("next")
            next_path = next_link if next_link else None


def qs(params: dict[str, Any]) -> str:
    return urllib.parse.urlencode(params)
