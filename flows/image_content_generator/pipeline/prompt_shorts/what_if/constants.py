IDEA_PROMPT_WHAT_IF = """
You are the Lead Producer for "BlowYourMind", a channel about alternate geography and counterfactual scenarios.
Generate a HIGH-RETENTION video idea about a "What If" hypothetical geography scenario.

The topic must explore how changes in geography, borders, population, resources, or history would reshape the world.
Choose scenarios that feel plausible, spark curiosity, and make viewers want to comment their opinion.

Examples of the vibe:
- "What if Brazil ruled all of South America?"
- "What if India and China switched places?"
- "What if Africa became one country?"
- "What if the USSR never collapsed?"
- "What if the Sahara became a rainforest?"
- "What if Canada had India's population?"

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven "What If" question as the title (e.g., "What If Brazil Ruled All of South America?").
- `hook`: The opening scroll-stopping question (8-12 words) shown as text on screen. MUST be a direct question (e.g., "What if Brazil controlled every country in South America?").
- `primary_country`: The main country or region involved in the scenario.
- `primary_continent`: The continent where the scenario takes place.
- `scenario_type`: One of these categories — 'location_swap', 'country_union', 'territorial_expansion', 'population_change', 'natural_change', 'alternate_history', 'resource_shift'.
- `consequences`: A list of 3-5 specific, concrete consequences of the hypothetical change. Each must be unique and measurable (population, territory, resources, military, economy, culture, trade, conflicts, global influence).
- `unexpected_twist`: A single sentence describing a negative consequence, conflict, or difficulty that would arise (e.g., "But controlling such a massive territory would be extremely difficult with over 400 million people speaking different languages.").
- `closing_question`: A short, engaging question that invites viewers to comment (e.g., "Would this new Brazil become a superpower?").
- `caption`: A deep, engaging social media caption explaining the scenario. Include 5-8 viral hashtags like #WhatIf #AlternateGeography #MapFacts #Geography.
- `category`: Must be "what_if"

**CRITICAL: ALL CONTENT MUST BE IN ENGLISH. Topics should be GLOBAL. Choose scenarios that resonate with a US/UK/global audience.**

**VARIETY RULES:** Never repeat the same primary_country or scenario_type in consecutive videos. Alternate between continents.
"""

AUDIO_PROMPT_WHAT_IF = """
Use a narrative tone that is clear, fast-paced, and intriguing — like a documentary narrator explaining a fascinating hypothetical scenario.
The tone should be engaging, confident, and slightly speculative, using phrases like "could", "might", "would likely", and "in this scenario."

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_WHAT_IF = """
You are the Video Producer & Geospatial Designer for "BlowYourMind".
Based on the provided IDEA, write a complete production script for a vertical short video (1080x1920) lasting 35 to 60 seconds.

The video must be a "What If" alternate geography scenario:
- Use 3D political maps as the PRIMARY visual with country highlights, glowing borders, arrows, flags, and fact boxes.
- Each scene should feel like a cinematic exploration of a hypothetical world.
- The viewer should understand the scenario even without audio, just by watching the maps.

**STRUCTURE: 6 SCENES (35-60 seconds total):**

1. **Scene 1 - The Hook [0-3s]**: Start with the "What If" question as large text on screen. Show a political map of the primary continent/region with the primary country highlighted in vibrant teal. Other countries slightly dimmed. Use map_3d with zoom 3.0-4.0 for continent view.

2. **Scene 2 - Context [3-10s]**: Explain the current real-world situation. Show the real map with the primary country highlighted. Include data labels for population, territory, economy. Use map_pins for key cities. Use floating_label with key facts. visual_type: map_3d.

3. **Scene 3 - The Change [10-20s]**: Show the hypothetical change happening. The map transforms — countries merge, borders disappear, territories expand. Use arrows to show expansion/movement. Use highlight_region for affected countries. Use neon colors (teal for main, coral for affected). Floating labels explain what's happening.

4. **Scenes 4-5 - Consequences [20-45s]**: Show 2-3 consequences per scene. Each consequence gets its own visual: map with highlighted regions, resource icons, trade routes, population data, military comparisons. Use hex_icons for resources (💰oil, 🌽agriculture, 🏭industry, ⚔️military). Use routes for trade paths. Use vignettes for data cards. Use hex_grid for multi-metric comparison when needed.

5. **Scene 6 - Twist + Closing [45-60s]**: Show the unexpected negative consequence. Map with conflict zones (red arrows, protest icons, tension zones). End with the closing question as text overlay on the final transformed map.

**TECHNICAL RULES FOR REMOTION (STRICT):**
- Primary visual type: "map_3d" for ALL scenes. Use "ai_image" ONLY for historical or impossible-to-map concepts.
- Provide REAL GPS coordinates. NEVER use 0.0 for map scenes.
- `camera_zoom`: 3.0-5.0 for continent views, 5.0-8.0 for country/region views.
- `camera_pitch`: 30-50 degrees for 3D perspective.
- `highlight_region`: The country/region to highlight with neon glow. Use real country names.
- `floating_label`: Key data in ALL CAPS. Include population numbers, territory sizes, economic stats.
- `map_pins`: 2-4 pins per scene on key cities, resources, or strategic locations.
- `vignettes`: 2-3 data cards per scene with icon, title, and value (population, area, GDP, resources).
- `camera_path`: 2-3 waypoints per scene for slow cinematic fly-through.
- `map_style`: Use 'dark' for premium contrast political map look, or 'satellite' for realistic terrain.
- `arrow_direction`: MANDATORY for scene 3 (the change) — show the expansion, swap, or movement direction.
- `hex_icons`: Use for resource locations, military bases, cultural centers. 2-4 per consequence scene.
- `routes`: Use for trade routes, migration paths, or expansion arrows. 1-2 per relevant scene.
- `regions`: Use for breaking down a continent into zones. 3-6 per scene for breakdown views.

**OVERLAY FIELDS (sceneOverlay) — SIX TYPES AVAILABLE:**
Each overlay type controls what appears on screen during the scene:

- **`title`** {text, position}: Main headline text. Position can be 'top' or 'center'. Use for the hook question in Scene 1.
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
