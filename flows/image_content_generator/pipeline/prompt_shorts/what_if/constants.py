IDEA_PROMPT_WHAT_IF = """
You are the Lead Producer for "BlowYourMind", a viral channel about mind-blowing geography, geopolitics, and alternate world scenarios.

Generate a HIGH-RETENTION video idea exploring a "What If" geopolitical alternate geography scenario. The best scenarios are counterfactuals that feel plausible and make the viewer rethink how geography shapes our world.

The topic must focus on swapping, merging, moving, enlarging, shrinking, or removing countries/continents in a way that reveals how geography determines global power, trade, culture, and your daily life.

Examples of the vibe:
- "What if India and China switched places?"
- "If Africa was one country..."
- "What if Canada had the population of India?"
- "What if the British Empire never fell?"
- "If America was located in Europe"
- "What if Japan was 10x bigger?"
- "If Brazil ruled all of South America"
- "What if Australia was at the North Pole?"
- "What if Antarctica melted and became a country?"
- "If Germany controlled all of Europe?"

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven "What If" title (e.g., "What if India and China Switched Places? The New World Order").
- `hook`: A scroll-stopping hook (10-15 words) that makes the viewer imagine the impossible (e.g., "What if the two biggest nations on Earth swapped locations overnight?").
- `intrigue_header`: A punchy 2-4 word phrase in ALL CAPS for the top banner (e.g., "SWAPPED WORLDS", "FROZEN EMPIRE", "UNITED CONTINENT").
- `personal_impact`: A sentence explaining how this scenario affects the viewer (e.g., "Your country's alliances would be meaningless overnight.").
- `key_data_stat`: A specific mind-blowing stat with units (e.g., "1.4 billion displaced", "25 trillion GDP", "70% oil control").
- `caption`: A viral social media caption with 5-8 hashtags like #WhatIf #Geography #BlowYourMind #AlternateHistory #MindBlowing.
- `category`: Must be "what_if"
"""

AUDIO_PROMPT_WHAT_IF = """
Use a deep, thoughtful, and cinematic tone — like a documentary narrator revealing an alternate reality.
Pause slightly before each key data point to build anticipation.
Speak clearly and dramatically, as if describing a world that could have been.

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_WHAT_IF = """
You are the Video Producer for "BlowYourMind" and you're writing a script for a vertical short video (1080x1920) exploring a "What If" alternate geography scenario.

The format is a compelling counterfactual exploration with 5-6 scenes: 1 hook + 3-4 geopolitical/economic breakdown points + 1 powerful conclusion.

**VISUAL STYLE (MANDATORY & CONSISTENT):**
Clean modern infographic documentary style. Dark navy or dark backgrounds with subtle grid lines. Clean sans-serif text in white or teal. Map-based visualizations with highlighted regions, arrows, and data labels.

**COLOR PALETTE RULE (CRITICAL — makes each video visually unique):**
- Choose ONE dominant accent color for the entire video (e.g., vibrant teal for "new powers", coral red for "collapsing empires", amber orange for "resource wealth", electric cyan for "Arctic/ice" scenarios).
- EVERY scene must use the same accent color so the video has a cohesive visual identity.

**STRUCTURE (5-6 scenes):**
1. **Scene 1 - The Hook [0-10s]**: Present the "What If" premise dramatically. Show the world map with the transformation happening. Make the viewer instantly imagine the impossible.
2. **Scenes 2-4 - The Breakdown [10-45s]**: 3-4 scenes each revealing a different consequence. One per scene: geopolitical shift, economic impact, military/power realignment. Each scene must use a 3D political map with highlighted regions, map pins, vignette info cards, and data labels.
3. **Final Scene - The Conclusion [45-60s]**: The mind-blowing final thought. Show the transformed world order and leave the viewer with a question or reflection about how geography shapes destiny.

**PER-SCENE FIELDS (ALL MANDATORY):**
- `scene_number`: Sequential number (1 to 5 or 6)
- `visual_type`: Use "map_3d" for all scenes. 3D political map fly-overs with highlighted countries, animated pins, vignette info cards, and floating data labels.
- `image_prompt`: A detailed description of the map visualization for AI image generation fallback. MUST follow this structure exactly:
  "9:16 vertical YouTube Shorts frame, clean modern infographic documentary style, a detailed 3D political map of [REGION/COUNTRIES], [COUNTRY 1] highlighted in vibrant teal with a soft glow outline, [COUNTRY 2] highlighted in bright coral red, [SPECIFIC MAP ELEMENTS like arrows, fact boxes, pins], clean dark navy background with subtle grid lines, minimal and uncluttered, crisp sans-serif text in white, professional documentary aesthetic, no labels on the map itself, volumetric soft lighting from top, ultra clean, photorealistic map textures, premium educational style, 4K"
- `pexels_query`: Leave empty.
- `narration`: Spoken narration in ENGLISH. Cinematic, compelling, educational. MAX 130 words total for the whole script.
- `camera_latitude`: GPS latitude of the camera target. Center the map on the most important country/region for this scene.
- `camera_longitude`: GPS longitude of the camera target.
- `camera_zoom`: Zoom level (3.0 for continents, 5.0 for countries, 7.0 for regions, 10.0 for cities).
- `camera_pitch`: Camera tilt (30-60 degrees for 3D perspective).
- `camera_bearing`: Camera rotation (-180 to 180).
- `highlight_region`: Name of a country or region to highlight with a neon glow (supports real GeoJSON borders). Use the main country/region discussed in this scene.
- `floating_label`: A key data stat or impact number in ALL CAPS displayed as a floating HUD element (e.g., "1.4 BILLION", "$25 TRILLION", "70% CONTROL").
- `map_pins`: Array of 2-3 map pins with `latitude`, `longitude`, `label` (short city/place name), and `value` (optional data). Pin key locations discussed in the narration.
- `vignettes`: Array of 2-3 info vignette cards with `icon` (emoji), `title` (short ALL CAPS label), and `value` (big data number). Show these as sequential fact boxes on the right side.
- `map_style`: Use "satellite" for realistic imagery or "dark" for a cleaner vector look.
- `sfx`: Set to "none" for most scenes.

**COLOR PALETTE RULE (CRITICAL — makes each video visually unique):**
- Choose ONE dominant accent color for the entire video (e.g., vibrant teal for "new powers", coral red for "collapsing empires", amber orange for "resource wealth", electric cyan for "Arctic/ice" scenarios).
- EVERY scene must use the same accent color in their map highlights, pins, and vignettes so the video has a cohesive visual identity.
- Put the accent color in the `image_prompt` as "vibrant [COLOR]" to ensure consistency.

**CRITICAL RULES:**
1. ALL text and narration must be in ENGLISH.
2. Every scene MUST have valid `camera_latitude`, `camera_longitude`, `camera_zoom`, `camera_pitch`, `camera_bearing` pointing to a real geographic location related to the narration.
3. Each scene must look visually DIFFERENT from the previous one (different camera location, different region, different highlighted countries).
4. You MUST output exactly 5-6 scenes. No more, no less.
"""

FOCUS_AREAS_WHAT_IF = [area.strip() for area in [
    "WHAT IF INDIA AND CHINA SWITCHED PLACES? — Swap India and China on the map: India becomes a Pacific superpower bordering Russia and Southeast Asia; China becomes landlocked in the subcontinent with monsoon climate and border disputes.",
    "IF AFRICA WAS ONE COUNTRY... — Merge all 54 African nations into one: the largest population (1.4B) and richest resources on Earth, commanding 30% of minerals and 54 UN seats as a single veto-wielding superpower.",
    "WHAT IF CANADA HAD THE POPULATION OF INDIA? — Give Canada 1.4 billion people: instantly becomes the most powerful country combining US technology, Indian manpower, and Canadian resources — GDP surpasses the US within decades.",
    "WHAT IF THE BRITISH EMPIRE NEVER FELL? — British Empire survives WWII controlling 25% of the globe and 2 billion people: no Cold War superpowers, English as sole global language, Pound replaces Dollar as reserve currency.",
    "IF AMERICA WAS LOCATED IN EUROPE... — Transplant the USA landmass into central Europe: physically crushes France/Germany/Spain, shares a direct land border with Russia (WW3 near-certainty), Mediterranean cut off from Atlantic trade.",
    "WHAT IF JAPAN WAS 10X BIGGER? — Multiply Japan's islands by ten: controls the entire Pacific Ocean as unchallenged superpower, economy dwarfs USA+China combined, becomes rival instead of ally to the United States.",
    "IF BRAZIL RULED ALL OF SOUTH AMERICA — Brazil absorbs all South American nations: controls 20% of world's fresh water and the Amazon, Portuguese replaces Spanish across continent, challenges US dominance in Western Hemisphere.",
    "WHAT IF AUSTRALIA WAS AT THE NORTH POLE? — Australia relocated to the Arctic: ecosystem collapses and unique wildlife goes extinct, but Australia controls the most valuable Arctic shipping routes becoming center of global trade.",
    "WHAT IF THE USSR NEVER COLLAPSED? — Soviet Union survives to 2024: Cold War never ends, technology accelerates (smartphones/internet/Mars colonies decades earlier), China's economic miracle blocked by USSR controlling Central Asia.",
    "WHAT IF ALL MUSLIM COUNTRIES UNITED? — 57 Muslim-majority nations merge into an Islamic Superstate from Morocco to Indonesia: 1.8 billion people, 70% of world's oil reserves, 5 million active soldiers challenging NATO+China simultaneously.",
    "WHAT IF ANTARCTICA MELTED AND BECAME A COUNTRY? — All Antarctic ice melts revealing green habitable land: catastrophic flooding submerges coastal cities displacing 1 billion people, geopolitical scramble for trillions in resources.",
    "IF GERMANY CONTROLLED ALL OF EUROPE — Germany dominates and unifies Europe: German becomes sole language erasing French/Latin dominance, GDP of $25 trillion exceeds USA+China combined, NATO dissolves.",
    "WHAT IF TEXAS BECAME ITS OWN COUNTRY AGAIN? — Texas secedes from the US: becomes 9th largest economy globally, inherits military bases on its territory, US loses strategic southern border and massive oil production.",
    "WHAT IF THE SAHARA DESERT WAS A FRESHWATER OCEAN? — Replace the Sahara with an inland sea: transforms climate across Africa/Europe, new trade routes emerge, coastal cities appear across what was empty desert.",
    "WHAT IF GREENLAND WAS INDEPENDENT AND WEALTHY? — Greenland gains independence and discovers trillions in rare earth minerals: becomes the Arctic Singapore controlling polar trade routes between North America, Europe, and Asia.",
    "WHAT IF THE PANAMA CANAL NEVER EXISTED? — No Panama Canal means ships must go around Cape Horn: Southern Cone nations become global trade powers, US West Coast develops independently, global shipping costs double.",
    "WHAT IF MONGOLIA BECAME A NAVAL POWER? — Give Mongolia access to the Sea of Japan via a narrow corridor: creates a new geopolitical flashpoint between Russia, China, and Japan; landlocked nation transforms into strategic naval player.",
    "WHAT IF THE HIMALAYAS WERE A FLAT PLAIN? — Remove the Himalayan mountain range: monsoon patterns shift drying up India, cold air from Central Asia floods South Asia, India and China share an open border with massive migration.",
    "WHAT IF EVERY ISLAND IN THE PACIFIC MERGED? — All Pacific islands (Indonesia, Philippines, Japan, PNG, NZ, Pacific islands) merge into one supercontinent: a new Pacific superpower controlling both hemispheres and the International Date Line.",
    "WHAT IF THE MEDITERRANEAN SEA DRIED UP? — The Mediterranean becomes a dry salt basin 3km deep: Europe and Africa connected by land, global climate shifts dramatically, new civilizations rise in the salt desert.",
    "WHAT IF SIBERIA WAS A TROPICAL PARADISE? — Siberia shifted to equatorial latitude: Russia's frozen wasteland becomes prime agricultural land, Russia becomes the world's breadbasket, population shifts east transforming global demographics.",
]]
