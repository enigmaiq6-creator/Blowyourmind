IDEA_PROMPT_FACT_SPLIT = """
You are the Creative Producer for "BlowYourMind", a channel specializing in viral "Fact Split" comparison videos.
Your task is to generate a comparative idea between TWO subjects that has viral potential.

**VIDEO STRUCTURE (4 ACTS):**
1. **Act 1 (0-2s)**: "This is [Subject A]" — Character points top-left (estado_A.png).
2. **Act 2 (2-4s)**: "This is [Subject B]" — Character points top-right (estado_B.png).
3. **Act 3 (4-6s)**: "What's the difference?" — Character with hands down, question marks (estado_curiosidad.png).
4. **Act 4 (6-end)**: Explanation of the unique contrast — Character dynamically points to whichever subject is being mentioned at that moment.

**VIRAL COMPARISON RULES:**
- Both subjects must be VISUALLY DISTINCT but belong to the same general category.
- The contrast must be something most people DON'T KNOW.
- The fact must be surprising but TRUE.
- Must make people want to comment: "Which one surprised you more?"

**EXAMPLES OF GOOD CONTRASTS:**
- Wolf vs Golden Retriever → "The wolf has twice the jaw pressure of any domestic dog."
- Crocodile vs Lizard → "Crocodiles don't sweat — they regulate temperature with their mouths open."
- Helium vs Hydrogen → "Hydrogen is the most abundant element in the universe, but helium cannot be synthesized."

**CRITICAL SPELLING RULE:** All generated English text MUST have PERFECT spelling and grammar. No typos, no misspellings, no punctuation errors. Each word must be correctly spelled. This is a hard requirement.

**MANDATORY FIELDS (ALL IN ENGLISH):**
- `tema`: Theme category: 'science', 'animals', 'history', 'mythology', 'technology', 'space', or 'geography'.
- `sujeto_a`: Name of Subject A.
- `sujeto_b`: Name of Subject B.
- `hook`: Scroll-stopping opening phrase (10-15 words in English). Must create intrigue.
- `contrast_key`: One-line summary of the key difference in English.
- `pexels.query_sujeto_a`: English search query for stock photo of Subject A (very descriptive, used for the SINGLE shared image of Subject A throughout the video).
- `pexels.query_sujeto_b`: English search query for stock photo of Subject B (very descriptive, used for the SINGLE shared image of Subject B throughout the video).
- `locucion.texto_a`: Act 1 narration in English. Starts with "This is...".
- `locucion.texto_b`: Act 2 narration in English. Starts with "This is...".
- `locucion.pregunta`: "What's the difference?" (or similar question).
- `locucion.contraste_final`: Contrast explanation in 1-2 sentences.
- `caption`: Viral caption in English with 5-8 hashtags (include #BlowYourMind #FactSplit #MindBlowing).
- `category`: "fact_split"
"""

SCRIPT_PROMPT_FACT_SPLIT = """
You are the Video Director for "BlowYourMind" — Fact Split format.
Based on the IDEA, write the complete technical production script.

**EXACT STRUCTURE — 4 ACTS (30-45 seconds total):**

**ACT 1 (0-2s) — Subject A**
- Character: estado_A.png (pointing top-left)
- Subject visible: A (top-left quadrant, x=40:y=60)
- On-screen text: Subject A name
- Narration (locucion.texto_a): "This is [Subject A]. [Mind-blowing fact]."

**ACT 2 (2-4s) — Subject B**
- Character: estado_B.png (pointing top-right)
- Subject visible: B (top-right quadrant, x=560:y=60)
- On-screen text: Subject B name
- Narration (locucion.texto_b): "This is [Subject B]. [Mind-blowing fact]."

**ACT 3 (4-6s) — Question**
- Character: estado_curiosidad.png (hands down, question marks)
- Subject visible: both (A at x=40:y=60, B at x=560:y=60)
- Visual text: "Did you know?" or large question mark
- Narration (locucion.pregunta): "What's the difference?"

**ACT 4 (6s-end) — Explanation**
- Character: dynamically points to whichever subject is being mentioned
- Subject visible: both (same positions)
- On-screen explanation text
- Narration (locucion.contraste_final): Contrast explanation.

**SOUND EFFECTS (SFX):** Each scene can have an `sfx` field. Use `sfx: "swoosh"` for scenes where the character changes pointing direction (character transitions). Use `sfx: "none"` for static scenes.

**MANDATORY TECHNICAL FIELDS:**
- `scenes`: Array of 4 acts, each with:
  - `act_number`: 1-4
  - `narration`: English narration for this act
  - `stickman_state`: Default state for the act ('estado_A', 'estado_B', or 'estado_curiosidad')
  - `stickman_timeline`: Array of {start_sec, end_sec, state} for time-based switching within the act. CRITICAL: In Act 4, when narration mentions Subject A, the character MUST point to A (estado_A). When it mentions Subject B, it MUST point to B (estado_B). Use estado_curiosidad for general statements.
  - `sujeto_visible`: 'A', 'B', or 'ambos'
  - `visual_text`: Optional on-screen text in English
  - `sfx`: Sound effect for this scene. "swoosh" when character changes state, "none" for static scenes.
  - `pexels_query_a`: Pexels query for Subject A image
  - `pexels_query_b`: Pexels query for Subject B image
  - `overlay_positions`: FFmpeg overlay coordinates
- `pexels`: Same queries as in the idea
- `locucion`: Same texts as in the idea
- `ffmpeg_logic`: Object with:
  - `input_1`: Description of all inputs
  - `acts`: Array with {tiempo, sujeto_visible, stickman_file, posicion_sujeto, texto_visual, explicacion}
- `whisper_payload`: Full concatenated narration text for subtitle segmentation

**CRITICAL:**
- ALL content must be in ENGLISH with PERFECT spelling and grammar — no typos, no misspellings.
- Each act must last EXACTLY as specified (2s, 2s, 2s, remainder).
- Pexels queries must be in ENGLISH.
- The final explanation must be surprising but TRUE.
- **IMPORTANT: The SAME subject images are used throughout the entire video.** The pexels_query_a / pexels_query_b for each scene should be CONSISTENT (same query for Subject A across all scenes, same query for Subject B across all scenes). The images never change per scene.
"""

AUDIO_PROMPT_FACT_SPLIT = """
Use a dynamic, fast-paced, and curious narrative tone — like a fact presenter on TikTok or YouTube Shorts.
The voice should sound enthusiastic and slightly dramatic on the contrasts.

TEXT TO NARRATE:
{audio_text}
"""

FOCUS_AREAS_FACT_SPLIT = [
    "Animals: predator vs domesticated",
    "Animals: marine mammal vs fish",
    "Animals: social insect vs solitary",
    "Animals: bird of prey vs songbird",
    "Animals: reptile vs amphibian",
    "Science: acid vs base",
    "Science: renewable energy vs fossil fuel",
    "Science: star vs planet",
    "Science: virus vs bacteria",
    "Science: DNA vs RNA",
    "History: empire vs republic",
    "History: revolution vs evolution",
    "History: middle ages vs renaissance",
    "History: colonization vs independence",
    "History: cold war vs world war",
    "Technology: CPU vs GPU",
    "Technology: internet vs intranet",
    "Technology: Machine Learning vs Deep Learning",
    "Technology: encryption vs hash",
    "Technology: VR vs AR",
    "Mythology: Greek god vs Norse god",
    "Mythology: mythical creature vs real",
    "Mythology: hero vs demigod",
    "Mythology: myth vs legend",
    "Mythology: eastern dragon vs western dragon",
    "Space: rocky planet vs gas giant",
    "Space: black hole vs neutron star",
    "Space: comet vs asteroid",
    "Space: moon vs artificial satellite",
    "Space: nebula vs galaxy",
    "Geography: river vs lake",
    "Geography: volcano vs mountain",
    "Geography: desert vs tundra",
    "Geography: ocean vs sea",
    "Geography: glacier vs iceberg",
]
