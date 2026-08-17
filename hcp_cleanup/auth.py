"""Token resolution for HCP Terraform / Terraform Enterprise."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_HOSTNAME = "app.terraform.io"


class AuthError(Exception):
    """Raised when no usable API token can be found."""


def _host_env_var(hostname: str) -> str:
    """Terraform's per-host credential env var, e.g. TF_TOKEN_app_terraform_io.

    Dots become single underscores, hyphens become double underscores.
    """
    return "TF_TOKEN_" + hostname.replace("-", "__").replace(".", "_")


def _from_credentials_file(hostname: str) -> str | None:
    path = Path.home() / ".terraform.d" / "credentials.tfrc.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    token = data.get("credentials", {}).get(hostname, {}).get("token")
    return token or None


def resolve_token(hostname: str = DEFAULT_HOSTNAME, explicit: str | None = None) -> tuple[str, str]:
    """Return (token, source_description).

    Lookup order:
      1. explicit value (--token)
      2. TFE_TOKEN environment variable
      3. TF_TOKEN_<host> environment variable (what `terraform login` documents)
      4. ~/.terraform.d/credentials.tfrc.json (what `terraform login` writes)
    """
    if explicit:
        return explicit, "--token argument"

    if os.environ.get("TFE_TOKEN"):
        return os.environ["TFE_TOKEN"], "TFE_TOKEN env var"

    host_var = _host_env_var(hostname)
    if os.environ.get(host_var):
        return os.environ[host_var], f"{host_var} env var"

    token = _from_credentials_file(hostname)
    if token:
        return token, "~/.terraform.d/credentials.tfrc.json"

    raise AuthError(
        "No API token found for host '{host}'.\n"
        "Fix it with any one of:\n"
        "  terraform login {host}\n"
        "  export TFE_TOKEN='<your-token>'\n"
        "  export {var}='<your-token>'\n"
        "Create a token at https://{host}/app/settings/tokens".format(
            host=hostname, var=host_var
        )
    )
