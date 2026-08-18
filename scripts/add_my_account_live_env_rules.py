#!/usr/bin/env python3
"""
Add high-level Live Env rules for every API under the MY Account section
on the remote AI Test Agent server.

Flow mirrors the UI:
  Edit API -> Execute -> inspect response fields -> add high-level rules.

Usage:
  python3 scripts/add_my_account_live_env_rules.py
  python3 scripts/add_my_account_live_env_rules.py --base http://172.16.1.4:5001 --dry-run
"""

from __future__ import annotations

import argparse
import json
import random
import string
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple


DEFAULT_BASE = "http://172.16.1.4:5001"
SECTION_NAME = "MY Account"
MAX_MS = 3000
MAX_FIELD_RULES = 10  # keep high-level, not every nested leaf


def rule_id() -> str:
    return "rule-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=9))


def http_json(method: str, url: str, body: Optional[dict] = None, timeout: float = 60.0) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"error": raw[:500]}
        raise RuntimeError(f"HTTP {exc.code} for {url}: {payload}") from exc


def collect_section_apis(sections: List[dict], target_name: str) -> List[dict]:
    found: List[dict] = []

    def walk(node: dict) -> None:
        if (node.get("name") or "").strip() == target_name:
            found.extend(node.get("apis") or [])
            for child in node.get("children") or node.get("folders") or []:
                walk(child)
            return
        for child in node.get("children") or node.get("folders") or []:
            walk(child)

    for section in sections:
        walk(section)
    return found


def get_nested(data: Any, path: str) -> Tuple[Any, bool]:
    if not path or data is None:
        return None, False
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None, False
    return cur, True


def type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def pick_high_level_fields(response: Any, available_fields: List[str]) -> List[str]:
    """Choose a compact set of high-value fields for structural checks."""
    preferred = [
        "success",
        "result",
        "result.status",
        "result.data",
        "result.data.id",
        "result.data.full_name",
        "result.data.M_user_name",
        "result.data.first_name",
        "result.data.memberCountry",
        "result.data.wallet_amount",
        "result.data.bundle_count",
        "result.data.followersCount",
        "result.data.followingsCount",
        "result.data.adsFree",
        "data",
        "data.id",
        "error",
    ]

    chosen: List[str] = []
    field_set = set(available_fields or [])

    # Prefer known important paths that actually exist
    for path in preferred:
        if path in field_set and path not in chosen:
            chosen.append(path)

    # If response is a dict, add top-level keys
    if isinstance(response, dict):
        for key in response.keys():
            if key not in chosen:
                chosen.append(key)
            if len(chosen) >= 6:
                break
        # One level under result.data if present
        data_obj, ok = get_nested(response, "result.data")
        if ok and isinstance(data_obj, dict):
            for key in list(data_obj.keys())[:8]:
                path = f"result.data.{key}"
                if path not in chosen:
                    chosen.append(path)
                if len(chosen) >= MAX_FIELD_RULES + 4:
                    break

    # Fallback to first available fields
    if not chosen:
        for path in available_fields[:MAX_FIELD_RULES]:
            if path.count(".") <= 2:
                chosen.append(path)

    # Cap
    return chosen[: MAX_FIELD_RULES + 4]


def build_live_env_rules(
    response: Any,
    available_fields: List[str],
    status_code: Optional[int],
) -> List[dict]:
    rules: List[dict] = []

    rules.append(
        {
            "id": rule_id(),
            "type": "status_code",
            "field": "",
            "name": "Live Env - Status Code 200",
            "config": {"expectedStatus": 200},
            "enabled": True,
        }
    )
    rules.append(
        {
            "id": rule_id(),
            "type": "response_time",
            "field": "",
            "name": "Live Env - Response Time < 3000ms",
            "config": {"maxMs": MAX_MS},
            "enabled": True,
        }
    )

    fields = pick_high_level_fields(response, available_fields)

    # success flag
    if "success" in (available_fields or []) or (
        isinstance(response, dict) and "success" in response
    ):
        val, found = get_nested(response, "success")
        if found and isinstance(val, bool):
            rules.append(
                {
                    "id": rule_id(),
                    "type": "success_flag",
                    "field": "success",
                    "name": "Live Env - Success Is True",
                    "config": {"expectedValue": True},
                    "enabled": True,
                }
            )

    field_rule_count = 0
    for path in fields:
        if path in ("success",):
            continue
        val, found = get_nested(response, path)
        if not found:
            # still add exists if listed in available fields
            if path not in (available_fields or []):
                continue
            rules.append(
                {
                    "id": rule_id(),
                    "type": "field_exists",
                    "field": path,
                    "name": f"Live Env - Field Exists: {path}",
                    "config": {},
                    "enabled": True,
                }
            )
            field_rule_count += 1
            if field_rule_count >= MAX_FIELD_RULES:
                break
            continue

        rules.append(
            {
                "id": rule_id(),
                "type": "field_exists",
                "field": path,
                "name": f"Live Env - Field Exists: {path}",
                "config": {},
                "enabled": True,
            }
        )
        field_rule_count += 1

        # not-null for scalars / non-empty containers
        if val is not None and not (isinstance(val, (str, list, dict)) and len(val) == 0):
            rules.append(
                {
                    "id": rule_id(),
                    "type": "field_not_null",
                    "field": path,
                    "name": f"Live Env - Field Not Null: {path}",
                    "config": {},
                    "enabled": True,
                }
            )
            field_rule_count += 1

        # type check for a few important paths
        if path in (
            "result",
            "result.data",
            "result.data.id",
            "success",
            "result.data.full_name",
            "result.data.adsFree",
            "result.data.wallet_amount",
            "result.data.bundle_count",
        ) or path.count(".") <= 1:
            rules.append(
                {
                    "id": rule_id(),
                    "type": "field_type",
                    "field": path,
                    "name": f"Live Env - Field Type {type_name(val)}: {path}",
                    "config": {"expectedType": type_name(val)},
                    "enabled": True,
                }
            )
            field_rule_count += 1

        if field_rule_count >= MAX_FIELD_RULES:
            break

    return rules


def merge_rules(existing: List[dict], new_rules: List[dict]) -> Tuple[List[dict], int]:
    """Keep existing non-Live-Env rules; replace previous Live Env rules with fresh set."""
    kept = [r for r in (existing or []) if not str(r.get("name") or "").startswith("Live Env -")]
    before = len(existing or [])
    merged = kept + new_rules
    return merged, len(merged) - before


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Optional max APIs to process")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    print(f"[*] Loading sections from {base}")
    sections_payload = http_json("GET", f"{base}/api/sections")
    sections = sections_payload.get("sections") or []
    apis = collect_section_apis(sections, SECTION_NAME)
    if not apis:
        print(f"[!] No APIs found under section '{SECTION_NAME}'")
        return 1

    if args.limit and args.limit > 0:
        apis = apis[: args.limit]

    print(f"[*] Found {len(apis)} APIs under '{SECTION_NAME}'")
    summary = []

    for idx, api in enumerate(apis, 1):
        api_id = api.get("id")
        name = api.get("name") or api_id
        curl = api.get("curl") or ""
        print(f"\n[{idx}/{len(apis)}] {name} ({api_id})")

        if not curl.strip():
            print("  [SKIP] empty curl")
            summary.append((name, "SKIP", "empty curl", 0))
            continue

        try:
            executed = http_json(
                "POST",
                f"{base}/api/execute-curl",
                {"curl": curl, "apiId": api_id},
                timeout=90.0,
            )
        except Exception as exc:
            print(f"  [FAIL] execute-curl: {exc}")
            summary.append((name, "FAIL", str(exc)[:120], 0))
            continue

        status = executed.get("status_code")
        response = executed.get("response")
        fields = executed.get("fields") or []
        print(f"  execute status={status} fields={len(fields)}")

        if status != 200:
            print("  [WARN] non-200 response; still adding status/time Live Env rules only")
            new_rules = [
                {
                    "id": rule_id(),
                    "type": "status_code",
                    "field": "",
                    "name": "Live Env - Status Code 200",
                    "config": {"expectedStatus": 200},
                    "enabled": True,
                },
                {
                    "id": rule_id(),
                    "type": "response_time",
                    "field": "",
                    "name": "Live Env - Response Time < 3000ms",
                    "config": {"maxMs": MAX_MS},
                    "enabled": True,
                },
            ]
        else:
            new_rules = build_live_env_rules(response, fields, status)

        existing = api.get("customRules") or []
        merged, delta = merge_rules(existing, new_rules)
        print(f"  rules: existing={len(existing)} live_env={len(new_rules)} merged={len(merged)} (delta {delta:+d})")

        if args.dry_run:
            print("  [DRY-RUN] not saving")
            summary.append((name, "DRY", f"status={status}", len(new_rules)))
            continue

        try:
            updated = http_json(
                "PUT",
                f"{base}/api/apis/{api_id}",
                {"customRules": merged},
                timeout=30.0,
            )
            ok = bool(updated.get("success"))
            print(f"  save={'OK' if ok else 'FAIL'}")
            summary.append((name, "OK" if ok else "SAVE_FAIL", f"status={status}", len(new_rules)))
        except Exception as exc:
            print(f"  [FAIL] save: {exc}")
            summary.append((name, "SAVE_FAIL", str(exc)[:120], 0))

    print("\n========== SUMMARY ==========")
    ok_n = sum(1 for s in summary if s[1] == "OK")
    for name, state, info, n in summary:
        print(f"  [{state}] {name}: {info}; live_env_rules={n}")
    print(f"Done. Saved OK: {ok_n}/{len(summary)}")
    return 0 if ok_n or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
