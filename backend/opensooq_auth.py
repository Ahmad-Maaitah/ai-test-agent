"""
Self-contained OpenSooq logged-out token helper.
Drop this single file into any project (stdlib only, no third-party packages) and:
    from opensooq_auth import get_logged_out_token
    result = get_logged_out_token()
    print(result["LoggedoutToken"])
What it does
------------
1. POSTs to https://api.opensooq.com/v2.1/configurations/token with a freshly
   generated X-Tracking-UUID on every call.
2. Reads the ticket pair from result.data.ticket -> [ticket_id, ticket_token].
3. Builds the logged-out JWT (port of the Android AuthManager) using
   sub = X-Tracking-UUID, at0 = ticket_id, signing key = ticket_token.
Individual pieces are public if you only need part of the flow:
    build_headers()           -> request headers with a new X-Tracking-UUID
    fetch_ticket()            -> ticket pair + tracking uuid, no JWT
    build_logged_out_token()  -> JWT from values you already have
Python 3.9+.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

__all__ = [
    "OpenSooqError",
    "BASE_HEADERS",
    "TOKEN_URL",
    "TOKEN_URL_STG",
    "build_headers",
    "build_logged_out_token",
    "fetch_ticket",
    "get_logged_out_token",
]

TOKEN_URL = "https://api.opensooq.com/v2.1/configurations/token"
TOKEN_URL_STG = "https://apiv.sooqtest.com/v2.1/configurations/token"
DEFAULT_TIMEOUT = 20.0


def _resolve_token_url(env: str = "prod") -> str:
    """Return the configurations/token URL for prod or stg."""
    normalized = (env or "prod").strip().lower()
    if normalized in ("stg", "staging", "sooqtest", "test"):
        return TOKEN_URL_STG
    return TOKEN_URL

# Every header from the reference request except X-Tracking-UUID, which is
# regenerated per call. Override any of these via the `headers` argument.
BASE_HEADERS: Dict[str, str] = {
    "country": "jo",
    "appVersion": "453",
    "ConnectionType": "WIFI",
    "device_timezone": "UTC+03:00",
    "User-Agent": "OpenSooq/453/v2.1/8 (Android-12/samsung,SM-N975F)",
    "source": "android",
    "always-200": "1",
    "screen_resolution": "1080x2156",
    "uuid": "28311c83-9195-4d32-979d-06fa9be4b999",
    "display-mode": "normal",
    "latency_ms": "332",
    "release-version": "12.6.00.04_QA",
    "abBucket": "8",
    "vpnEnabled": "false",
    "currency": "JOD",
    "Accept-Language": "ar",
    "device_language": "en",
    "session-id": "8ecfdf10-7646-48d7-8135-65b73a30379a",
    "Cookie": (
        "NEXT_LOCALE=ar; default_currency=OMR; ecountry=om; "
        "session=%7B%22id%22%3A%22bfd639e2c18b-47773d1c80e1-5dce-4b1d-8c99-88938c4d1940%22%2C"
        "%22startedAt%22%3A1784404309836%7D; source=desktop; userABBucket=8"
    ),
}

# --- AuthManager constants (do not change: they are baked into the signature) ---
_HMAC_KEY = "7dcaETkYfMkKx1EmNpk/+fU4QNRnyEICdMAdq+tdf+urkTny"
_AUD_SEED = "AIzaSyDH9E6A4qW7IqXPRVQNhHAJe4mrs"
_AUDIENCE = "android"
_EXPIRY_OFFSET_SECONDS = 15000
_audience_secret_cache: Optional[str] = None


class OpenSooqError(RuntimeError):
    """Raised when the token request fails or returns an unexpected body."""

    def __init__(self, message: str, payload: Any = None):
        super().__init__(message)
        self.payload = payload


# ---------------------------------------------------------------- JWT building

def _url_safe(raw: bytes) -> str:
    """Base64 with '+' -> '-', '/' -> '_', padding stripped (Java getUrlSafe)."""
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _hmac_sha256(data: str, key: str) -> str:
    digest = hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).digest()
    return _url_safe(digest)


def _encode_json(payload: Dict[str, Any]) -> str:
    return _url_safe(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


def _audience_secret() -> str:
    global _audience_secret_cache
    if not _audience_secret_cache:
        _audience_secret_cache = _hmac_sha256(_AUD_SEED, _HMAC_KEY)
    return _audience_secret_cache


def build_logged_out_token(
    member_id: str,
    auth_time: str,
    auth_secret: str,
    now_ms: Optional[int] = None,
    rnd: Optional[str] = None,
) -> str:
    """Port of AuthManager.get().
    member_id   : X-Tracking-UUID used for the request (or a real member id once logged in)
    auth_time   : ticket[0]
    auth_secret : ticket[1]
    now_ms / rnd are only for reproducible tests; leave them unset in production.
    """
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if rnd is None:
        rnd = "%d%d" % (random.randint(1000, 99999999), now_ms - 7)

    header = _encode_json({"alg": "HS256", "typ": "JWT"})
    payload = _encode_json(
        {
            "sub": member_id,
            "at0": auth_time,
            "exp": now_ms // 1000 + _EXPIRY_OFFSET_SECONDS,
            "aud": _AUDIENCE,
            "rnd": rnd,
        }
    )
    signing_input = header + "." + payload
    secret = _hmac_sha256(
        "%s.%s.%s.%s" % (_AUDIENCE, _audience_secret(), rnd, auth_time),
        auth_secret,
    )
    return signing_input + "." + _hmac_sha256(signing_input, secret)


# ------------------------------------------------------------- ticket fetching

def build_headers(overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """BASE_HEADERS plus a brand-new X-Tracking-UUID for this call."""
    headers = dict(BASE_HEADERS)
    headers["X-Tracking-UUID"] = str(uuid.uuid4())
    if overrides:
        headers.update({k: v for k, v in overrides.items() if v is not None})
    return headers


def fetch_ticket(
    headers: Optional[Dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    env: str = "prod",
) -> Dict[str, Any]:
    """Call the configurations/token endpoint and return the ticket pair."""
    token_url = _resolve_token_url(env)
    request_headers = build_headers(headers)
    request = urllib.request.Request(
        token_url, data=b"", headers=request_headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise OpenSooqError("Request to OpenSooq failed: %s" % exc) from exc

    try:
        parsed = json.loads(body)
    except ValueError as exc:
        raise OpenSooqError("OpenSooq returned a non-JSON response") from exc

    # 'always-200: 1' makes the upstream answer HTTP 200 even for failures, so the
    # real outcome has to be read from the body.
    result = parsed.get("result") or {}
    status = result.get("status")
    if not parsed.get("success") or status != 200:
        raise OpenSooqError(
            "OpenSooq rejected the token request (status %s)" % status, parsed
        )

    ticket = (result.get("data") or {}).get("ticket")
    if not isinstance(ticket, list) or len(ticket) < 2:
        raise OpenSooqError("OpenSooq response did not contain a ticket pair", parsed)

    return {
        "env": "stg" if token_url == TOKEN_URL_STG else "prod",
        "token_url": token_url,
        "tracking_uuid": request_headers["X-Tracking-UUID"],
        "ticket_id": ticket[0],
        "ticket_token": ticket[1],
        "hash": result.get("hash"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def get_logged_out_token(
    headers: Optional[Dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    env: str = "prod",
) -> Dict[str, Any]:
    """Fetch a ticket and return it together with the logged-out JWT.
    Returns keys: env, token_url, tracking_uuid, ticket_id, ticket_token, hash,
    fetched_at, LoggedoutToken.
    """
    record = fetch_ticket(headers=headers, timeout=timeout, env=env)
    record["LoggedoutToken"] = build_logged_out_token(
        member_id=record["tracking_uuid"],
        auth_time=str(record["ticket_id"]),
        auth_secret=str(record["ticket_token"]),
    )
    return record


if __name__ == "__main__":
    print(json.dumps(get_logged_out_token(), indent=2))
