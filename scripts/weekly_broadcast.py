import os
import glob
import re
import random
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

PERSONAS = [
    {
        "name": "Cosmo",
        "intro": "Hello, this is Cosmo from Smartin. I've been screaming at the ticker tape all week, and frankly, my blood pressure can't take much more of this market. But before I stroke out, here is what our team chewed up and spit out this week:",
        "outro": "Keep your stomach out of it, and don't let them hustle you!"
    },
    {
        "name": "Kurt",
        "intro": "Hello, this is Kurt from Smartin. I've spent the last 120 hours running the exact same Peter Lynch models over and over again because nobody else here respects the math! Here are the undeniable, hard-coded fundamentals we processed this week:",
        "outro": "Trust the numbers. So it goes."
    },
    {
        "name": "Jerry",
        "intro": "Hello, this is Jerry from Smartin. What's the deal with these valuations?! Seriously, who looks at these P/E ratios and says 'Yeah, that makes sense'? Here is what we found hiding in the filings this week:",
        "outro": "See you in the market, and try to keep a straight face."
    }
]

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
            description = ""
            permalink = ""
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
                
            # Extract description
            desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
            if desc_match:
                description = desc_match.group(1)
                
            # Extract permalink
            permalink_match = re.search(r'^permalink:\s*(.*?)$', content, re.MULTILINE)
            if permalink_match:
                permalink = permalink_match.group(1).strip()
            
            if permalink:
                recent_posts.append({
                    "title": title,
                    "description": description,
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

def send_weekly_broadcast(email, recent_posts, persona):
    """Sends the compiled weekly summary via Resend"""
    resend_url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Render the posts HTML and Text blocks
    posts_html = ""
    posts_text = ""
    for post in recent_posts:
        posts_html += f"""
        <div style="margin-bottom: 24px;">
            <h3 style="margin-bottom: 4px; color: #d32f2f;">{post['title']}</h3>
            <p style="margin-top: 0; font-size: 14px; line-height: 1.5; color: #555;">{post['description']}</p>
            <a href='{post['url']}' style="color: #0066cc; font-weight: bold; text-decoration: none;">[ Read the full roast ] &rarr;</a>
        </div>
        """
        
        posts_text += f"\n- {post['title']}\n  {post['description']}\n  URL: {post['url']}\n"
    
    html_body = f"""
    <div style="font-family: sans-serif; color: #111; max-width: 600px; line-height: 1.5;">
        <p>{persona['intro']}</p>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 24px 0;">
        
        {posts_html}
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 24px 0;">
        
        <p>{persona['outro']}</p>
        <p><strong>- The Smartin Team</strong></p>
    </div>
    """

    text_body = f"{persona['intro']}\n\n{posts_text}\n\n{persona['outro']}\n- The Smartin Team"
    
    payload = {
        "from": f"{persona['name']} at Smartin <roasts@smartinthe.app>", 
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
        
    subscribers = get_broadcast_audience()
    if not subscribers:
        print("No subscribers are eligible for the weekly broadcast (drip_step < 7).")
        return

    print(f"Found {len(subscribers)} eligible subscribers for the broadcast.")
    
    # Pick the host persona globally per broadcast so everyone gets the same one this week
    persona = random.choice(PERSONAS)
    print(f"Randomly selected broadcast host: {persona['name']}")
    
    success_count = 0
    for sub in subscribers:
        email = sub.get("email")
        if send_weekly_broadcast(email, recent_posts, persona):
            success_count += 1
            
    print(f"Successfully broadcasted to {success_count}/{len(subscribers)} subscribers.")

if __name__ == "__main__":
    run_weekly_broadcast()
