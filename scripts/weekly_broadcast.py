import os
import glob
import re
import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cgjhjpairujduvctezfp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
POSTS_DIR = "_posts"
SITE_URL = "https://smartinthe.app"

def get_recent_posts(days=7):
    """Parses markdown files to find posts published in the last `days` days."""
    if not os.path.exists(POSTS_DIR):
        print(f"Posts directory not found: {POSTS_DIR}")
        return []

    recent_posts = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)

    for filepath in glob.glob(os.path.join(POSTS_DIR, "*.md")):
        filename = os.path.basename(filepath)
        # Expected format: YYYY-MM-DD-title.md
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
        if not date_match:
            continue
            
        post_date_str = date_match.group(1)
        try:
            post_date = datetime.strptime(post_date_str, "%Y-%m-%d")
        except ValueError:
            continue
            
        if post_date >= cutoff_date:
            # Parse frontmatter
            title = "New Fintainment Roast"
            permalink = ""
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
                
            # Extract permalink
            permalink_match = re.search(r'^permalink:\s*(.*?)$', content, re.MULTILINE)
            if permalink_match:
                permalink = permalink_match.group(1).strip()
            
            if permalink:
                recent_posts.append({
                    "title": title,
                    "url": f"{SITE_URL}{permalink}"
                })

    return recent_posts

def get_broadcast_audience():
    """Fetches active subscribers who have finished the welcome drip (drip_step >= 7)."""
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY is missing from .env")
        return []

    # gte.7 means Greater Than or Equal to 7 (completed the 7-week series)
    url = f"{SUPABASE_URL}/rest/v1/waitlist_emails?status=eq.active&drip_step=gte.7"
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

def send_weekly_broadcast(email, posts_html, posts_text):
    """Sends the compiled weekly summary via Resend"""
    resend_url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    html_body = f"""
    <div style="font-family: sans-serif; color: #111;">
        <p>Hello!</p>
        <p>Here is what the Smartin algorithm and our writers chewed up and spit out this week:</p>
        <ul>
            {posts_html}
        </ul>
        <br>
        <p>Keep your stomach out of it,</p>
        <p><strong>The Smartin Team</strong></p>
    </div>
    """

    text_body = f"Hello!\n\nHere is what the Smartin algorithm and our writers chewed up and spit out this week:\n\n{posts_text}\n\nKeep your stomach out of it,\nThe Smartin Team"
    
    payload = {
        "from": "Smartin <roasts@smartinthe.app>", 
        "to": [email],
        "subject": "🥊 Your Weekly Smartin Roasts",
        "html": html_body,
        "text": text_body
    }

    try:
        response = requests.post(resend_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            print(f"RESEND ERROR for {email}: {response.text}")
            return False
    except Exception as e:
        print(f"RESEND REQUEST FAILED: {e}")
        return False

def run_weekly_broadcast():
    """Main execution loop for the Weekly Broadcast"""
    print(f"--- Weekly Broadcast Sprint: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    recent_posts = get_recent_posts(days=7)
    if not recent_posts:
        print("No new posts this week. Skipping broadcast.")
        return
        
    print(f"Found {len(recent_posts)} recent posts to broadcast.")
    
    # Build the email chunks
    posts_html = ""
    posts_text = ""
    for post in recent_posts:
        posts_html += f"<li><a href='{post['url']}'>{post['title']}</a></li>\n"
        posts_text += f"- {post['title']}: {post['url']}\n"
        
    subscribers = get_broadcast_audience()
    if not subscribers:
        print("No subscribers are eligible for the weekly broadcast (drip_step < 7).")
        return

    print(f"Found {len(subscribers)} eligible subscribers for the broadcast.")
    
    success_count = 0
    for sub in subscribers:
        email = sub.get("email")
        if send_weekly_broadcast(email, posts_html, posts_text):
            success_count += 1
            
    print(f"Successfully broadcasted to {success_count}/{len(subscribers)} subscribers.")

if __name__ == "__main__":
    run_weekly_broadcast()
