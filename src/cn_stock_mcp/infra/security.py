from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


_SECRET_KEY = re.compile(
    r"(?i)^(?:token|access[_-]?token|api[-_ ]?key|secret|password|authorization|bearer|credential|cookie)$"
)
_SECRET_ASSIGNMENT_QUOTED = re.compile(
    r"(?i)([\"']?(?:token|access[_-]?token|api[-_ ]?key|secret|password|authorization|bearer|credential|cookie)[\"']?\s*[:=]\s*)([\"'])(.*?)(\2)"
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(\b(?:token|access[_-]?token|api[-_ ]?key|secret|password|authorization|bearer|credential|cookie)\b\s*[:=]\s*)([^\s,;&}\"']+)"
)
_BEARER_VALUE = re.compile(r"(?i)(\bBearer\s+)([^\s,;&}\"']+)")
_SECRET_BARE_VALUE = re.compile(
    r"(?i)(\b(?:access[_-]?token|api[-_ ]?key|secret|password|credential)\b\s+)([A-Za-z0-9._~+/=-]{8,})"
)
_URL_SECRET = re.compile(
    r"(?i)([?&](?:token|access[_-]?token|api[-_ ]?key|secret|password|authorization)=)([^&#\s]+)"
)


def _is_sensitive_key(value: object) -> bool:
    key = str(value or "").strip().strip("\"'").lower()
    compact = re.sub(r"[^a-z0-9]", "", key)
    if not compact:
        return False
    if _SECRET_KEY.fullmatch(key):
        return True
    return (
        compact.endswith("token")
        or compact.endswith("apikey")
        or compact.endswith("secret")
        or compact.endswith("password")
        or compact.endswith("authorization")
        or compact.endswith("credential")
        or compact.endswith("cookie")
    )


def redact_sensitive_text(value: object, secrets: Iterable[str] | None = None) -> str:
    """Return diagnostic-safe text without credential-like values."""
    text = str(value)
    for secret in secrets or ():
        candidate = str(secret or "").strip()
        if candidate:
            text = text.replace(candidate, "<redacted>")
    text = _URL_SECRET.sub(r"\1<redacted>", text)
    text = _SECRET_ASSIGNMENT_QUOTED.sub(r"\1\2<redacted>\4", text)
    text = _SECRET_ASSIGNMENT.sub(r"\1<redacted>", text)
    text = _BEARER_VALUE.sub(r"\1<redacted>", text)
    return _SECRET_BARE_VALUE.sub(r"\1<redacted>", text)


def redact_sensitive_value(value: Any, secrets: Iterable[str] | None = None) -> Any:
    """Recursively redact credential-like mapping values and text.

    This helper is intended for logs and diagnostic responses.  Mapping keys
    such as ``token`` are redacted without exposing their values, while other
    values are traversed so nested provider errors cannot accidentally leak a
    credential.
    """

    if isinstance(value, Mapping):
        redacted: dict[Any, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if _is_sensitive_key(key_text):
                redacted[key] = "<redacted>"
            else:
                redacted[key] = redact_sensitive_value(child, secrets)
        return redacted
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_sensitive_value(item, secrets) for item in value]
    if isinstance(value, str):
        return redact_sensitive_text(value, secrets)
    return value


def safe_validation_error_details(exc: Exception, secrets: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """Return validation details without echoing submitted input values."""

    raw_errors = exc.errors() if hasattr(exc, "errors") else []
    details: list[dict[str, Any]] = []
    for raw in raw_errors:
        if not isinstance(raw, Mapping):
            continue
        # Pydantic includes the submitted value under ``input``.  Omitting it
        # entirely prevents a malformed request from echoing a token or other
        # secret in the MCP response; the location/type/message remain useful.
        # ``ctx`` may contain an exception whose message embeds the submitted
        # value; it is not needed by an MCP caller once ``type``/``msg`` and
        # ``loc`` are present, so omit it along with ``input``.
        item = {key: value for key, value in raw.items() if key not in {"input", "ctx"}}
        item = redact_sensitive_value(item, secrets)
        if isinstance(item, Mapping):
            details.append(dict(item))
    return details
