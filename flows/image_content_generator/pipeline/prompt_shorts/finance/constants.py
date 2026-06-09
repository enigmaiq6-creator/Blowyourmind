IDEA_PROMPT_FINANCE = """
You are the Lead Producer for "BlowYourMind", a viral channel about mind-blowing secrets, hidden truths, and financial education.

Generate a HIGH-RETENTION video idea exposing a financial secret, tax trap, banking trick, or economic curiosity that directly impacts the viewer's wallet.

The topic must focus on a hidden financial mechanism, double taxation, sneaky banking rules, or wealth-building tricks.

Examples of the vibe:
- "The 6 worst taxes quietly draining your wallet right now."
- "How banks use fractional reserve banking to create money out of thin air."
- "The subscription trap: how companies make you pay for things you never use."
- "Fiscal Drag: the silent tax increase that governments don't want you to know about."
- "The compound interest trap: how credit card companies keep you in debt forever."

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title (e.g., "The Silent Wealth Killer: How Fiscal Drag Taxes Your Hard Work").
- `hook`: A scroll-stopping hook (10-15 words) that addresses the viewer directly (e.g., "The system is quietly stealing your money, and you're letting it happen.").
- `intrigue_header`: A punchy 2-4 word phrase in ALL CAPS for the top banner (e.g., "DIRTY TAX TRAPS", "MONEY SECRETS").
- `personal_impact`: A single sentence explaining how this connects to the viewer's life (e.g., "This hidden rule is slowly eroding your savings, and it will only get worse.").
- `key_data_stat`: A specific mind-blowing stat with units (e.g., "60% effective tax", "$8.4 Billion collected", "30-year debt cycle").
- `caption`: A viral social media caption with 5-8 hashtags like #FinanceSecrets #MoneyTips #BlowYourMind #SmartMoney #TaxHacks.
- `category`: Must be "finance"
"""

AUDIO_PROMPT_FINANCE = """
Use a confident, shocking, and revealing tone — like you are exposing a massive hidden system or a secret trap that the viewer is stuck in.
Speak clearly, with punchy emphasis on key data points.

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_FINANCE = """
You are the Video Producer for "BlowYourMind" and you're writing a script for a vertical short video (1080x1920) about a financial secret, tax trap, or money mechanics.

The format is a rapid-fire listicle/ranking or step-by-step breakdown (6-8 scenes) following an avatar character (we'll call him "Jack", a hard-working average guy) to make the dry financial concept visual, humorous, and highly relatable.

**VISUAL STYLE (MANDATORY & CONSISTENT):**
Use a flat 2D vector cartoon style with clean lines, solid color backgrounds, and a consistent cartoon character named Jack (who wears a green sweater and looks tired or confused) to illustrate each financial struggle.
Example style prompt to include in images: `"Flat 2D vector cartoon illustration, bold outlines, simple geometric shapes, clean minimal style, featuring a cartoon worker named Jack in a green sweater..."`

**STRUCTURE (6-8 scenes):**
1. **Scene 1 - The Hook & Introduction [0-8s]**: (list_number=0). Introduce the topic and Jack. Show Jack working hard but the system quietly draining his wallet.
2. **Scenes 2-6 - The Breakdown [8-48s]**: (list_number=1 to N). Rank the worst points (like 5 down to 1) or break down the steps. Show Jack suffering under each point with clear visual graphics/diagrams.
3. **Scene 7 - The Personal Impact [48-55s]**: Show how this adds up and affects Jack's future.
4. **Scene 8 - The CTA / Outro [55-60s]**: End with a mind-blowing question to Jack and the viewer, prompting comments.

**PER-SCENE FIELDS:**
- `scene_number`: Sequential number (1 to 8)
- `list_number`: 0 for intro, 1 to N for the list items.
- `scene_title`: A short ALL CAPS title for the list item/concept (e.g., "FISCAL DRAG", "DOUBLE TAXATION").
- `visual_type`: Use "ai_image" for these cartoon scenes.
- `image_prompt`: Description of the scene in ENGLISH using the mandatory cartoon style. Describe what Jack is doing, his expression, and any diagrammatic elements (e.g. arrows, giant stamps, money bags, funnels) in the scene.
- `pexels_query`: (Leave empty, we will use "ai_image" for everything in this mode).
- `narration`: Spoken narration in ENGLISH. Keep it punchy, simple, and shocking. MAX 150 words total for the whole script.

**CRITICAL:**
1. ALL text and narration must be in ENGLISH.
2. The image prompts must strictly describe a flat 2D cartoon illustration with Jack the character so the images generated look consistent and custom-made.
"""

FOCUS_AREAS_FINANCE = [
    "THE DEBT SNOWBALL TRICK: How the psychological debt snowball method beats the debt avalanche mathematically due to human behavior.",
    "DYNAMIC PRICING SECRETS: How hotels and airlines use cookies, browsing history, and hidden resort fees to inflate costs dynamically.",
    "THE COFFEE TRAP: How small daily micro-purchases ($5/day) cost you over $100,000 in retirement savings due to lost compound growth.",
    "TREASURY BILL SECRETS: How wealthy individuals protect their cash from bank failures and earn tax-free local interest.",
    "LIFESTYLE CREEP: The silent wealth killer where every salary raise is immediately offset by buying a better car or house, keeping you broke.",
    "THE 4% RULE: How the Trinity Study proved you can live off your investments forever if you only withdraw 4% annually.",
    "INSURANCE DEDUCTIBLE LOOPS: How insurance companies use deductibles, fine print, and loyalty penalties to charge long-term customers more.",
    "THE INDEX FUND REVOLUTION: Why 90% of professional hedge fund managers fail to beat a simple S&P 500 index fund over 15 years.",
    "TAX-LOSS HARVESTING: The secret strategy used by the ultra-rich to offset their investment gains by selling losing assets at the end of the year.",
    "FIAT MONEY SECRETS: How the end of the Gold Standard in 1971 completely decoupled wages from productivity and inflated asset prices.",
]
