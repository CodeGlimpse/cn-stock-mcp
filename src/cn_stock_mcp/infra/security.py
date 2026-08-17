from __future__ import annotations

import re
from collections.abc import Iterable


_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(\b(?:token|api[-_ ]?key|secret|password|authorization|bearer)\b\s*[:=]\s*)([^\s,;&}\"']+)"
)
_URL_TOKEN = re.compile(r"(?i)([?&]token=)([^&#\s]+)")


def redact_sensitive_text(value: object, secrets: Iterable[str] | None = None) -> str:
    """Return diagnostic-safe text without credential-like values."""
    text = str(value)
    for secret in secrets or ():
        candidate = str(secret or "").strip()
        if candidate:
            text = text.replace(candidate, "<redacted>")
    text = _URL_TOKEN.sub(r"\1<redacted>", text)
    return _SECRET_ASSIGNMENT.sub(r"\1<redacted>", text)
