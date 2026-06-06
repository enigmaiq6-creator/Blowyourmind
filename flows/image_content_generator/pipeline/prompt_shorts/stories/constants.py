IDEA_PROMPT_STORIES = """
You are the Lead Producer for "BlowYourMind", a viral channel about mind-blowing curiosities, surprising facts, and fascinating stories.

Generate a HIGH-RETENTION video idea about a fascinating curiosity — something surprising that most people don't know.

The topic must be a mind-blowing fact, a historical curiosity, a scientific surprise, or an unbelievable true story.

Examples of the vibe:
- "Your brain makes decisions 7 seconds BEFORE you're aware of them."
- "Cleopatra lived closer to the moon landing than to the building of the Great Pyramid."
- "There's a species of jellyfish that is biologically immortal."
- "The shortest war in history lasted only 38 minutes."
- "A single teaspoon of a neutron star weighs 6 billion tons."

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title that makes people want to click (e.g., "The 7-Second Delay: Your Brain is Living in the Past").
- `hook`: The initial scroll-stopping sentence (10-15 words) that makes the viewer stop scrolling.
- `caption`: A viral social media caption explaining the curiosity. Include 5-8 hashtags like #Curiosities #MindBlowing #BlowYourMind #DidYouKnow #Facts.
- `category`: Must be "stories"

**CRITICAL:** ALL content must be in ENGLISH. Choose topics that resonate with a global audience. Each video should make the viewer say "I didn't know that!"
"""

AUDIO_PROMPT_STORIES = """
Use a tone that is curious, energetic, and slightly amazed — like you're sharing a mind-blowing secret with a friend.
Keep the energy up throughout the video. Sound excited about the revelation.

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_STORIES = """
You are the Video Producer for "BlowYourMind" and you're writing a script for a vertical short video (1080x1920) about a fascinating curiosity.

The video format is a rapid-fire curiosity reel with quick scene changes.

**STRUCTURE (6-8 scenes):**
1. **Scene 1 - The Hook [0-8s]**: Start with a shocking question or a "did you know" statement that grabs attention. Use "You" to make it personal.
2. **Scenes 2-5 - The Reveal [8-40s]**: Unfold the fascinating details. Each scene reveals a new layer of the curiosity.
3. **Scenes 6-7 - The Impact [40-52s]**: Explain why this matters or how it affects our understanding of the world.
4. **Final Scene - The CTA [52-60s]**: End with a mind-blowing perspective shift and a question that invites comments.

**PER-SCENE FIELDS:**
- `scene_number`: Sequential number
- `visual_type`: Use "stock_video" for real footage, "ai_image" for conceptual/illustrative imagery (historical, microscopic, abstract concepts).
- `image_prompt`: Physical description and style in ENGLISH for AI image generation (only for ai_image type).
- `pexels_query`: 1-3 English keywords to search for stock video (e.g., "brain neurons", "ancient pyramid", "jellyfish ocean").
- `narration`: Spoken narration in ENGLISH. Each sentence must deliver a punch of curiosity.

**NARRATION RULES:**
- Total narration: MAX 150 words (60 seconds).
- Every sentence must spark curiosity.
- The FIRST line MUST use "You" or "Your" to hook personally.
- The LAST line MUST be a question that makes people comment.

**VISUAL STYLE (randomly pick one):**
Choose one of these styles and use it consistently across all scenes:
- Hyper-realistic cinematic lighting, dark moody colors, National Geographic quality
- Vintage illustration on aged parchment, sepia tones, historical aesthetic
- Dark digital art with neon accents, high contrast, modern infographic style
- Surreal fantasy realism with cosmic colors, dreamlike quality
- Clean modern documentary style, bright colorful, educational channel aesthetic

**CRITICAL:** ALL text and narration must be in ENGLISH. The video should feel fast-paced and full of wonder.
"""

FOCUS_AREAS_STORIES = [
    "COGNITIVE BIASES: Mind tricks your brain plays on you every day — the Mandela Effect, confirmation bias, the Dunning-Kruger effect, and why you're not as rational as you think.",
    "HIDDEN ANIMAL SUPERPOWERS: Animals with abilities that seem like science fiction — tardigrades that survive space, pistol shrimp that create plasma, axolotls that regenerate limbs.",
    "EXTREME SURVIVAL: True stories of people who survived impossible situations — plane crashes in the Andes, 72 days lost at sea, years alone on deserted islands.",
    "HISTORICAL COINCIDENCES: Bizarre coincidences in history that seem too strange to be true — Lincoln and Kennedy parallels, the Great Moon Hoax, the man who survived both atomic bombs.",
    "BODY MYSTERIES: Strange things your body does that you didn't know about — why we yawn, what dreams actually are, the purpose of goosebumps, why we forget dreams.",
    "SCIENTIFIC PARADOXES: Mind-bending scientific paradoxes — Schrödinger's cat, the Fermi Paradox, the Bootstrap Paradox, and why they break our brains.",
    "FORGOTTEN TECHNOLOGIES: Ancient technologies that modern science can't explain — Greek fire, Damascus steel, Roman concrete, the Antikythera mechanism.",
    "WEIRD LAWS: Real laws that sound fake — it's illegal to die in this town, owning a pet whale is legal in this country, the law that makes you pay for the moon.",
    "FOOD FACTS: Mind-blowing facts about what you eat — why honey never spoils, wasabi isn't real wasabi, the science of why cheese is addictive, the truth about expiration dates.",
    "SPACE CURIOSITIES: Strange facts about space — a day on Venus is longer than its year, there's a planet where it rains glass sideways, the sound of space is actually terrifying.",
    "PSYCHOLOGICAL EXPERIMENTS: Famous psychological experiments and what they revealed — the Stanford Prison Experiment, the Milgram shock experiment, the Marshmallow Test.",
    "NATURAL PHENOMENA: Incredible natural phenomena you've never heard of — blood falls in Antarctica, the singing dunes of the desert, lightning that never stops, the door to hell.",
    "RANDOM PROBABILITIES: Shocking probability facts — the chance of being born is 1 in 400 trillion, the lottery is more likely than this, you share a birthday with 20 million people.",
    "LOST CIVILIZATIONS: Mysterious ancient civilizations that disappeared without explanation — the Indus Valley, the Minoans, the Anasazi, the Kingdom of Kush.",
    "TECHNOLOGY PARADOXES: Modern technology paradoxes — the internet weighs as much as a strawberry, every step you take generates data, the cloud is actually underwater cables.",
    "UNSOLVED CRIMES: Famous unsolved crimes and mysteries — the Zodiac killer, D.B. Cooper, the Tamam Shud case, the Somerton Man.",
    "LINGUISTIC CURIOSITIES: Strange facts about language — the word 'set' has 464 definitions, there's a language with no words for numbers, the most untranslatable words.",
    "MEDICAL MYSTERIES: Strange medical conditions and cases — people who don't feel pain, foreign accent syndrome, the man who forgot his entire life every 2 hours.",
    "OCEAN MYSTERIES: Deep ocean secrets — we've mapped more of Mars than our oceans, the deepest point is darker than space, creatures that live at crushing depths.",
    "MATHEMATICAL WONDERS: Mind-blowing math facts — the number 0.999... equals 1, the Banach-Tarski paradox, the Monty Hall problem, why infinity isn't a number.",
    "TIME PERCEPTION: How time works differently than you think — your perception of time changes with age, time dilation is real, why time flies when you're having fun.",
    "ARTIFICIAL INTELLIGENCE: Mind-blowing AI facts — AI can now beat humans at everything, the first AI passed the Turing test years ago, AI dreams in images.",
    "HUMAN LIMITS: The extreme limits of the human body — the longest someone has gone without sleep, the hottest temperature survived, the deepest free dive.",
    "CONSPIRACY THEORY ORIGINS: The real stories behind famous conspiracy theories — where they started, why people believe them, and the truth behind them.",
    "RECORD BREAKERS: Extreme world records you won't believe — the longest hiccup episode (68 years), the heaviest weight lifted by tongue, the most pierced person.",
    "SLEEP MYSTERIES: Strange facts about sleep — sleep is more complex than you think, sleep paralysis demons explained, what really happens when you dream.",
    "MONEY CURIOSITIES: Strange facts about money — the largest bill ever printed was $100,000, there are more Monopoly money printed than real money, salt was once currency.",
    "EVOLUTION SURPRISES: Evolution facts that defy intuition — why humans lost their tails, the dinosaur that evolved into a bird, the animal that hasn't evolved in 200 million years.",
    "MAP CURIOSITIES: Map facts that will change how you see the world — Africa is bigger than you think, Australia is wider than the moon, the most remote place on Earth.",
    "GENETIC WONDERS: Amazing genetic facts — your DNA can stretch to the sun and back, you share 60% of your DNA with bananas, genes can skip generations.",
]
