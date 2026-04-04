# Email Templates for the Smartin Drip Sequence
# Keys correspond to the 'drip_step' value (0 through 6)

WELCOME_SERIES = {
    0: {
        "days_delay": 0, # Send immediately upon confirmation (Day 0)
        "subject": "Quick question before you get your first Roast...",
        "body": """
Hello!

Thanks so much for joining the Smartin family. 

Before we send you your first deeply satisfying stock roast, I have a quick favor to ask:

Could you just reply with a quick "Got it!" or a "Hello" to this email? 

This tells the email gods that you actually want to hear from us, ensuring our weekly stock roasts don't end up lost in your spam folder next to the fake lottery winnings.

Stay Smart,
The Smartin Team
        """
    },
    1: {
        "days_delay": 7, # Send 7 days after confirmation
        "subject": "Welcome to Fintainment (and why we built Smartin)",
        "body": """
Welcome to the Smartin family!

We created Smartin because modern finance has turned into either boring, unreadable charts or incredibly bad TikTok advice. There wasn't a middle ground. 

So we built one. We call it "Fintainment." 

Every week, we'll deliver fundamental, undeniable stock analysis. We'll tell you if a stock is a fortress or a house of cards—and we'll do it by roasting the bad ones without mercy.

See you in the market,
The Smartin Team
        """
    },
    2: {
        "days_delay": 14,
        "subject": "The Philosophy: What the heck is GARP?",
        "body": """
Hello again!

Let's talk about the secret sauce behind the Smartin algorithm: GARP (Growth At A Reasonable Price).

It’s exactly what it sounds like. We want companies that are growing fast, but we refuse to overpay for them. It’s the philosophy pioneered by legends like Peter Lynch.

Our Modernized Peter Lynch Algorithm chews through the fundamentals to score stocks based on their PEG ratio and debt load. No moving averages. No astrology. Just pure, unadulterated math.

Stay Smart,
The Smartin Team
        """
    },
    3: {
        "days_delay": 21,
        "subject": "A sneak peek under the hood at Smartin...",
        "body": """
Ever wonder what thousands of rows of financial data looks like when organized for a normal human?

Here’s a sneak peek at the Smartin App interface.

Our Basic tier gives you the immediate, bottom-line verdict: buy, hold, or run away. 
Our upcoming Pro tier will let you dive deeper into the specific Peter Lynch metrics that drove the decision. 

We can't wait to get this in your hands.

Stay Smart,
The Smartin Team
        """
    },
    4: {
        "days_delay": 28,
        "subject": "Mini Guide to Peter Lynch (Part 1)",
        "body": """
Have you ever heard the phrase "Invest in what you know"?

That's classic Peter Lynch. In Chapter 1 of our Hitchhiker's Guide to Peter Lynch, we break down why sticking to your specific "circle of competence" is the ultimate alpha. 

If you are a doctor, you spot medical tech trends years before Wall Street does. Use your unfair advantage.

Read the full chapter here: https://smartinthe.app/guide/invest-in-what-you-know

Stay Smart,
The Smartin Team
        """
    },
    5: {
        "days_delay": 35,
        "subject": "Mini Guide to Peter Lynch (Part 2)",
        "body": """
We need to talk about Diworseification. 

Yes, Di-worse-ification. It's what happens when a great company decides they can also build smartphones, cars, and stream movies—and they fail at all of them, tanking the stock.

In Chapter 2, we teach you how to spot a company that's straying too far from its core competency before the stock plummets.

Read the full breakdown: https://smartinthe.app/guide/the-diworseification-trap

Stay Smart,
The Smartin Team
        """
    },
    6: {
        "days_delay": 42,
        "subject": "Mini Guide to Peter Lynch (Part 3)",
        "body": """
The elusive "Tenbagger."

A stock that returns 10x your original investment. In Chapter 3 of our guide, we explore the math behind the Tenbagger. Hint: It almost never comes from massive dividend yields. It comes from small, under-the-radar companies with incredibly fast earnings growth.

Here is how you spot them before Wall Street catches on:
https://smartinthe.app/guide/tenbaggers

Stay Smart,
The Smartin Team
        """
    }
}
