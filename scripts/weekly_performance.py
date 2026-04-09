import os
import random
import time
from datetime import datetime
from google import genai
import yfinance as yf
import tweepy
import sys
# Ensure we can import from the current script's directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from personas import PERSONAS as ALL_PERSONAS

# Setup API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
model_id = 'gemini-3-flash-preview'

# ALL_PERSONAS are now imported from personas.py

def get_weekly_data():
    tickers = [
        "SPY", "QQQ", "DIA", "AAPL", "TSLA", "GME", "AMC", "PLTR", "SOFI", "NVDA", "AMD", "META", "GOOGL", 
        "AMZN", "NFLX", "MSFT", "INTC", "DJT", "HOOD", "COIN", "MARA", "RIOT", "BABA", 
        "NIO", "ROKU", "PTON", "ZM", "DOCU", "WISH", "CLOV", "WKHS", "BB", "NOK", 
        "SPCE", "MVIS", "SNDL", "TLRY", "CRSR", "DKNG", "PENN", "RBLX", "U", "SNOW", 
        "DDOG", "NET", "CRWD", "OKTA", "ZS", "PANW", "FTNT", "CHWY", "SQ", "PYPL",
        "IBM", "IONQ", "RGTI", "QBTS", "XOM", "CVX", "OXY", "GOLD", "NEM", "AEM",
        "CLSK", "MU", "RDDT", "MSTR", "LULU", "DNUT", "PBR", "WING", "NYCB", "BLK",
        "BX", "VTI"
    ]
    global_indices = {
        "ASX 200 (Australia)": "^AXJO",
        "TA-35 (Israel)": "TA35.TA",
        "Euro Stoxx 50 (Europe)": "^STOXX50E"
    }
    
    data = {"us_market": {}, "global_context": {}}
    
    # Fetch US Market Data
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                data["us_market"][ticker] = {
                    "price": round(end_price, 2),
                    "change": round(change_pct, 2)
                }
            else:
                data["us_market"][ticker] = {"price": "N/A", "change": "0.00"}
        except Exception:
            data["us_market"][ticker] = {"price": "N/A", "change": "0.00"}
            
    # Fetch Global Context (Impact on US Markets)
    for name, ticker in global_indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                data["global_context"][name] = round(change_pct, 2)
            else:
                data["global_context"][name] = 0.00
        except Exception:
            data["global_context"][name] = 0.00
            
    return data

def select_persona_dynamic():
    selected = random.choice(["george", "cosmo"])
    description = f"A decisive monologue by {ALL_PERSONAS[selected]}. This is not a dialogue. It is a data-driven analysis in their unique voice."
    return description, selected

weekly_data = get_weekly_data()
data_summary = "\n".join([f"{ticker}: {info['price']} ({info['change']}%)" for ticker, info in weekly_data["us_market"].items()])
persona_desc, persona_slug = select_persona_dynamic()
selected_author = ALL_PERSONAS[persona_slug].split(" - ")[0]

# Load Centralized Instructions
instructions_path = os.path.join(os.path.dirname(__file__), "blog_instructions.md")
with open(instructions_path, 'r') as f:
    blog_instructions = f.read()

date_str = datetime.now().strftime('%Y-%m-%d')
safe_slug = "weekly-summary"
permalink = f"/blog/{date_str}/{safe_slug}/"
live_url = f"https://smartinthe.app{permalink}"

# Significance Filtering (Context only)
SIGNIFICANCE_THRESHOLD = 0.5
significant_global = {name: change for name, change in weekly_data["global_context"].items() if abs(change) >= SIGNIFICANCE_THRESHOLD}

global_context_str = ""
if significant_global:
    global_context_data = "\n".join([f"{name}: {change}%" for name, change in significant_global.items()])
    global_context_str = f"""
GLOBAL CONTEXT (Significant Overnight Moves):
{global_context_data}

IMPORTANT: Use the Global Context above to set the 'Market Vibe.' For example, if Australia and Europe were down significantly, the persona should start with a more pessimistic/neurotic tone about the US market opening.
DO NOT directly analyze or list the global tickers in the blog post—keep the primary focus 100% on the US market and the Smartin roasts.
"""
else:
    global_context_str = "\nGLOBAL CONTEXT: Global markets (Australia, Israel, Europe) were relatively stable last week. Focus your analysis purely on US internal metrics and the Smartin roasts."

prompt = f"""
110: Write a highly entertaining, 'Fintainment' blog post called a 'Weekly Market Performance Summary' for the iOS app 'Smartin: Quick Stock Ratings'.
111: This post MUST be a **joy to read**—priority one is the character's voice and comedic energy. 
112: However, it must also provide a DECISIVE, DATA-DRIVEN ANALYSIS of the week's market performance based on valid Peter Lynch fundamental principles (e.g. PEG, P/E, Debt) using this primary US data:
113: {data_summary}
114: 
115: IMPORTANT: Keep the SEO natural. Use exactly **1 or 2 terms** from our Target_Keyword list as an **EXACT STRING MATCH** in the text. The post should never feel like 'marketing text'.
{global_context_str}

Use this precise comedic persona:
{persona_desc}

{blog_instructions}

MARKDOWN FORMAT RULES:
1. Write a DECISIVE MONOLOGUE. Do not write a script or dialogue.
2. Focus on ACTUAL DATA. Mention the specific prices and % changes provided.
3. Be OPINIONATED. The persona should have a clear, over-the-top take on what the numbers mean for the week.
4. NO MEANINGLESS BLURB. Every paragraph must relate to the market numbers or the economic context.

138: Format your absolute output exactly as follows:
139: TWEET:
140: <Write a punchy, 1-2 sentence hook for Twitter natives in the persona's voice. Include $SPY and end with: "Weekly Summary: {live_url}">
141: <CRITICAL COPYRIGHT RULE: NO REAL NAMES OR CATCHPHRASES.>
142: 
143: MARKDOWN:
144: ---
145: layout: post
146: title: <Title here (MUST NOT use 'Kramer' or 'George')>
147: author: {selected_author}
148: description: <140-160 character SEO summary for the blog index>
149: keywords: <Target_Keywords here>
150: permalink: {permalink}
151: ---
152: <Full SEO markdown blog post here, starting with a Header as per the Golden Rule.>
153: 👉 **[Download Smartin: Quick Stock Ratings on the App Store today](https://apps.apple.com/il/app/smartin-quick-stock-ratings/id6755475652)**
"""

# Generate Content with Retry Logic
output_text = ""
max_retries = 3
for attempt in range(max_retries):
    try:
        response = ai_client.models.generate_content(model=model_id, contents=prompt)
        output_text = response.text
        break
    except Exception as e:
        print(f"AI ERROR (Attempt {attempt+1}/{max_retries}): {e}")
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 5
            print(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            print("MAX RETRIES REACHED. Defaulting safely.")
            output_text = "TWEET: Weekly summary is here! $SPY MARKDOWN: AI safety blocked this summary or server overloaded. Stay tuned for the next one."

try:
    tweet_content = output_text.split("MARKDOWN:")[0].replace("TWEET:", "").strip()
    # Ensure the front matter starts at the absolute top by stripping all leading whitespace
    markdown_content = output_text.split("MARKDOWN:")[1].lstrip()
except IndexError:
    tweet_content = f"Fresh roast incoming! Check it out: {live_url}"
    markdown_content = output_text.strip()

import re
markdown_content = re.sub(r'^yaml\n', '', markdown_content, flags=re.MULTILINE | re.IGNORECASE)
markdown_content = re.sub(r'^markdown\n', '', markdown_content, flags=re.MULTILINE | re.IGNORECASE)
markdown_content = markdown_content.replace('```markdown', '').replace('```yaml', '').replace('```', '').strip()

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
