import os
import requests
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cgjhjpairujduvctezfp.supabase.co")
# IMPORTANT: This needs the SERVICE ROLE KEY (not Anon Key) to fetch and update private data
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Email Templates (Simplified for now - can be expanded to HTML files)
TEMPLATES = {
    "Waitlist": {
        "subject": "🚀 You're on the Smartin Waitlist!",
        "body": """
        Hello! 
        
        Thanks for joining the Smartin Android Waitlist. We're roasting stocks on iOS daily, and we'll let you know the second the Android version is ready.
        
        Please click the link below to confirm your interest and stay on the list:
        https://smartinthe.app/confirm?email={email}&token={token}
        
        Stay Smart,
        The Smartin Team
        """
    },
    "Newsletter": {
        "subject": "🥊 Welcome to the Smartin Roast List!",
        "body": """
        Hello!
        
        You're one step away from getting weekly stock comedy and brutal fundamental roasts delivered straight to your inbox.
        
        Please confirm your subscription by clicking here:
        https://smartinthe.app/confirm?email={email}&token={token}
        
        If you didn't sign up for this, you can safely ignore this email.
        
        See you in the market,
        The Smartin Team
        """
    }
}

def get_pending_subscribers():
    """Fetches users with status='pending' and notified_at=null"""
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY is missing from .env")
        return []

    url = f"{SUPABASE_URL}/rest/v1/waitlist_emails?status=eq.pending&notified_at=is.null"
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

def send_confirmation_email(subscriber):
    """Sends a confirmation email via Resend based on source"""
    email = subscriber.get("email")
    source = subscriber.get("source", "unknown")
    token = subscriber.get("token")

    # Generate a unique token if one doesn't exist
    if not token:
        token = str(uuid.uuid4())
    
    # Determine template bucket
    bucket = "Newsletter" if "Newsletter" in source else "Waitlist"
    template = TEMPLATES.get(bucket)
    
    print(f"Sending {bucket} confirmation to {email} with token...")

    resend_url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": "Smartin <roasts@smartinthe.app>", 
        "to": [email],
        "subject": template["subject"],
        "text": template["body"].format(email=email, token=token)
    }

    try:
        response = requests.post(resend_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200 or response.status_code == 201:
            return token # Return the token so we can save it
        else:
            print(f"RESEND ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"RESEND REQUEST FAILED: {e}")
        return False

def mark_as_notified(email, token):
    """Updates the record with notified_at timestamp and the secret token"""
    url = f"{SUPABASE_URL}/rest/v1/waitlist_emails?email=eq.{email}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    data = {
        "notified_at": datetime.now().isoformat(),
        "token": token
    }
    
    try:
        requests.patch(url, headers=headers, json=data)
    except Exception as e:
        print(f"UPDATE ERROR FOR {email}: {e}")

def run_automation_cycle():
    """Main execution loop"""
    print(f"--- Automation Sprint: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    subscribers = get_pending_subscribers()
    if not subscribers:
        print("No pending subscribers to notify.")
        return

    print(f"Found {len(subscribers)} pending subscribers.")
    
    for sub in subscribers:
        token = send_confirmation_email(sub)
        if token:
            mark_as_notified(sub["email"], token)
            print(f"SUCCESS: Email sent and token stored for {sub['email']}")

if __name__ == "__main__":
    run_automation_cycle()
