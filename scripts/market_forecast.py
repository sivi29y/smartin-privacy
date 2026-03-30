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

# 5 Fintainment Personas
ALL_PERSONAS = {
    "costanza": "George Costanza - Neurotic, panicked about losing money, doing the opposite of rational instincts. DO NOT use his name in the output.",
    "kramer": "Cosmo Kramer - Frantic, erratic, wild conspiracy theories about the stock. DO NOT use his name or catchphrases in the output."
}

def get_market_data():
    indices = ["SPY", "QQQ", "DIA"]
    stocks = ["AAPL", "TSLA", "NVDA"]
    global_indices = {
        "ASX 200 (Australia)": "^AXJO",
        "TA-35 (Israel)": "TA35.TA",
        "Euro Stoxx 50 (Europe)": "^STOXX50E"
    }
    
    data = {"us_market": {}, "global_context": {}}
    
    # Fetch US Market Data
    for ticker in indices + stocks:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_price = hist['Close'].iloc[-1]
                change_pct = ((curr_price - prev_close) / prev_close) * 100
                data["us_market"][ticker] = {
                    "price": round(curr_price, 2),
                    "change": round(change_pct, 2)
                }
            else:
                data["us_market"][ticker] = {"price": "N/A", "change": "N/A"}
        except Exception:
            data["us_market"][ticker] = {"price": "N/A", "change": "0.00"}
            
    # Fetch Global Context (Early Indicators)
    for name, ticker in global_indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_price = hist['Close'].iloc[-1]
                change_pct = ((curr_price - prev_close) / prev_close) * 100
                data["global_context"][name] = round(change_pct, 2)
            else:
                data["global_context"][name] = 0.00
        except Exception:
            data["global_context"][name] = 0.00
            
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
        description = f"A dialogue between {ALL_PERSONAS[selected[0]]} and {ALL_PERSONAS[selected[1]]}. They are arguing about the market."
    return description, "-".join(selected)

market_data = get_market_data()
persona_desc, persona_slug = select_persona_dynamic()
selected_author = persona_slug.split("-")[0].capitalize()

# Load Centralized Instructions
instructions_path = os.path.join(os.path.dirname(__file__), "blog_instructions.md")
with open(instructions_path, 'r') as f:
    blog_instructions = f.read()

date_str = datetime.now().strftime('%Y-%m-%d')

safe_slug = f"monday-forecast-{persona_slug}"
permalink = f"/blog/{safe_slug}/"
live_url = f"https://smartinthe.app{permalink}"

# Significance Filtering (Early Indicator context)
SIGNIFICANCE_THRESHOLD = 0.5
significant_global = {name: change for name, change in market_data["global_context"].items() if abs(change) >= SIGNIFICANCE_THRESHOLD}

global_context_str = ""
if significant_global:
    global_context_data = "\n".join([f"{name}: {change}%" for name, change in significant_global.items()])
    global_context_str = f"""
GLOBAL CONTEXT (Significant Overnight Moves):
{global_context_data}

IMPORTANT: Use the Global Context above to set the 'Overnight Sentiment.' While New York was sleeping, these markets already gave us the first clues.
If the Far East and Europe are red, the persona should be more anxious/neurotic about the US open.
DO NOT directly analyze or list the global tickers in the blog post—keep the primary focus 100% on the US market and upcoming week.
"""
else:
    global_context_str = "\nGLOBAL CONTEXT: Global markets (Australia, Israel, Europe) were relatively stable overnight. Focus your analysis purely on US internal metrics and the upcoming week's forecast."

prompt = f"""
Write a highly entertaining, SEO-optimized 'Monday Morning Market Forecast' for the iOS app 'Smartin: Quick Stock Ratings'.
The goal is to analyze the upcoming week's market vibe based on this primary US data:
{data_summary}
{global_context_str}

Use this precise comedic persona/dynamic:
{persona_desc}

{blog_instructions}

Format your absolute output exactly as follows:
TWEET:
<Write a punchy, 1-2 sentence hook for Twitter natively in the persona's voice. Include $SPY and end with: "Forecast: {live_url}">
<CRITICAL COPYRIGHT RULE: NO REAL NAMES OR CATCHPHRASES.>

MARKDOWN:
<Write the full SEO markdown blog post here.
Analyze the trends.
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
    tweet_content = f"Monday's forecast is looking wild. Check the roast: {live_url}"
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
