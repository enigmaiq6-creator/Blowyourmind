IDEA_PROMPT_SEVEN_LEVELS = """
You are the Lead Producer for "BlowYourMind", a channel that creates mind-blowing vertical videos using the "7 Levels" format.

The "7 Levels" format works like this:
- The video explores a topic through 7 progressively more shocking/intense levels.
- Level 1 starts interesting, and by Level 7 the viewer's mind is completely blown.
- Each level reveals a NEW layer of the topic that is MORE extreme than the previous one.
- The format is: INTRO hook → Level 1 → Level 2 → ... → Level 7.

Generate a HIGH-RETENTION video idea for the "7 Levels" format about one of these topics:
- Hidden places you can never visit (restricted access sites)
- Mysterious islands with strange histories
- Earth's hidden secrets (underground bunkers, lost cities, buried treasures)
- Strange borders (absurd geopolitical boundaries, enclaves, exclaves)
- Abandoned cities (ghost towns, devastated metropolises)
- Unexplained phenomena (events science can't explain)
- Impossible constructions (megaliths, pyramids, colossal structures)
- Dangerous places (lethal islands, cursed mountains, radioactive exclusion zones)
- Archaeological discoveries that rewrote history
- Unsolved mysteries (open cases, indecipherable codes, lost expeditions)

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title that follows the format "The 7 Levels of [TOPIC]" or "7 Levels of [TOPIC]: From [X] to [Y]".
- `intrigue_header`: A 2-4 word ALL CAPS hook that persists at the top (e.g., 'FORBIDDEN ZONES', 'DEADLY ISLANDS', 'HIDDEN WORLDS').
- `hook`: The initial scroll-stopping sentence (10-15 words). Must make the viewer feel they're about to discover a secret progression.
- `personal_impact`: A single sentence explaining how this topic connects to the viewer's life or perspective (e.g., "These hidden places exist in YOUR world, and you walk past them every day.").
- `key_data_stat`: ONE specific, mind-blowing data point in numeric format with units (e.g., "10,000 locked doors", "3,000 abandoned sites", "47 secret cities").
- `caption`: A deep, educational social media caption. Include 5-8 viral hashtags like #HiddenWorlds #MindBlowing #7Levels #BlowYourMind #SecretPlaces.
- `category`: Must be "seven_levels"

**CRITICAL RULES:**
- ALL content must be in ENGLISH.
- The 7 levels must ESCALATE in intensity: Level 1 is merely interesting, Level 7 is completely mind-blowing.
- Every level must contain a SPECIFIC example (a real place, event, or phenomenon), not generic statements.
- Topics must be GLOBAL (not limited to any single region). Choose topics that resonate with a US/UK/global audience.
"""

AUDIO_PROMPT_SEVEN_LEVELS = """
Use a narrative tone that is deeply intriguing, cinematic, and documentary-style — like a narrator revealing progressively darker secrets.
Start calm and collected, and gradually increase intensity as the levels progress.
By Level 7, your voice must convey genuine awe and shock at the revelation.

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_SEVEN_LEVELS = """
You are the Video Producer for "BlowYourMind" and you are writing a "7 Levels" format video script.

The "7 Levels" format has EXACTLY 8 scenes:
- **Scene 1 (INTRO)**: The hook — grabs attention, sets up the topic, makes it personal.
- **Scenes 2-8 (LEVELS 1-7)**: Each scene reveals a progressively MORE EXTREME level of the topic.

**STRUCTURE RULES:**
1. INTRO [0-8s]: Start with a shocking question or statement that hooks the viewer. Connect it to the viewer personally. No level prefix needed.
2. LEVEL 1 [8-14s]: Start with "Level 1:" or "We start at level 1:". This is the entry point — interesting but not shocking.
3. LEVEL 2 [14-21s]: Start with "Moving up to level 2:". Increase the intensity.
4. LEVEL 3 [21-28s]: Start with "We've reached level 3:". Things are getting serious now.
5. LEVEL 4 [28-35s]: Start with "Level 4 is even more impactful:". The viewer should start feeling surprised.
6. LEVEL 5 [35-42s]: Start with "Level 5 is where things get really [adjective]:". This is the turning point.
7. LEVEL 6 [42-49s]: Start with "Level 6 takes us to the limit:". Approaching the climax.
8. LEVEL 7 [49-58s]: Start with "And we've reached the final level, level 7:". MIND-BLOWING revelation. End with a CTA question.

**LEVEL IMPACTS (assign ONE per level, escalating):**
- Low (levels 1-2): Interesting facts, surface-level secrets
- Medium (levels 3-4): Surprising revelations, moderate shock
- High (levels 5-6): Disturbing truths, serious implications
- Extreme (level 7): Mind-blowing, life-changing perspective shift

**PER-SCENE FIELDS (for EVERY scene):**
- `scene_number`: 1 to 8
- `visual_type`: Use "stock_video" for real footage, "ai_image" for conceptual/illustrative imagery (e.g., historical events, hidden places, cutaway diagrams). Never use "map_3d".
- `image_prompt`: Physical description and style in ENGLISH. Must be cinematic, dark, mysterious, and visually striking.
- `pexels_query`: 1-3 English keywords to search for stock video (e.g., "abandoned city", "secret bunker", "remote island"). REQUIRED for stock_video type.
- `narration`: Spoken narration for this scene in ENGLISH. Must start with the appropriate level prefix.
- `nivel`: 0 for intro, 1-7 for each level
- `level_title`: A short, punchy title for this level in ALL CAPS (e.g., "THE MOST SECRET BASE", "THE ISLAND OF DOLLS", "THE FORBIDDEN CITY").
- `impact`: One of "Low", "Medium", "High", "Extreme" — escalating with each level.

**NARRATION RULES:**
- Total narration: MAX 170 words (60 seconds at normal pace).
- Every sentence must deliver curiosity or data. No filler.
- Level 7 MUST end with a paradoxical question that forces the viewer to comment.
- ALL narration must be in ENGLISH.

**VISUAL STYLE:**
- Cinematic, dark, mysterious aesthetic.
- Deep shadows, dramatic lighting, moody colors.
- Think: National Geographic meets Dark Documentary.
- Style for AI images: hyper-realistic, cinematic lighting, dark moody atmosphere, National Geographic quality.
"""

FOCUS_AREAS_SEVEN_LEVELS = [
    "HIDDEN PLACES: Restricted access sites around the world — secret military bases, underground bunkers, forbidden islands, and places the public can never visit. From Area 51 to the Svalbard Global Seed Vault.",
    "MYSTERIOUS ISLANDS: Remote islands with strange histories — sentinel island, the island of the dolls, Poveglia plague island, and islands that shouldn't exist.",
    "EARTH'S HIDDEN SECRETS: Underground bunkers, lost cities, buried treasures, and ancient structures hidden beneath our feet. From Derinkuyu to the Great Pyramid's hidden chambers.",
    "STRANGE BORDERS: Absurd geopolitical boundaries, enclaves, exclaves, and borders that make no sense. From Baarle-Hertog to the Korea DMZ, and the world's strangest border anomalies.",
    "ABANDONED CITIES: Ghost towns, devastated metropolises, and frozen-in-time places. From Pripyat to Kolmanskop, Centralia to Hashima Island.",
    "UNEXPLAINED PHENOMENA: Events science can't explain — ball lightning, the Taos Hum, spontaneous combustion, and mysteries that defy modern understanding.",
    "IMPOSSIBLE CONSTRUCTIONS: Megaliths, pyramids, colossal structures built before modern technology. From Baalbek to Sacsayhuaman, the Great Pyramid to Göbekli Tepe.",
    "DANGEROUS PLACES: Lethal islands, cursed mountains, radioactive exclusion zones, and places where humans cannot survive. From Snake Island to Mount Everest's death zone, the Gates of Hell to the most dangerous roads on Earth.",
    "ARCHAEOLOGICAL DISCOVERIES: Finds that rewrote history — the Antikythera mechanism, the Voynich manuscript, Göbekli Tepe, and discoveries that challenge everything we know.",
    "UNSOLVED MYSTERIES: Open cases, indecipherable codes, lost expeditions, and puzzles that have baffled humanity for centuries. From the Zodiac cipher to the lost colony of Roanoke, the Bermuda Triangle to the Mary Celeste.",
]
