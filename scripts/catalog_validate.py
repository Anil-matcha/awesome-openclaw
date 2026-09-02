#!/usr/bin/env python3
"""Validate one or more providers/*.yaml catalog entries.

Usage:
    python3 scripts/catalog_validate.py providers/hunter.yaml
    python3 scripts/catalog_validate.py providers/*.yaml   # CI runs it over every changed file
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

REQUIRED_TOP = ["provider", "docs_url", "status", "auth", "pricing", "endpoints", "base_url"]
REQUIRED_AUTH = ["location", "format", "bad_key_behavior"]
REQUIRED_PRICING = ["model", "source_url", "checked"]
REQUIRED_ENDPOINT = ["id", "method", "path", "summary"]
VALID_STATUS = {"draft", "verified"}
VALID_AUTH_LOCATION = {"header", "query", "path"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Secrets that look like real keys, not placeholder text. Tuned loosely on purpose —
# false positives here just mean re-checking a file by hand, false negatives ship a leak.
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT-shaped
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
]
PLACEHOLDER_HINTS = {"{key}", "your-key", "your_api_key", "xxxx", "example", "changeme", "<key>"}


def fail(errors, msg):
    errors.append(msg)


def check_secrets(raw_text, errors):
    for pat in SECRET_PATTERNS:
        for m in pat.finditer(raw_text):
            token = m.group(0)
            if any(h in token.lower() for h in PLACEHOLDER_HINTS):
                continue
            fail(errors, f"possible real secret matched pattern {pat.pattern!r}: {token[:12]}...")


def validate_entry(path):
    errors = []
    raw_text = path.read_text()
    check_secrets(raw_text, errors)

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as e:
        return [f"invalid YAML: {e}"]

    if not isinstance(data, dict):
        return ["top-level document must be a mapping"]

    for field in REQUIRED_TOP:
        if field not in data:
            fail(errors, f"missing required top-level field: {field}")

    if data.get("provider") and path.stem != "_TEMPLATE":
        expected = data["provider"]
        if path.stem != expected:
            fail(errors, f"filename {path.stem}.yaml does not match provider: {expected}")

    if data.get("status") not in VALID_STATUS and "status" in data:
        fail(errors, f"status must be one of {VALID_STATUS}, got {data.get('status')!r}")

    auth = data.get("auth") or {}
    for field in REQUIRED_AUTH:
        if not auth.get(field):
            fail(errors, f"auth.{field} is required and must be non-empty")
    if auth.get("location") and auth["location"] not in VALID_AUTH_LOCATION:
        fail(errors, f"auth.location must be one of {VALID_AUTH_LOCATION}")

    pricing = data.get("pricing") or {}
    for field in REQUIRED_PRICING:
        if not pricing.get(field):
            fail(errors, f"pricing.{field} is required and must be non-empty")
    checked = pricing.get("checked")
    if checked and not DATE_RE.match(str(checked)):
        fail(errors, f"pricing.checked must be YYYY-MM-DD, got {checked!r}")

    endpoints = data.get("endpoints") or []
    if not endpoints:
        fail(errors, "at least one endpoint is required")
    seen_ids = set()
    for i, ep in enumerate(endpoints):
        for field in REQUIRED_ENDPOINT:
            if not ep.get(field):
                fail(errors, f"endpoints[{i}].{field} is required and must be non-empty")
        eid = ep.get("id")
        if eid:
            if not ID_RE.match(eid):
                fail(errors, f"endpoints[{i}].id {eid!r} must look like <provider>.<action>")
            if eid in seen_ids:
                fail(errors, f"duplicate endpoint id: {eid}")
            seen_ids.add(eid)

    if data.get("status") == "verified":
        example_path = path.parent.parent / "examples" / f"{data.get('provider', path.stem)}.json"
        if not example_path.exists():
            fail(errors, f"status: verified requires a captured example at {example_path}")

    return errors


def main(argv):
    if not argv:
        print("usage: catalog_validate.py providers/<file>.yaml [more files...]")
        return 2

    any_failed = False
    for arg in argv:
        path = Path(arg)
        if path.name == "_TEMPLATE.yaml":
            continue
        if not path.exists():
            print(f"SKIP {arg}: not found")
            continue
        errors = validate_entry(path)
        if errors:
            any_failed = True
            print(f"FAIL {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"OK   {path}")

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
