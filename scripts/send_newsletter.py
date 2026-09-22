#!/usr/bin/env python3
"""Send biweekly newsletter via Resend from GitHub Actions (not Vercel — CF 1010)."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import settings

SITE = settings.SITE_BASE
CRON_SECRET = settings.CRON_SECRET
RESEND_API_KEY = settings.RESEND_API_KEY
RESEND_NEWSLETTER_AUDIENCE_ID = settings.RESEND_NEWSLETTER_AUDIENCE_ID


def http_json(method: str, url: str, body: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {CRON_SECRET}", "User-Agent": "knob.monster-newsletter/1.0"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_resend(
    to: str,
    subject: str,
    body: str,
    from_addr: str,
    reply_to: str,
    list_unsubscribe: str,
) -> tuple[bool, str | None]:
    payload = {
        "from": from_addr,
        "to": [to],
        "subject": subject,
        "text": body,
        "reply_to": [reply_to],
        "headers": {
            "List-Unsubscribe": f"<{list_unsubscribe}>",
            "Precedence": "bulk",
        },
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "knob.monster-newsletter/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        return True, None
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        return False, f"HTTP {err.code}: {detail}"
    except Exception as err:
        return False, str(err)


def resend_request(method: str, path: str, payload: dict | None = None) -> tuple[bool, dict[str, Any] | None, str | None]:
    if not RESEND_API_KEY:
        return False, None, "RESEND_API_KEY is not configured"
    req = urllib.request.Request(
        f"https://api.resend.com{path}",
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={
            "Authorization": f"******",
            "Content-Type": "application/json",
            "User-Agent": "knob.monster-newsletter/1.0",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return True, json.loads(raw), None
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        return False, None, f"HTTP {err.code}: {detail}"
    except Exception as err:
        return False, None, str(err)


def sync_contact_to_audience(email: str, audience_id: str) -> tuple[bool, str | None]:
    email = (email or "").strip().lower()
    if not email:
        return False, "missing email"
    payload = {"email": email}
    primary_ok, _, primary_err = resend_request("POST", f"/audiences/{audience_id}/contacts", payload)
    if primary_ok:
        return True, None
    if primary_err and "already exists" in primary_err.lower():
        return True, None

    fallback_payload = {"email": email, "audience_id": audience_id}
    fallback_ok, _, fallback_err = resend_request("POST", "/contacts", fallback_payload)
    if fallback_ok:
        return True, None
    if fallback_err and "already exists" in fallback_err.lower():
        return True, None
    return False, fallback_err or primary_err


def create_and_send_broadcast(audience_id: str, from_addr: str, reply_to: str, subject: str, body: str) -> tuple[bool, str | None]:
    create_payload = {
        "audience_id": audience_id,
        "from": from_addr,
        "reply_to": reply_to,
        "subject": subject,
        "text": body,
    }
    created_ok, created, create_err = resend_request("POST", "/broadcasts", create_payload)
    if not created_ok or not created:
        return False, create_err or "failed to create broadcast"

    broadcast_id = created.get("id")
    if not broadcast_id:
        data = created.get("data") or {}
        broadcast_id = data.get("id")
    if not broadcast_id:
        return False, f"create broadcast missing id: {created}"

    send_ok, _, send_err = resend_request("POST", f"/broadcasts/{broadcast_id}/send", {})
    if not send_ok:
        return False, send_err or "failed to send broadcast"
    return True, None


def mask_email(email_str: str) -> str:
    if not email_str or "@" not in email_str:
        return "***"
    user, domain = email_str.split("@", 1)
    masked_user = (user[0] + "***" + user[-1]) if len(user) > 2 else "***"
    return f"{masked_user}@{domain}"


def main() -> int:
    if not RESEND_NEWSLETTER_AUDIENCE_ID:
        print("missing RESEND_NEWSLETTER_AUDIENCE_ID", file=sys.stderr)
        return 1

    queue = http_json("GET", f"{SITE}/api/cron/newsletter-pending")
    status = queue.get("status")
    if status == "skipped":
        print(json.dumps(queue, indent=2))
        return 0
    if status == "empty":
        print("no newsletter recipients")
        return 0
    if status != "ready":
        print(f"unexpected status: {status}", file=sys.stderr)
        return 1

    subject = queue["subject"]
    from_addr = queue["from"]
    reply_to = queue["reply_to"]
    recipients = queue.get("recipients") or []
    if not recipients:
        print("no newsletter recipients")
        return 0
    body_template = queue.get("body_template") or recipients[0].get("body") or ""
    body = body_template.replace("{{unsubscribe_token}}", "").strip()
    body = re.sub(r"https://bipluk\.com/unsubscribe\?token=\S+", "", body, flags=re.IGNORECASE).strip()

    synced_count = 0
    failed: list[dict] = []

    for item in recipients:
        email = item.get("email", "")
        masked = mask_email(email)
        ok, err = sync_contact_to_audience(email, RESEND_NEWSLETTER_AUDIENCE_ID)
        if ok:
            synced_count += 1
            print(f"synced: {masked}")
        else:
            failed.append({"email": email, "error": err})
            print(f"sync failed: {masked} — {err}", file=sys.stderr)
        time.sleep(0.2)

    broadcast_ok, broadcast_err = create_and_send_broadcast(
        RESEND_NEWSLETTER_AUDIENCE_ID,
        from_addr,
        reply_to,
        subject,
        body,
    )
    if not broadcast_ok:
        failed.append({"email": "broadcast", "error": broadcast_err})
        print(f"broadcast failed: {broadcast_err}", file=sys.stderr)
        sent_count = 0
    else:
        sent_count = synced_count

    result = http_json(
        "POST",
        f"{SITE}/api/cron/newsletter-ack",
        {
            "sent_count": sent_count,
            "failed_count": len(failed),
            "subject": subject,
            "failed": failed,
        },
    )
    print(json.dumps(result, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
