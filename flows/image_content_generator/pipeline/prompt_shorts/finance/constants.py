"""
Constants and Prompts for BlowYourMind - Viral Finance, Wealth & Economic Mysteries.
Dynamic Multi-Style & Anti-Repetition Engine.
"""

VISUAL_STYLES = [
    {
        "name": "Cinematic Photorealism",
        "suffix": ", hyper-realistic 8K cinematic shot, 35mm film photography, dramatic atmospheric volumetric lighting, high dynamic range, award-winning documentary aesthetics."
    },
    {
        "name": "Dark Investigative Noir",
        "suffix": ", dark moody cinematic atmosphere, high contrast chiaroscuro lighting, sharp focal details, intense dramatic shadows, investigative documentary film still."
    },
    {
        "name": "Epic Baroque & Renaissance Oil",
        "suffix": ", dramatic oil on canvas painting, rich golden tones, Caravaggio style lighting, epic historical realism, intricate textured details, masterpiece art."
    },
    {
        "name": "Vintage 1970s Kodachrome Archival",
        "suffix": ", authentic 1960s-1970s vintage colorized film photograph, retro Kodachrome grain, realistic historical archive style, warm tones."
    },
    {
        "name": "3D Isometric Miniature Diorama",
        "suffix": ", tactile high-detail miniature 3D diorama, tilt-shift macro lens, soft volumetric studio lighting, photorealistic claymation stop-motion look."
    },
    {
        "name": "Cyberpunk High-Tech Dataviz",
        "suffix": ", sleek 3D octane render, neon holographic blueprints, glowing high-tech digital currency elements, futuristic cinematic aesthetics."
    },
    {
        "name": "Layered 3D Paper Sculpture",
        "suffix": ", intricate 3D layered papercraft art, architectural paper sculpture, depth shadows, textured craft paper, warm ambient studio glow."
    }
]

IDEA_PROMPT_FINANCE = """
You are the Creative Producer for "BlowYourMind: Money & Power" — specializing in viral, mind-bending stories about wealth, insane financial events, legendary scams, currency paradoxes, and economic history.
Your task is to generate a fascinating, true financial story that has viral potential.

**VIDEO STRUCTURE (4-5 SCENES, 35-50 SECONDS TOTAL):**
1. **Scene 1 (Hook)**: Intense, curiosity-sparking opening that hooks the viewer instantly.
2. **Scene 2 (Context)**: The historical background or the bizarre setup.
3. **Scene 3 (Climax/Twist)**: The mind-blowing financial turning point, massive impact, or shocking scale.
4. **Scene 4+ (Conclusion)**: The aftermath, modern consequence, or philosophical takeaway.

**VIRAL RULES:**
- The story must be TRUE, HISTORICALLY ACCURATE, and SHOCKING.
- Avoid generic banking lectures; focus on human drama, crazy wealth disparities, insane hyperinflation, unbelievable heists, or economic paradoxes.
- Visual Variety: Describe realistic, tangible objects, historical figures, epic architectural vaults, cityscapes, or dramatic environments.
- DO NOT force any fixed mascot or character. Tailor the scene purely to the historical narrative.

**CRITICAL SPELLING RULE:** All generated English text MUST have PERFECT spelling and grammar.

**MANDATORY FIELDS (ALL IN ENGLISH):**
- `tema`: Theme category: 'finance', 'history', 'economics', 'scams', or 'banking'.
- `title`: Short punchy title (e.g. "The $100 Billion Loaf of Bread").
- `hook`: Scroll-stopping opening phrase (10-15 words).
- `key_takeaway`: One-line summary of the lesson or fascinating fact.
- `caption`: Viral caption in English with 5-8 hashtags (include #BlowYourMind #MoneyMysteries #History #Finance #MindBlowing).
- `category`: "finance"
"""

SCRIPT_PROMPT_FINANCE = """
You are the Master Video Director for "BlowYourMind".
Based on the IDEA, write the complete technical production script.

**EXACT STRUCTURE — 4 to 5 SCENES (35-50 seconds total):**
- **Scene 1**: Hook & Shocking Fact.
- **Scene 2**: The Bizarre Setup & Historical Context.
- **Scene 3**: The Escalation or Main Shocking Event.
- **Scene 4+**: The Climax, Collapse or Lasting Legacy.

**VISUAL PROMPT RULES:**
- For `image_prompt`: Describe rich, immersive scenes that visually illustrate that specific moment in the narration.
- {visual_style_instruction}

**MANDATORY TECHNICAL FIELDS:**
- `scenes`: Array of 4-5 scenes, each with:
  - `scene_number`: 1, 2, 3, 4, etc.
  - `narration`: English narration for this scene (engaging, dramatic pacing).
  - `image_prompt`: Full Midjourney/Vertex style prompt to generate the scene. Must include the visual style instructions!
- `whisper_payload`: Full concatenated narration text.

**CRITICAL:**
- ALL content must be in ENGLISH with PERFECT spelling and grammar.
- Fast-paced, mysterious, and highly captivating narration.
"""

AUDIO_PROMPT_FINANCE = """
Use a dynamic, fast-paced, and curious narrative tone — like an educational mini-documentary on YouTube Shorts / Netflix documentary.
The voice should sound enthusiastic, professional, and dramatic.

TEXT TO NARRATE:
{audio_text}
"""

FOCUS_AREAS_FINANCE = [
    "The 100-Trillion Dollar Zimbabwe Banknote and Extreme Hyperinflation",
    "Operation Bernhard: The Secret Nazi Counterfeiting Plot Inside Sachsenhausen",
    "Mansa Musa: The African King Who Collapsed Cairo's Economy With Free Gold",
    "The Great Salad Oil Swindle: $175 Million in Sea Water and Ghost Tanks",
    "Victor Lustig: The Con Artist Who Sold the Eiffel Tower Twice",
    "The $1 Billion McDonald's Monopoly Fraud Engineered by 'Uncle Jerry'",
    "The Hunt Brothers Attempt to Corner the Global Silver Market in 1980",
    "The Nickel Short Squeeze That Paralyzed the London Metal Exchange",
    "Weimar Republic 1923: When Burning German Marks Was Cheaper Than Firewood",
    "Ivar Kreuger: The Match King and His Sovereign Debt Ponzi Empire",
    "The $6 Billion Bre-X Fake Indonesian Gold Mine Scandal",
    "The South Sea Bubble That Bankrupted Sir Isaac Newton",
    "Roberto Calvi and God's Banker: The Mysterious Vatican Bank Collapse",
    "The Secret 8,000-Tonne Gold Stash Deep Inside the New York Federal Reserve Vault",
    "How Double-Entry Bookkeeping in Venice Created Modern Capitalism",
    "John Law and the Mississippi Company: The First Stock Market Mania",
    "The Giant 4-Ton Stone Disks of Yap Island Currency",
    "The Trillion-Dollar Platinum Coin Legal Loophole",
    "The 2010 Flash Crash: How One London Suburban Trader Shook Wall Street",
    "The Banco Central Fortaleza Tunnel Heist: Stealing $70 Million Undetected",
    "The 10,000 Bitcoin Pizza: The $600 Million Papa John's Order",
    "Tulip Mania 1637: When a Single Bulb Purchased an Amsterdam Canal House",
    "Scotland's Darien Disaster: The Tropical Colony Scheme That Bankrupted a Nation",
    "The London Whale: How JPMorgan Lost $6.2 Billion on a Single Derivative Desk",
    "The De Beers Monopoly: How Diamonds Were Marketed as Rare and Forever",
    "Black Wednesday 1992: How George Soros Broke the Bank of England",
    "Barings Bank Demise: Nick Leeson's Infamous 88888 Hidden Error Account",
    "Gregor MacGregor's Phantom Republic of Poyais: Selling Deeds to a Jungle",
    "The Great San Francisco Diamond Hoax of 1872",
    "The 1970 Irish Bank Strike: When Pubs Became the Nation's Financial Clearinghouses",
    "The Coinage Act of 1873: The Crime of the Century That Demonetized Silver",
    "Secret Swiss Alpine Bunkers: Gold Vaults Carved Inside Mountain Granite",
    "The Mexican Desert Aluminum Cache: The Secret Chinese Smuggling Stockpile",
    "Parmalat's $14 Billion Fraud: The Forged Bank of America Confirmation Letter",
    "Billie Sol Estes: The Texas Tycoon Who Financed Empires on Phantom Fertilizer Tanks",
    "Enron Special Purpose Entities: How Chewco and Raptor Hid Billions in Debt",
    "Siberian Fur Currency: When Squirrel and Marten Pelts Built Russian Empires",
    "The 1720 Bubble Act: Crazy Enterprises for Extracting Silver from Lead",
    "The 1978 Lufthansa Heist at JFK: $6 Million Stolen in the Dead of Night",
    "The French Assignats Collapse: Revolutionary Currency Printed to Dust",
    "The Golden Age of Pirates: The Real Value of 17th Century Spanish Doubloons",
    "The 1933 Executive Order 6102: When the US Government Confiscated Private Gold",
    "The 1987 Black Monday: When Program Trading Crashed 22% in 6 Hours",
    "The Dutch East India Company (VOC): The $8 Trillion Mega-Corporation of History"
]
