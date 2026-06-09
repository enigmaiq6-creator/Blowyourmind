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

The format is a rapid-fire listicle/ranking or step-by-step breakdown (EXACTLY 6 scenes) following an avatar character (we'll call him "Jack", a hard-working average guy) to make the dry financial concept visual, humorous, and highly relatable.

**VISUAL STYLE (MANDATORY & CONSISTENT):**
Use a flat 2D vector cartoon style with clean lines and a consistent cartoon character named Jack (who wears a green sweater and looks tired or confused).

**COLOR PALETTE RULE (CRITICAL — makes each video visually unique):**
- Choose ONE dominant background color that fits the video's emotional tone (e.g., deep navy blue for "debt", burnt orange for "inflation", dark red for "tax traps", forest green for "investing", purple for "banking tricks").
- EVERY scene in this video must use the SAME dominant background color so the video has a cohesive visual identity.
- NEVER use generic white or grey backgrounds.
- State the color explicitly in every image_prompt (e.g., "solid deep navy blue background", "solid burnt orange background").

**TOPIC-SPECIFIC PROPS (CRITICAL — makes each video content unique):**
- Design props, objects, and diagrams that are 100% specific to THIS video's topic. For example:
  - "Debt Snowball" → actual cartoon snowballs rolling, debt labels (CREDIT CARD $5k, CAR $12k), snowball growing bigger
  - "Fiscal Drag" → salary bar chart rising, tax bracket lines moving left, invisible hand pulling coins
  - "Coffee Trap" → coffee cups stacking up, calculator, retirement piggy bank cracking
  - "4% Rule" → investment pie chart, withdrawal arrow, infinite loop symbol
- DO NOT reuse generic props (plain money bags, simple funnels) — make them SPECIFIC to this topic.

**STRUCTURE (EXACTLY 6 scenes):**
1. **Scene 1 - The Hook & Introduction [0-8s]**: (list_number=0). Introduce the topic and Jack. Show Jack working hard but the system quietly draining his wallet.
2. **Scenes 2-4 - The Breakdown [8-40s]**: (list_number=1 to 3). Break down the 3 most critical points or steps. Show Jack with topic-specific props and diagrams.
3. **Scene 5 - The Personal Impact [40-50s]**: Show the direct consequence on Jack's life using a topic-specific visual.
4. **Scene 6 - The CTA / Outro [50-60s]**: End with a mind-blowing question, show Jack looking shocked at a revealing chart or stat.

**PER-SCENE FIELDS:**
- `scene_number`: Sequential number (1 to 6)
- `list_number`: 0 for intro, 1 to 4 for the list items, 5 for outro.
- `scene_title`: A short ALL CAPS title for the list item/concept.
- `visual_type`: Use "ai_image" for all scenes.
- `image_prompt`: MUST follow this structure exactly:
  "Flat 2D vector cartoon illustration, bold outlines, simple geometric shapes, clean minimal style. [SPECIFIC TOPIC-RELATED ACTION Jack is doing]. [SPECIFIC PROP/DIAGRAM unique to this video topic — be very detailed]. Solid [COLOR NAME] background."
- `pexels_query`: Leave empty.
- `narration`: Spoken narration in ENGLISH. Punchy, shocking. MAX 130 words total for the whole script.

**CRITICAL RULES:**
1. ALL text and narration must be in ENGLISH.
2. Every image_prompt MUST include: (a) the flat 2D cartoon style, (b) Jack in green sweater, (c) a topic-specific prop or diagram described in detail, (d) the chosen background color stated explicitly.
3. Each scene must look visually DIFFERENT from the previous one (different action, different prop configuration, different diagram).
4. You MUST output EXACTLY 6 scenes. No more, no less.
"""


FOCUS_AREAS_FINANCE = [
    "THE MCDONALD'S REAL ESTATE TRICK: McDonald's doesn't make money from burgers; they are one of the world's largest real estate landlords, charging high rents to franchisees.",
    "THE G-WAGON TAX LOOPHOLE: The Section 179 tax deduction where business owners buy heavy SUVs (over 6,000 lbs) like a G-Wagon to write off 100% of the cost in year one.",
    "THE BUY BORROW DIE STRATEGY: How billionaires avoid income tax entirely by holding appreciating assets, taking low-interest loans against them, and passing them to heirs.",
    "DIRTY MONEY LAUNDERING SECRETS: The placement, layering, and integration process criminals use to wash cash, and how big banks quietly profit from compliance fees.",
    "THE RETAIL REVENUE TRAP: Why busy high-street shops making millions in revenue end up with £0 in profit due to soaring commercial rent, business rates, and inventory.",
    "THE TV LICENSE & COUNCIL TAX SCAM: How local UK taxes and license fees force citizens to pay for services they don't use under threat of heavy fines.",
    "THE STEPPED-UP BASIS LOOPHOLE: How heirs inherit properties and stocks at current market values, completely erasing decades of built-up capital gains taxes.",
    "CREDIT SCORE ALGORITHM SECRETS: How credit bureaus manipulate scores, why paying off your debt early can actually drop your score, and the piggyback credit trick.",
    "THE SILENT INFLATION TAX: How central banks printing money is a hidden tax that quietly steals 90% of your savings' buying power over decades.",
    "BANK BAIL-IN LAWS: The scary legal mechanisms allowing banks to seize customer deposits to save themselves during a financial crash instead of getting government bailouts.",
]

