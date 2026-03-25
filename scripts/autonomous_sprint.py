import os
import random
from datetime import datetime
import google.generativeai as genai

# Setup Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 5 Fintainment Personas
PERSONAS = [
    "Kurt Vonnegut (writing for SNL) - Darkly satirical, pointing out absurd corporate greed",
    "Jerry Seinfeld - Observational comedy, confused by the ridiculous minutiae of financial jargon",
    "George Costanza - Neurotic, panicked about losing money, doing the opposite of rational instincts",
    "Cosmo Kramer - Frantic, erratic, wild conspiracy theories about the stock",
    "Elaine Benes - Aggressively confident, tearing down 'bro' stocks with sharp insults"
]

# 50 Retail/Meme/Tech Stocks
STOCKS = [
    "AAPL", "TSLA", "GME", "AMC", "PLTR", "SOFI", "NVDA", "AMD", "META", "GOOGL", 
    "AMZN", "NFLX", "MSFT", "INTC", "DJT", "HOOD", "COIN", "MARA", "RIOT", "BABA", 
    "NIO", "ROKU", "PTON", "ZM", "DOCU", "WISH", "CLOV", "WKHS", "BB", "NOK", 
    "SPCE", "MVIS", "SNDL", "TLRY", "CRSR", "DKNG", "PENN", "RBLX", "U", "SNOW", 
    "DDOG", "NET", "CRWD", "OKTA", "ZS", "PANW", "FTNT", "CHWY", "SQ", "PYPL"
]

def get_used_history():
    """Reads the _posts directory to prevent repeating the same stock or persona."""
    used_stocks = set()
    used_personas = set()
    
    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        return used_stocks, used_personas
        
    for filename in os.listdir(posts_dir):
        if not filename.endswith(".md"): continue
        
        with open(os.path.join(posts_dir, filename), 'r') as f:
            content = f.read().lower()
            # Scan for used stocks
            for stock in STOCKS:
                if f"({stock.lower()})" in content or f" {stock.lower()} " in content:
                    used_stocks.add(stock)
            
            # Scan for used personas (George, Elaine, etc.)
            for p in ["vonnegut", "seinfeld", "costanza", "kramer", "elaine"]:
                if p in content:
                    used_personas.add(p)
                    
    return used_stocks, used_personas

used_stocks, used_personas = get_used_history()

# Filter available to strictly prevent loops
available_stocks = [s for s in STOCKS if s not in used_stocks]
if len(available_stocks) < 5:
    available_stocks = STOCKS # Reset cycle if we've exhausted everything
    
available_personas = [p for p in PERSONAS if p.split()[0].lower() not in " ".join(used_personas).lower()]
if not available_personas:
    available_personas = PERSONAS # Reset cycle

# Select random combination of unused variables
selected_stock = random.choice(available_stocks)
selected_persona = random.choice(available_personas)
short_persona_name = selected_persona.split()[0].lower()

print(f"Targeting Stock: {selected_stock}")
print(f"Selected Persona: {selected_persona}")

date_str = datetime.now().strftime('%Y-%m-%d')
safe_slug = f"{selected_stock.lower()}-roast-{short_persona_name}"
permalink = f"/blog/{safe_slug}/"

prompt = f"""
Write a highly entertaining, SEO-optimized blog post for the iOS app 'Smartin: Quick Stock Ratings'.
The post must roast the stock {selected_stock} using this precise comedic persona:
{selected_persona}

Rules:
1. Briefly explain what {selected_stock} does, but immediately pivot to roasting its valuation (P/E ratio, PEG ratio) in the character's unique voice. Be funny, cynical, and authoritative.
2. The ultimate goal is converting the reader. You MUST include this exact line as a call to action at the bottom of the article:
👉 **[Download Smartin: Quick Stock Ratings on the App Store today](https://apps.apple.com/il/app/smartin-quick-stock-ratings/id6755475652)**
3. The response MUST be ONLY valid Markdown with YAML frontmatter. Do not include any block backticks (```markdown) around your output.
4. The frontmatter MUST ONLY include: layout: post, title, description, keywords, and permalink: {permalink}
5. The keywords must include the stock ticker, the persona name, and "AI stock analysis app".
6. The title should be incredibly catchy, funny, and include the ticker.
"""

response = model.generate_content(prompt)
markdown_content = response.text.replace('```markdown', '').replace('```', '').strip()

# Create directory if it doesn't exist
os.makedirs("_posts", exist_ok=True)

# Save the file
filename = f"_posts/{date_str}-{safe_slug}.md"
with open(filename, 'w') as f:
    f.write(markdown_content)

print(f"Generated successfully: {filename}")
