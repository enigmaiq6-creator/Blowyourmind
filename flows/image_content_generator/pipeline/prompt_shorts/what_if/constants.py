IDEA_PROMPT_WHAT_IF = """
You are the Lead Producer for "BlowYourMind", a channel about alternate geography and counterfactual scenarios.
Generate a HIGH-RETENTION video idea about a "What If" hypothetical geography scenario.

The topic must explore how changes in geography, borders, population, resources, or history would reshape the world.
Choose scenarios that feel plausible, spark curiosity, and make viewers want to comment their opinion.

**HOOK PSYCHOLOGY — CRITICAL FOR 300K VIEWS:**
The hook must make the viewer STOP SCROLLING in the first second.
Use these PROVEN viral patterns for the `hook` field:

Pattern A — Imagine + You: "Imagine waking up tomorrow and [impossible scenario]. What would happen to YOUR life?"
  → Forces mental visualization. "YOUR" creates personal stakes.

Pattern B — The Impossible Statement: "What if [scenario] happened overnight? YOUR [food/jobs/travel/economy] would never be the same."
  → Immediate personal impact. Makes it real.

Pattern C — The Shocking Comparison: "[Crazy comparison] — that's what the world would look like if [scenario]."
  → Visual + unexpected. Makes them picture it.

Pattern D — The Secret Reveal: "There's a reason [country/region] looks the way it does. But what if that reason disappeared?"
  → Curiosity gap about the current world, then twists it.

Examples of viral hooks using these patterns:
- "Imagine waking up tomorrow and Africa was ONE country. YOUR grocery prices would triple overnight."
- "What if the Panama Canal was never built? YOUR shipping costs would be 10x higher."
- "There's a reason Brazil speaks Portuguese in a continent of Spanish. But what if history was different?"
- "What if Antarctica was green? YOUR coastal city would be underwater right now."
- "Imagine Canada had India's population overnight. YOUR winter vacations would never be the same."

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title (8-15 words). MUST use one of these formats:
  - "What If [Scenario] Happened [Timeframe]?" (e.g., "What If Africa Became One Country Tomorrow?")
  - "The [Adjective] Reason Why [Scenario] Would Change YOUR Life"
  - "Imagine [Scenario]. Here's How It Would Destroy YOUR World."
  Keep it specific and personal. Avoid generic "What If X" — add a consequence in the title.
- `hook`: The opening scroll-stopping sentence (12-18 words). MUST use Pattern A (Imagine + You) or Pattern D (Secret Reveal). Must contain "YOUR" or "YOU". Must make the viewer imagine the scenario happening to THEM.
- `primary_country`: The main country or region involved.
- `primary_continent`: The continent of the scenario.
- `scenario_type`: One of — 'location_swap', 'country_union', 'territorial_expansion', 'population_change', 'natural_change', 'alternate_history', 'resource_shift'.
- `consequences`: 3-5 specific, concrete, measurable consequences. Each must mention how it affects real people.
- `unexpected_twist`: A single sentence with a negative consequence (e.g., "But uniting 54 countries with 2,000 languages would create chaos beyond imagination.")
- `closing_question`: A short question that forces viewers to comment their opinion (e.g., "Would this new superpower unite or destroy the world? Comment below.")
- `caption`: A SHORT caption (max 3 lines) that starts with the hook question and ends with the closing question. Include 8-10 viral hashtags prioritizing #WhatIf #AlternateGeography #MindBlowing #GeographyFacts #BlowYourMind.
- `category`: Must be "what_if"

**CRITICAL RULES:**
- ALL content in ENGLISH. Global topics (US/UK/global audience).
- TITLE must include a personal consequence. "What If X" alone is not enough — add "YOUR life would change".
- HOOK must contain "YOUR" or "YOU" — personal stakes are mandatory.
- CLOSING QUESTION must demand a comment. Make it debatable, not yes/no.
- VARY primary_country and scenario_type across consecutive videos. Alternate continents.
"""

AUDIO_PROMPT_WHAT_IF = """
Use a narrative tone that is clear, fast-paced, and intriguing — like a documentary narrator explaining a fascinating hypothetical scenario.
The tone should be engaging, confident, and slightly speculative, using phrases like "could", "might", "would likely", and "in this scenario."

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_WHAT_IF = """
You are the Video Producer & Graphic Designer for "BlowYourMind".
Based on the provided IDEA, write a complete production script for a vertical short video (1080x1920) lasting 35 to 60 seconds.

The video must be a "What If" alternate geography scenario:
- Use AI-GENERATED IMAGES as the PRIMARY visual for ALL scenes. No 3D maps, no real satellite imagery.
- Each scene shows a cinematic AI-generated still image depicting the hypothetical world.
- Text overlays (titles, big numbers, labels) appear on top of the images.
- The viewer should understand the scenario through powerful visuals + on-screen text.

**STRUCTURE: 6 SCENES (35-60 seconds total):**

1. **Scene 1 - The Hook [0-3s]**: Start with the "What If" question as large text on screen. The image should show a dramatic vision of the alternate world — a stylized map or landscape that sets the scene. Use scene_overlay_type: "title" for the hook question.

2. **Scene 2 - Context [3-10s]**: Explain the current real-world situation. The image should show the real-world setting with data visualized as graphic elements within the image (population numbers, territory outlines, flags). Use scene_overlay_type: "big_number" or "location" for key facts.

3. **Scene 3 - The Change [10-20s]**: Show the hypothetical change happening. The image should depict the transformation visually — countries merging, borders shifting, territories expanding. Include visual hints of movement (arrows, dashed lines) as graphic elements within the generated image. Use scene_overlay_type: "title" for the change description.

4. **Scenes 4-5 - Consequences [20-45s]**: Show 2-3 consequences per scene. Each image should depict a different aspect: population explosion, economic maps, resource maps, military comparisons. Include flag icons, data numbers, and graphic charts as elements within the image. Use scene_overlay_type: "big_number" or "trade" for data.

5. **Scene 6 - Twist + Closing [45-60s]**: Show the unexpected negative consequence. The image should be darker, more dramatic — conflict zones, protests, crisis atmospheres. End with the closing question as text overlay. Use scene_overlay_type: "nightmare" for the twist and "title" for the closing question.

**TECHNICAL RULES (STRICT):**
- Primary visual type: "ai_image" for ALL scenes. NEVER use "map_3d".
- `image_prompt`: Write a DETAILeD visual description in ENGLISH for AI image generation. Describe:
  - Setting and composition (e.g., "A stylized map of South America at night")
  - Colors and lighting (e.g., "Dark navy background with teal and coral accents")
  - Graphic elements to include (e.g., "Glowing country borders, floating population numbers, flag icons")
  - Mood and style (e.g., "Cinematic documentary style, clean sans-serif text elements, dark modern aesthetic")
  - DO NOT describe real 3D map features (camera angles, GPS coordinates, terrain)
- Each image_prompt MUST be unique per scene. Vary the composition, colors, and focus.
- `scene_overlay_type`: Use overlays to display key information on screen — titles, big numbers, location badges, etc.

**OVERLAY FIELDS (sceneOverlay) — SIX TYPES AVAILABLE:**
Each overlay type controls what appears as text on screen during the scene:

- **`title`** {text, position}: Main headline text. Position can be 'top' or 'center'. Use for the hook question in Scene 1 and change title in Scene 3.
- **`big_number`** {number, label, suffix}: A large animated counter number with label and optional suffix. Use for population, territory, economic stats.
- **`year`** {year}: A year badge in the corner (for history scenarios).
- **`location`** {name, country, coordinates}: Location badge showing place name and coordinates.
- **`nightmare`** {text}: A dark/ominous prediction text. Use for the twist in Scene 6.
- **`trade`** {from, to, value, commodity}: Trade route info card. Use for economic consequences.

Examples of overlay usage:
- Scene 1: title "WHAT IF BRAZIL RULED ALL OF SOUTH AMERICA?"
- Scene 2: big_number {number: 214000000, label: "POPULATION", suffix: ""} + location {name: "Brazil", country: "South America"}
- Scene 3: title "BRAZIL EXPANDS ACROSS THE CONTINENT" + big_number {number: 17, label: "COUNTRIES ABSORBED", suffix: ""}
- Scene 4: big_number {number: 17000000, label: "SQ KM", suffix: "TOTAL AREA"} + trade {from: "Amazon", to: "Global Markets", value: "$200B", commodity: "Resources"}
- Scene 5: big_number {number: 450000000, label: "POPULATION", suffix: ""} + nightmare {text: "But controlling such a massive territory with 9 different languages would be extremely difficult."}
- Scene 6: nightmare {text: "Separatist movements could tear the continent apart."} + title "WOULD THIS UNITE OR DESTROY SOUTH AMERICA?"

**IMAGE PROMPT GUIDELINES (CINEMATIC QUALITY — STRICT):**
ALL images MUST follow these cinematography rules:
- **Resolution**: Native vertical 9:16 (1080×1920) — NO horizontal/landscape compositions. The image itself must be composed for vertical viewing.
- **Lighting**: Cinematic lighting — rim lights, dramatic shadows, volumetric light rays where possible. Avoid flat/uniform lighting. Each scene should have a distinct lighting mood.
- **Depth**: Multi-layer composition with clear foreground, midground, and background. Use depth of field (background blur) for cinematic feel.
- **Style**: Photorealistic documentary photograph. NOT a map, NOT a flat illustration, NOT a diagram. Should look like a frame from a Netflix documentary. Graphic data elements (numbers, labels) may appear embedded in the scene naturally (e.g., on screens, billboards, as holographic overlays).
- **Variety**: Each scene MUST have a DIFFERENT visual identity — distinct color palette, scene type, and composition. No two scenes should look like they belong to the same template.
- **Text space**: Leave the top 25% and bottom 20% of the frame relatively clear for text overlays and subtitles. Do not place critical visual elements in these zones.
- **Composition**: Use rule of thirds. Place key visual elements off-center to avoid overlap with center-screen text.

Per-scene specifics:
- **Scene 1 — The Hook**: Dramatic establishing shot of the alternate world. Show a photorealistic scene that instantly communicates the "What If" — e.g., a skyscraper skyline with an impossible landmark, a landscape with altered geography, a bustling port where one shouldn't exist. Golden hour or blue hour lighting. Rich warm tones (amber, gold, sunset orange) or cool sci-fi blues (cyan, deep teal). No maps, no diagrams. The hook title text will overlay at top center. 9:16 vertical.
- **Scene 2 — Context**: Documentary photograph style showing the real-world situation grounded in reality. A photorealistic scene of the actual place/people involved — e.g., a crowded street, a factory, a port, a landscape. Use amber and warm steel tones. Include subtle embedded data: a glowing building number, a screen showing a population count, a road sign with a distance. Feels like a frame from a Vice or Netflix documentary. 9:16 vertical.
- **Scene 3 — The Change**: Dramatic transformation scene — the moment the hypothetical change occurs. Show a cinematic wide shot of the transition happening: a border wall crumbling, a massive bridge connecting two landmasses, a fleet of ships arriving at a new coast, a desert turning green. Golden/coral light piercing through dust or fog. Sense of motion and scale. Human figures silhouetted in foreground for scale. No diagrams or arrows — let the image itself tell the story. 9:16 vertical.
- **Scene 4 — Consequences (Part 1)**: Economic or geopolitical consequence shown as a real scene. E.g., a massive new shipping port with cranes and container ships at sunset (trade consequence), a sprawling megacity at night with glowing windows (population consequence), a military fleet in formation (military consequence). Vibrant teal and magenta neon accents at night, or warm amber/gold during golden hour. Data overlays appear naturally (e.g., a giant screen on a building showing "$2.5T" or a holographic globe showing trade routes). 9:16 vertical.
- **Scene 5 — Consequences (Part 2)**: Human or social consequence — completely different palette and scene type from Scene 4. E.g., a street market overflowing with people (cultural mixing), a classroom with students of mixed backgrounds, a refugee camp at dawn (negative consequence), a futuristic city boulevard with autonomous vehicles. Use distinct palette: if Scene 4 was warm amber, use cool cyan+magenta here. The scene must feel like a different world from Scene 4. 9:16 vertical.
- **Scene 6 — Twist + Closing**: Dark cinematic climax. The unexpected negative consequence visualized as a dramatic scene. E.g., protest burning barricades in a city square at night, a cracked drought landscape with storm clouds, a military checkpoint under red emergency lights, a crumbling infrastructure scene. Red and crimson dominant colors, heavy shadows, smoke or fog, harsh directional lighting (street lamps, fires, headlights). Ominous mood. Space at bottom center for the closing question text. 9:16 vertical.

**NARRATION RULES:**
- Total narration: MAX 130 WORDS (60 seconds at normal pace).
- Short, punchy sentences. No filler.
- Each sentence corresponds to one visual element.
- Use speculative language: "could", "might", "would likely", "in this scenario".
- The FINAL sentence MUST be the closing_question from the idea.

**CRITICAL: ALL TEXT AND NARRATION MUST BE IN ENGLISH.**
"""

FOCUS_AREAS_WHAT_IF = [
    "What if South America became one country?",
    "What if Africa became one country?",
    "What if India and China switched places?",
    "What if Brazil was located in Europe?",
    "What if Japan was next to the United States?",
    "What if Australia was in the Arctic?",
    "What if Canada was located in Africa?",
    "What if Colombia was next to Spain?",
    "What if Mexico was located in Asia?",
    "What if all Arab countries united?",
    "What if Central America became one nation?",
    "What if the Caribbean became one country?",
    "What if the Nordic countries united?",
    "What if every country in Europe became one empire?",
    "What if Brazil controlled all of South America?",
    "What if Germany controlled Europe?",
    "What if India controlled Asia?",
    "What if Canada controlled the Arctic?",
    "What if Mexico controlled Central America?",
    "What if Indonesia controlled all Pacific islands?",
    "What if Turkey controlled the Middle East?",
    "What if Canada had India's population?",
    "What if Australia had 500 million people?",
    "What if Africa had only 100 million people?",
    "What if Japan had 1 billion people?",
    "What if Greenland had the population of China?",
    "What if Colombia had 200 million people?",
    "What if the Sahara became a rainforest?",
    "What if Antarctica melted?",
    "What if the Amazon River dried up?",
    "What if the Mediterranean Sea disappeared?",
    "What if the Himalayas vanished?",
    "What if the Arctic became habitable?",
    "What if the USSR never collapsed?",
    "What if the British Empire never fell?",
    "What if the Roman Empire survived?",
    "What if Germany won World War II?",
    "What if the Panama Canal was never built?",
    "What if the United States split into 50 countries?",
    "What if the Cold War never ended?",
    "What if Venezuela controlled all oil reserves?",
    "What if Africa controlled all global food production?",
    "What if Greenland discovered massive gold reserves?",
    "What if Brazil controlled the Amazon's resources?",
    "What if Saudi Arabia ran out of oil?",
    "What if China lost access to the Pacific Ocean?",
    "What if the Amazon Rainforest became a country?",
    "What if the United States split into 50 countries?",
    "What if Europe had only 3 countries?",
    "What if Russia split into 10 different countries?",
    "What if Mexico became part of the United States?",
    "What if the Korean Peninsula reunified today?",
    "What if the Pacific Ocean disappeared?",
    "What if the United Kingdom had the population of India?",
    "What if Antarctica was a lush green continent?",
    "What if the Gobi Desert became a sea?",
    "What if the Caspian Sea dried up?",
    "What if the Bosporus Strait closed?",
    "What if the Suez Canal was never built?",
    "What if the Mississippi River flowed west instead of east?",
    "What if California became an independent country?",
    "What if Texas became an independent country?",
    "What if Puerto Rico became a sovereign nation?",
    "What if Alaska was returned to Russia?",
    "What if Hawaii was an independent kingdom?",
    "What if the Baltic states were still part of Russia?",
    "What if Czechoslovakia never split?",
    "What if Yugoslavia never collapsed?",
    "What if the Ottoman Empire survived into the 21st century?",
    "What if the Persian Empire still existed?",
    "What if the Mongol Empire never fragmented?",
    "What if the Spanish Empire still controlled Latin America?",
    "What if the Portuguese Empire still existed?",
    "What if the Dutch Empire never declined?",
    "What if France still controlled North America?",
]
