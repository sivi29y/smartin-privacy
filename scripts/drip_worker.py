import os
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from drip_templates import WELCOME_SERIES

# Load local environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cgjhjpairujduvctezfp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

def get_active_newsletter_subscribers():
    """Fetches users with status='active' and source matching Newsletter."""
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY is missing from .env")
        return []

    # Fetch users who are active, signed up via Newsletter, and haven't finished the drip series
    url = f"{SUPABASE_URL}/rest/v1/waitlist_emails?status=eq.active&source=like.*Newsletter*&drip_step=lt.7"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"FETCH ERROR: {e}")
        return []

def send_drip_email(email, step):
    """Sends the specific drip email template via Resend"""
    template = WELCOME_SERIES.get(step)
    if not template:
        return False
        
    print(f"Sending Drip Email #{step} to {email}...")

    resend_url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": "Smartin <roasts@smartinthe.app>", 
        "to": [email],
        "subject": template["subject"],
        "text": template["body"]
    }

    try:
        response = requests.post(resend_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            print(f"RESEND ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"RESEND REQUEST FAILED: {e}")
        return False

def advance_drip_step(user_email, current_step):
    """Updates the record's drip_step in Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/waitlist_emails?email=eq.{user_email}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    data = {
        "drip_step": current_step + 1
    }
    
    try:
        requests.patch(url, headers=headers, json=data)
    except Exception as e:
        print(f"UPDATE ERROR FOR {user_email}: {e}")

def run_drip_campaign():
    """Main execution loop for the Drip Sequence"""
    print(f"--- Welcome Drip Sprint: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    subscribers = get_active_newsletter_subscribers()
    if not subscribers:
        print("No active newsletter subscribers need nurturing today.")
        return

    print(f"Found {len(subscribers)} active newsletter subscribers in the pipeline.")
    
    now = datetime.now(timezone.utc)

    for sub in subscribers:
        email = sub.get("email")
        confirmed_at_str = sub.get("confirmed_at")
        drip_step = sub.get("drip_step", -1)
        
        # If they somehow have no confirmed_at date, skip them
        if not confirmed_at_str:
            continue
            
        # Parse the ISO timestamp from Supabase
        try:
            confirmed_date = datetime.fromisoformat(confirmed_at_str.replace("Z", "+00:00"))
        except ValueError:
            continue
            
        days_active = (now - confirmed_date).days
        
        # Determine which email they should get next
        next_step = drip_step + 1 if drip_step != -1 else 0
        
        # Guard: Have they completed the sequence?
        if next_step not in WELCOME_SERIES:
            continue
            
        target_delay = WELCOME_SERIES[next_step]["days_delay"]
        
        # Check if they have been active long enough to receive the next email
        # To avoid sending multiple caught-up emails in one day, we check EXACTLY or past the target day.
        # But we only advance one step per run.
        if days_active >= target_delay:
            success = send_drip_email(email, next_step)
            if success:
                advance_drip_step(email, next_step)
                print(f"SUCCESS: Advanced {email} to drip_step {next_step + 1}")

if __name__ == "__main__":
    run_drip_campaign()
