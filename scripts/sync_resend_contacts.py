#!/usr/bin/env python3
"""
Sync PostgreSQL database users and newsletter subscribers into Resend Contacts and Segments.
Uses the Resend CLI authenticated session.
"""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import database

SEGMENT_FREE = "fa00f7a7-1009-4e68-a6c9-3d4f6040eec4"       # Free Vault Leads
SEGMENT_VIP = "d2e2d72e-766b-44f2-b139-9cf67421b018"        # VIP Paid Members
SEGMENT_GENERAL = "4711d46a-e61b-4dbf-b547-a6a1a5462bf3"    # General

RESEND_BIN = "resend.cmd" if os.name == "nt" else "resend"


def extract_first_name(email_str: str) -> str:
    if not email_str:
        return "Synth Enthusiast"
    local = email_str.split("@")[0]
    parts = re.split(r"[\._\-\+0-9]+", local)
    cleaned = [p.capitalize() for p in parts if p and len(p) > 1]
    return cleaned[0] if cleaned else "Synth Enthusiast"


def mask_email(email_str: str) -> str:
    if not email_str or "@" not in email_str:
        return "***"
    user, domain = email_str.split("@", 1)
    masked_user = (user[0] + "***" + user[-1]) if len(user) > 2 else "***"
    return f"{masked_user}@{domain}"


def sync_single_contact(user_data: dict) -> tuple[str, bool, str]:
    email = user_data["email"]
    first_name = user_data["first_name"]
    tier = user_data["tier"]
    plan = user_data["plan"]
    is_unsubscribed = user_data["is_unsubscribed"]
    segment_id = user_data["segment_id"]

    cmd = [
        RESEND_BIN,
        "contacts",
        "create",
        "--email", email,
        "--first-name", first_name,
        "--properties", json.dumps({"plan": plan, "tier": tier}),
        "--segment-id", segment_id,
        "--segment-id", SEGMENT_GENERAL,
    ]

    if is_unsubscribed:
        cmd.append("--unsubscribed")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=(os.name == "nt"))
        if proc.returncode == 0:
            return email, True, "synced"
        else:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            return email, False, err_msg
    except Exception as e:
        return email, False, str(e)


def main():
    print("=" * 60)
    print("🚀 Starting Resend Contacts & Audience Sync")
    print("=" * 60)

    # 1. Fetch DB users and unsubscribed list
    all_users = database.get_all_users()
    conn = database.get_db_connection()
    unsubscribed_set = set()
    subscribers_set = set()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM unsubscribed_emails")
        unsubscribed_set = {row[0].lower().strip() for row in cursor.fetchall()}

        cursor.execute("SELECT email FROM subscribers")
        subscribers_set = {row[0].lower().strip() for row in cursor.fetchall()}
    finally:
        conn.close()

    # Consolidate distinct contacts map
    contacts_map = {}

    for u in all_users:
        email = u.get("email", "").lower().strip()
        if not email or "@" not in email:
            continue

        raw_tier = (u.get("tier") or "free").lower().strip()
        is_paid = raw_tier in ["premium", "personal", "studio", "vip"]
        tier_label = "premium" if is_paid else "free"
        plan_label = u.get("plan") or ("lifetime" if is_paid else "free")
        segment_id = SEGMENT_VIP if is_paid else SEGMENT_FREE

        contacts_map[email] = {
            "email": email,
            "first_name": extract_first_name(email),
            "tier": tier_label,
            "plan": plan_label,
            "is_unsubscribed": email in unsubscribed_set,
            "segment_id": segment_id,
        }

    # Include any standalone newsletter subscribers if not already in users
    for email in subscribers_set:
        if email not in contacts_map:
            contacts_map[email] = {
                "email": email,
                "first_name": extract_first_name(email),
                "tier": "free",
                "plan": "free",
                "is_unsubscribed": email in unsubscribed_set,
                "segment_id": SEGMENT_FREE,
            }

    contact_list = list(contacts_map.values())
    total_contacts = len(contact_list)
    free_count = sum(1 for c in contact_list if c["tier"] == "free")
    vip_count = sum(1 for c in contact_list if c["tier"] == "premium")
    unsub_count = sum(1 for c in contact_list if c["is_unsubscribed"])

    print(f"📊 Total DB contacts found: {total_contacts}")
    print(f"   • Free Vault Leads:     {free_count}")
    print(f"   • VIP Paid Members:     {vip_count}")
    print(f"   • Unsubscribed:         {unsub_count}")
    print("-" * 60)
    print("⏳ Uploading to Resend Contacts & assigning Segments...")

    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(sync_single_contact, c): c for c in contact_list}
        for future in as_completed(futures):
            c_data = futures[future]
            email, ok, status = future.result()
            masked = mask_email(email)
            if ok:
                success_count += 1
                tier_badge = "💎 VIP" if c_data["tier"] == "premium" else "🆓 FREE"
                unsub_badge = " [OPT-OUT]" if c_data["is_unsubscribed"] else ""
                print(f"   ✅ {masked:<28} {tier_badge}{unsub_badge}")
            else:
                fail_count += 1
                print(f"   ❌ {masked:<28} Failed: {status}")

    print("=" * 60)
    print(f"🎉 Sync Complete! Successfully synced: {success_count}/{total_contacts} (Failed: {fail_count})")
    print("=" * 60)


if __name__ == "__main__":
    main()
