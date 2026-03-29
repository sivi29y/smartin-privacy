import os
import random
from datetime import datetime
import google.generativeai as genai
import yfinance as yf
import tweepy

# Setup API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Persona rotation
ALL_PERSONAS = {
    "costanza": "George Costanza - Neurotic, panicked about losing money, doing the opposite of rational instincts. DO NOT use his name in the output.",
    "kramer": "Cosmo Kramer - Frantic, erratic, wild conspiracy theories about the stock. DO NOT use his name or catchphrases in the output."
}

def get_weekly_data():
    tickers = ["SPY", "QQQ", "DIA", "AAPL", "TSLA", "NVDA"]
    data = {}
    
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                data[ticker] = {
                    "price": round(end_price, 2),
                    "change": round(change_pct, 2)
                }
            else:
                data[ticker] = {"price": "N/A", "change": "0.00"}
        except Exception:
            data[ticker] = {"price": "N/A", "change": "0.00"}
    return data

def select_persona_dynamic():
    options = [
        ("costanza",),
        ("kramer",),
        ("costanza", "kramer"),
        ("kramer", "costanza")
    ]
    selected = random.choice(options)
    description = ""
    if len(selected) == 1:
        description = ALL_PERSONAS[selected[0]]
    else:
        description = f"A dialogue between {ALL_PERSONAS[selected[0]]} and {ALL_PERSONAS[selected[1]]}. They are arguing about the week's performance."
    return description, "-".join(selected)

weekly_data = get_weekly_data()
persona_desc, persona_slug = select_persona_dynamic()
selected_author = persona_slug.split("-")[0].capitalize()

# Load Centralized Instructions
instructions_path = os.path.join(os.path.dirname(__file__), "blog_instructions.md")
with open(instructions_path, 'r') as f:
    blog_instructions = f.read()

date_str = datetime.now().strftime('%Y-%m-%d')

safe_slug = f"weekly-performance-{persona_slug}"
permalink = f"/blog/{safe_slug}/"
live_url = f"https://smartinthe.app{permalink}"

data_summary = "\n".join([f"{t}: ${d['price']} ({d['change']}%)" for t, d in weekly_data.items()])

prompt = f"""
Write a highly entertaining, SEO-optimized 'Weekly Performance Summary' for the iOS app 'Smartin: Quick Stock Ratings'.
Analyze the wins and losses of the week based on this data:
{data_summary}

Use this precise comedic persona/dynamic:
{persona_desc}

{blog_instructions}

Format your absolute output exactly as follows:
TWEET:
<Write a punchy, 1-2 sentence hook for Twitter natives in the persona's voice. Include $SPY and end with: "Weekly Summary: {live_url}">
<CRITICAL COPYRIGHT RULE: NO REAL NAMES OR CATCHPHRASES.>

MARKDOWN:
<Write the full SEO markdown blog post here.
Summarize the week.
Must follow the H2/H3 'Golden Rule' from the instructions.
Must include 1-3 internal links from the instruction targets.
Must start with Jekyll YAML frontmatter containing: layout: post, title, author: {selected_author}, description, keywords (use the Target_Keyword from the instructions), and permalink: {permalink}.
Must include the following call to action line at the bottom, integrating the 'Smartin_App_Pitch' from your selected SEO row: 
👉 **[Download Smartin: Quick Stock Ratings on the App Store today](https://apps.apple.com/il/app/smartin-quick-stock-ratings/id6755475652)**>
"""

response = model.generate_content(prompt)
output_text = response.text

try:
    tweet_content = output_text.split("MARKDOWN:")[0].replace("TWEET:", "").strip()
    markdown_content = output_text.split("MARKDOWN:")[1].strip()
except IndexError:
    tweet_content = f"The week is over, and we're roasted. Check the stats: {live_url}"
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
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        client.create_tweet(text=tweet_content)
        print("SUCCESS: Tweet posted.")
    except Exception as e:
        print(f"TWITTER ERROR: {e}")
else:
    print("Skipping Twitter: Keys missing.")
