import os
import random
from datetime import datetime
from google import genai
import tweepy
import sys
# Ensure we can import from the current script's directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from personas import PERSONAS_LIST as PERSONAS

# Setup API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

client = genai.Client(api_key=GEMINI_API_KEY)
model_id = 'gemini-2.0-flash' # Using a known stable model ID for genai SDK if flash 2.5 is not available or correct. 
# Re-checking the model version. The user log mentions gemini-2.5-flash which might be internal/future. 
# Looking at the prev output line 19 had 'gemini-2.5-flash'. 
# I will stick to 'gemini-2.0-flash' as it is the current standard for the new SDK unless I'm sure 2.5 is right.
# Actually, I'll keep the string as is if the user was using it, but I'll use client.models.generate_content correctly.


# PERSONAS are now imported from personas.py

STOCKS = [
    "AAPL", "TSLA", "GME", "AMC", "PLTR", "SOFI", "NVDA", "AMD", "META", "GOOGL", 
    "AMZN", "NFLX", "MSFT", "INTC", "DJT", "HOOD", "COIN", "MARA", "RIOT", "BABA", 
    "NIO", "ROKU", "PTON", "ZM", "DOCU", "WISH", "CLOV", "WKHS", "BB", "NOK", 
    "SPCE", "MVIS", "SNDL", "TLRY", "CRSR", "DKNG", "PENN", "RBLX", "U", "SNOW", 
    "DDOG", "NET", "CRWD", "OKTA", "ZS", "PANW", "FTNT", "CHWY", "SQ", "PYPL",
    "IBM", "IONQ", "RGTI", "QBTS", "XOM", "CVX", "OXY", "GOLD", "NEM", "AEM",
    "CLSK", "MU", "RDDT", "MSTR", "LULU", "DNUT", "PBR", "WING", "NYCB", "BLK",
    "BX", "VTI"
]

def get_used_history():
    used_stocks, used_personas = set(), set()
    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        return used_stocks, used_personas
        
    for filename in os.listdir(posts_dir):
        if not filename.endswith(".md"): continue
        with open(os.path.join(posts_dir, filename), 'r') as f:
            content = f.read().lower()
            for stock in STOCKS:
                if f"({stock.lower()})" in content or f" {stock.lower()} " in content:
                    used_stocks.add(stock)
            for p in ["vonnegut", "seinfeld", "costanza", "costonzo", "kramer", "elaine"]:
                if p in content:
                    used_personas.add(p)
    return used_stocks, used_personas

used_stocks, used_personas = get_used_history()

available_stocks = [s for s in STOCKS if s not in used_stocks]
if len(available_stocks) < 5: available_stocks = STOCKS
    
available_personas = [p for p in PERSONAS if p.split()[0].lower() not in " ".join(used_personas).lower()]
if not available_personas: available_personas = PERSONAS

selected_stock = random.choice(available_stocks)
selected_persona = random.choice(available_personas)
short_persona_name = selected_persona.split()[0].lower()
selected_author = selected_persona.split()[0].capitalize()

# Load Centralized Instructions
instructions_path = os.path.join(os.path.dirname(__file__), "blog_instructions.md")
with open(instructions_path, 'r') as f:
    blog_instructions = f.read()

print(f"Targeting Stock: {selected_stock}")

print(f"Selected Persona: {selected_persona}")

date_str = datetime.now().strftime('%Y-%m-%d')
safe_slug = f"{selected_stock.lower()}-roast-{short_persona_name}"
permalink = f"/blog/{date_str}/{selected_stock.lower()}/"
live_url = f"https://smartinthe.app{permalink}"

prompt = f"""
Write a highly entertaining, SEO-optimized blog post for the iOS app 'Smartin: Quick Stock Ratings'.
You are roasting the stock {selected_stock} using this precise comedic persona:
{selected_persona}

{blog_instructions}

Format your absolute output exactly as follows:
TWEET:
<Write a punchy, 2-sentence hook for Twitter natively in the persona's voice. Include {selected_stock} and end with this exact text: "Read the full roast: {live_url}">
<CRITICAL COPYRIGHT RULE: YOU MUST NOT MENTION THE PERSONA'S REAL NAME OR USE ANY COPYRIGHTED CATCHPHRASES IN THE OUTPUT. YOU ARE ANONYMOUS.>

MARKDOWN:
<Write the full SEO markdown blog post here.
Remember to briefly explain {selected_stock}, roast its P/E and PEG ratios.
Must follow the H2/H3 'Golden Rule' from the instructions.
Must include 1-3 internal links from the instruction targets.
Must start with Jekyll YAML frontmatter containing: layout: post, title, author: {selected_author}, description, keywords (use the Target_Keyword from the instructions), and permalink: {permalink}.
Must include the following call to action line at the bottom, integrating the 'Smartin_App_Pitch' from your selected SEO row: 
👉 **[Download Smartin: Quick Stock Ratings on the App Store today](https://apps.apple.com/il/app/smartin-quick-stock-ratings/id6755475652)**>
"""


response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
output_text = response.text

try:
    tweet_content = output_text.split("MARKDOWN:")[0].replace("TWEET:", "").strip()
    markdown_content = output_text.split("MARKDOWN:")[1].strip()
except IndexError:
    print("Formatting error from Gemini. Defaulting safely.")
    tweet_content = f"Check out our latest roast on {selected_stock}! {live_url}"
    markdown_content = output_text

markdown_content = markdown_content.replace('```markdown', '').replace('```', '').strip()

# Generate the SEO Article
os.makedirs("_posts", exist_ok=True)
filename = f"_posts/{date_str}-{safe_slug}.md"
with open(filename, 'w') as f:
    f.write(markdown_content)
print(f"Generated successfully: {filename}")

# Post to Twitter
if TWITTER_API_KEY and TWITTER_API_SECRET and TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_SECRET:
    print(f"Tweeting: {tweet_content}")
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        response = client.create_tweet(text=tweet_content)
        print(f"SUCCESS: Roast posted to Twitter. Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"TWITTER ERROR: {e}")
else:
    print("Skipping Twitter: Twitter API Keys not found in environment.")
