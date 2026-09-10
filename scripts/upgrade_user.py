#!/usr/bin/env python3
"""
Manually upgrade a user to Premium Lifetime in PostgreSQL and dispatch the VIP Welcome Email.

Usage:
    python scripts/upgrade_user.py <email> [plan] [--no-email]

Examples:
    python scripts/upgrade_user.py halfradiationllc@gmail.com
    python scripts/upgrade_user.py halfradiationllc@gmail.com studio
    python scripts/upgrade_user.py buyer@domain.com personal --no-email
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import database
import main

def upgrade_user(email: str, plan: str = "personal", send_email: bool = True):
    email_clean = email.lower().strip()
    plan_clean = plan.lower().strip()
    if plan_clean not in ("personal", "studio", "yearly", "monthly"):
        plan_clean = "personal"

    print(f"=== Manual Premium Upgrade for: {email_clean} ===")
    
    # 1. Lookup user in database
    user = database.get_user_by_email(email_clean)
    if not user:
        print(f"Error: User with email '{email_clean}' does not exist in the database.")
        print("Tip: Ask the customer to sign up first, or create their account before upgrading.")
        return False

    current_tier = user.get("tier")
    current_plan = user.get("plan")
    print(f"Current Status: Tier='{current_tier}', Plan='{current_plan}' (User ID: {user.get('id')})")

    # 2. Update tier and plan in PostgreSQL
    database.update_user_tier(
        email=email_clean,
        tier="premium",
        stripe_customer_id=user.get("stripe_customer_id") or "manual_admin_grant",
        plan=plan_clean
    )

    # Verify update
    updated_user = database.get_user_by_email(email_clean)
    if not updated_user or updated_user.get("tier") != "premium":
        print("Error: Failed to verify tier update in PostgreSQL.")
        return False

    print(f"Database Updated: Tier='premium', Plan='{plan_clean}' successfully saved.")

    # 3. Clean up any pending premium records
    try:
        database.delete_pending_premium(email_clean)
    except Exception:
        pass

    # 4. Dispatch VIP Welcome Email
    if send_email:
        print("Dispatching VIP Welcome Email via Resend...")
        ok, err = main.send_vip_purchase_email(email_clean, plan=plan_clean)
        if ok:
            print("VIP Welcome Email successfully delivered! Subject: 'Welcome to bipluk+ Lifetime!'")
        else:
            print(f"Warning: Could not send VIP email: {err}")
    else:
        print("Skipping email dispatch (--no-email flag active).")

    print(f"Successfully upgraded {email_clean} to bipluk+ ({plan_clean.capitalize()} Plan)!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/upgrade_user.py <email> [plan] [--no-email]")
        sys.exit(1)

    target_email = sys.argv[1]
    target_plan = "personal"
    should_send_email = True

    for arg in sys.argv[2:]:
        if arg.lower() in ("--no-email", "-no-email", "--noemail"):
            should_send_email = False
        elif arg.lower() in ("personal", "studio", "yearly", "monthly"):
            target_plan = arg.lower()

    ok = upgrade_user(target_email, plan=target_plan, send_email=should_send_email)
    sys.exit(0 if ok else 1)
