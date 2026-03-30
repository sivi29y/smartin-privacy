# SMARTIN BLOG GENERATION INSTRUCTIONS

This document contains the primary rules and data for all automated blog content (Daily Roasts, Market Forecasts, Weekly Summaries).

## 1. SEO Keyword Mapping
Gemini: Select the **most relevant** row from the table below based on the stock or market topic you are currently writing about. Use the "Target_Keyword" in your frontmatter and text, and integrate the "Smartin_App_Pitch" as a core part of the article's conclusion.

| Target_Keyword | Intent_Level | Actual_User_Question | Blog_Post_Topic | Smartin_App_Pitch |
| :--- | :--- | :--- | :--- | :--- |
| "how to find tenbagger stocks" | High - Strategy | What metrics actually point to a 10x return? | The Anatomy of a Peter Lynch Tenbagger | Use Smartin to instantly filter out companies that fail the basic tenbagger math. |
| "good peg ratio for tech stocks" | High - Metric | Is a PEG of 1.5 okay for a tech company? | Why the PEG Ratio is the Ultimate Tech Stock Reality Check | Don't crunch the numbers manually. Smartin gives you a clear rating on valuation instantly. |
| "peter lynch buy what you know" | Medium - Educational | Does investing in products I like actually work? | The 'Buy What You Know' Trap: Why You Still Need the Balance Sheet | You found a cool brand. Now run the ticker through Smartin to see if the stock is actually a buy. |
| "fundamental stock screener app" | High - Commercial | What is the best app to quickly check stock fundamentals? | Why Desktop Stock Screeners are Overkill for Most Investors | Smartin is built for speed: fundamental analysis and clear ratings right in your pocket. |
| "what is a good debt to equity ratio" | Medium - Metric | How much corporate debt is a dealbreaker? | Peter Lynch's Warning on Debt: How to Spot a Sinking Ship | Smartin's algorithm flags dangerous debt levels automatically before you hit the buy button. |
| "growth at a reasonable price stocks" | Medium - Strategy | How do I balance growth with value? | GARP Investing: The Sweet Spot Between Value and Tech Bubbles | Smartin's rating system is essentially an automated GARP engine. |
| "fun stock market app" | High - Commercial | Are there finance apps that aren't dry and boring? | The Rise of Fintainment: Why Finance Doesn't Have to be Dry | Switch on Smartin's Empire State Theme and make analyzing stocks actually entertaining. |

## 2. Overnight Sentiment (Global Pulse)
When writing **Market Forecasts** or **Weekly Summaries**, always check the "Global Context" provided in the data feed (Australia, Israel, Europe).
*   **Significance Threshold**: Focus on the US-impact of global markets **only** when they show significant movement (e.g., +/- 0.5% or more). 
*   **Mandate**: If global markets are stable, do not mention them. Only use them as a "driving force" or "major outlier" to adjust the persona's anxiety/pessimism for the US session.

## 2. Heading Hierarchy (The Golden Rule)
Search engines read a page like an outline. Never skip levels.

*   **H2 (Chapters)**: Use for main section breaks. These must be punchy, narrative-driven declarations (e.g., "The Inflation Monster vs. Your Wallet" not "Market Outlook").
*   **H3 (Supporting Evidence)**: Use for sub-points under an H2. If a section under an H2 goes longer than 300 words or contains multiple steps/metrics, break it down with H3s.

**Mandate**: Never use an H3 unless it is nested directly under an H2. 

## 3. Internal Linking Rules
Every post must keep the website connected to avoid "orphan pages."

*   **1-3 Internal Links**: Include at least one and up to three internal links per post.
*   **Targets**:
    *   [The Hitchhiker's Guide to Peter Lynch Investing](/guide/)
    *   [Latest Fintainment Roasts](/blog/)
    *   Any relevant specific guide volume (e.g., [/guide/the-peg-ratio/](/guide/the-peg-ratio/))
