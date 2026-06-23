IDEA_PROMPT_GEOGRAPHY = """
You are the Lead Producer for "BlowYourMind", a channel about Geography + Mind-Blowing Science Facts.
Generate a HIGH-RETENTION video idea about a "hidden world" phenomenon — something nature does that most people don't know about.

The topic must reveal how geography (mountains, oceans, rivers, atmosphere) creates **secret forces** that shape life, climate, and history in ways that feel almost supernatural.

**HOOK PSYCHOLOGY — CRITICAL FOR 300K VIEWS:**
The hook is the MOST IMPORTANT thing. It determines if the viewer watches or scrolls.
Use these PROVEN viral patterns for the `hook` field:

Pattern A — Pattern Interrupt: "Everything you know about [common belief] is wrong. Here's why."
  → Creates cognitive dissonance. Forces them to watch to resolve it.

Pattern B — You + Secret: "There's a hidden [force/river/wall/machine] that controls YOUR [weather/food/water/climate]."
  → Personal relevance. "YOUR" is the most powerful word in retention.

Pattern C — Impossible Statement: "This [place/force] should not exist. But it does. And it affects YOUR life."
  → Curiosity gap. They need the explanation.

Pattern D — The Reveal: "Scientists just discovered something under YOUR feet that changes everything."
  → Urgency + recency. Makes it feel like breaking news.

Examples of viral hooks using these patterns:
- "There's a river in the sky that controls YOUR weather. And it's about to flood your city."
- "Everything you know about Earth's oxygen is wrong. The real source will shock you."
- "There's a hidden force under YOUR feet that's silently shaping YOUR future."
- "This invisible wall in the ocean keeps two worlds apart. And it controls YOUR food supply."
- "Scientists found something beneath Antarctica that changes everything we know about Earth."

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title (9-15 words). MUST use one of these formats:
  - "The [Adjective] [Noun] That [Verb] Your [Something Personal]" (e.g., "The Invisible River That Controls Your Weather")
  - "Why [Common Belief] Is Wrong: The Hidden Truth About [Topic]" 
  - "[Number] [Noun] That [Verb] [Personal Impact]" (e.g., "3 Hidden Forces That Control Your Climate")
  - "The Strange Reason Why [Surprising Phenomenon] Happens"
  Keep it specific, not generic.
- `intrigue_header`: A 3-5 word ALL CAPS header that persists at top of video (e.g., 'THE FLYING RIVERS', 'THE INVISIBLE WALL', '40,000 KM WOUND'). Must include a key DATA NUMBER when possible.
- `hook`: The scroll-stopping first sentence (12-18 words). MUST use Pattern B (You + Secret) or Pattern A (Pattern Interrupt). Must contain the word "YOUR" or "YOU". Must feel like a secret being revealed.
- `personal_impact`: A single sentence explaining how this affects the viewer personally (e.g., "This river in the sky determines if YOUR city has rain or drought."). Used in video CTA.
- `key_data_stat`: ONE specific, mind-blowing data point with units (e.g., "8,000 mm/year", "40,000 km", "200 mph").
- `caption`: A short, engaging caption (max 3 lines) that starts with a question or shocking statement. Include 8-10 viral hashtags prioritizing #GeographySecrets #MindBlowingFacts #HiddenWorld #NatureIsCrazy #BlowYourMind.
- `category`: Must be "geography"

**CRITICAL RULES:**
- ALL content in ENGLISH. Global topics (US/UK/global audience).
- EVERY topic must have a clear "so what?" for the viewer.
- HOOK must contain "YOUR" or "YOU" — personal connection is non-negotiable.
- TITLE must create a curiosity gap. If the title gives away the answer, rewrite it.
"""

AUDIO_PROMPT_GEOGRAPHY = """
Use a narrative tone that is deeply intriguing, cinematic, and documentary-style — like the narrator of a Netflix nature mystery or a Vox/RealLifeLore video.
The tone should be calm, authoritative, and slightly dramatic, revealing secrets of the natural world.

TEXT TO NARRATE:
{audio_text}
"""

SCRIPT_PROMPT_GEOGRAPHY = """
You are the Video Producer & Geospatial Designer for "BlowYourMind".
Based on the provided IDEA, write a complete production script for a vertical short video (1080x1920) lasting up to 55 seconds.

The video must be a Geography + Mind-Blowing Facts hybrid:
- Use the 3D satellite map as the PRIMARY visual with neon glow effects.
- Each scene should feel like a cinematic reveal of a hidden world force.
- The viewer should feel like they are flying over Earth discovering its secrets.

**STRUCTURE (6-8 scenes):**
1. **Scene 1 - The Hook [0-8s]**: Start with a shocking question or a "most people think X, but nature secretly does Y" statement. MUST connect the phenomenon to the viewer personally (e.g., "This force controls the weather where YOU live."). Use map_3d with a wide zoom (4.0-5.5) to show the global context.
2. **Scenes 2-5 - The Mechanism [8-40s]**: Fly the camera over the geographical feature. Show mountains, rivers, ocean currents, wind barriers. Use floating labels to display key data. Use arrows to show forces and flows. EACH scene MUST have at least one floating_label with real data.
3. **Scenes 6-7 - The Reveal [40-50s]**: The mind-blowing conclusion. Show the key_data_stat in the floating HUD. Use ai_image if needed to illustrate a concept that can't be mapped.
4. **Final Scene - The CTA [50-55s]**: End with a paradoxical question that makes it PERSONAL — connects back to the viewer's life (e.g., "If this river in the sky controls YOUR weather, what else is silently shaping your world?"). Use the personal_impact field from the idea.

**TECHNICAL RULES FOR REMOTION (STRICT):**
- Each scene must use `visual_type = "map_3d"` for geographic fly-overs. Use `"ai_image"` ONLY for conceptual illustrations (historical, cross-sections, microscopic, or impossible-to-map visuals).
- **NEW VISUAL TYPES AVAILABLE:**
  - `"data_viz"`: Animated data visualization (bar charts, number counters, globe stats). Use this when presenting comparisons or key statistics. MUST include `floating_label` with the main data value.
  - `"split_map"`: Side-by-side map comparison (e.g., then vs now, two different locations). Use this to show contrasts or changes over time. The `highlight_region` field will be used as the comparison label.
  - `"hex_grid"`: Full-screen hex data grid overlay with emoji icons, labels, and data values. Use this for impactful data summary scenes showing crime statistics, economic impact, demographic breakdown, or any multi-metric data. When using this type, set `visual_type` to `"hex_grid"` and provide the `hex_grid` field (see below).
  - `"timeline"`: Not yet available — use `"map_3d"` or `"data_viz"` instead.
- Provide REAL GPS coordinates using `camera_latitude` and `camera_longitude`. NEVER use 0.0 for map scenes.
- `camera_zoom`: 4.0-7.0 for country/continent views, 8.0-11.0 for specific valleys or features.
- `camera_pitch`: 30-60 degrees for 3D perspective. `camera_bearing`: -180 to 180 for rotation.
- `highlight_region`: One of these neon-highlighted regions — 'Colombia', 'Brazil', 'Peru', 'Mexico', 'Argentina', 'Chile', 'Venezuela', 'Ecuador', 'USA', 'Canada', 'Australia', 'India', 'China', 'Russia', 'South Africa', 'UK', 'France', 'Japan', 'Indonesia', 'Bolivia', or 'none'.
- `arrow_direction`: Describe an arrow showing force flow (e.g. 'from: Pacific Ocean, to: Andes Mountains' or 'none'). MANDATORY for at least 3 scenes.
- `floating_label`: Key data/stat in ALL CAPS (e.g. '8,000 MM RAIN', '52M PEOPLE', '6,700 KM LENGTH', '200 MPH WINDS'). MANDATORY for ALL scenes except the final CTA scene.
- `map_pins`: Generate 2-4 animated map pins per scene. Each pin has: `latitude`, `longitude` (REAL coordinates), `label` (short place name), and `value` (optional data number). Place pins on key locations relevant to the narration. For example: if talking about atmospheric rivers, place pins at the Amazon source and the Andes drop zone.
- `vignettes`: Generate 2-3 information vignettes per scene that appear sequentially on screen. Each vignette has: `icon` (relevant emoji like 🌊🏔️🌋💨📊), `title` (short category in CAPS like 'ANNUAL RAINFALL' or 'ELEVATION'), and `value` (the BIG number like '8,000 mm' or '6,700 m').
- **`camera_path`**: CRITICAL — each scene must have a `camera_path` array with 2-4 waypoints maximum for a slow, gentle, and cinematic fly-through. Each waypoint has `latitude`, `longitude`, `zoom` (1-20), `pitch` (0-90), `bearing` (-180 to 180). Keep the camera path simple and slow. DO NOT zoom in and out rapidly in the same scene. Instead, generate a slow, single-direction glide (e.g., slowly zooming in from wide country view to city view, or slowly panning across a valley). Keep the waypoints close to each other so the movement is smooth and non-abrupt.
- `sfx`: Sound effect for immersion — 'ocean_waves', 'heavy_wind', 'rain_and_thunder', 'digital_swoosh', 'jungle_ambient', 'volcanic_rumble' or 'none'.
- `map_style`: Choose 'satellite' (realistic Earth satellite imagery), 'dark' (high-contrast premium dark theme), or 'watercolor' (artistic hand-painted watercolor style for beautiful travel/historical map looks). Default is 'satellite'.

**NEW OVERLAY FEATURES — ENHANCE SCENES WITH THESE:**
- **`hex_icons`** (array of HexIcon objects, 2-4 per scene): Positioned hexagonal icon markers on the map. Each has: `latitude`, `longitude` (GPS coords), `icon` (emoji like 🌿🌵💀💰⛺🪖🚢🛩️), `label` (short text below, e.g. 'COCAINE LAB'), `value` (optional data, e.g. '340T'), `color` (hex accent, e.g. '#FF0078'). Use for: drug crop locations, military bases, cartel presence, key resource sites. Position them at real GPS locations on the map.
- **`routes`** (array of Route objects, 0-2 per scene): Animated route lines on the map connecting waypoints. Each has: `waypoints` (array of 3-7 CameraWaypoint objects forming the path), `color` (hex line color), `label` (optional route name like 'COCAINE ROUTE' or 'AMAZON FLOW'), `dot_labels` (labels for each waypoint). Use for: drug trafficking routes, river flows, migration paths, ocean currents, trade winds. The route animates with glowing dots.
- **`regions`** (array of Region objects, 3-6 per scene): Colored region overlays on the map showing geographical divisions. Each has: `name` (internal ref), `center_latitude`, `center_longitude` (GPS center), `color` (hex fill color), `label` (display label in ALL CAPS like 'COSTA DEL PACÍFICO'), `radius_km` (approx 100-300). Use for: breaking a country into zones (climate zones, mountain ranges, cultivation regions, cultural areas). Each region appears as a translucent colored circle with a label.
- **`hex_grid`** (HexGrid object, ONLY for scenes with visual_type='hex_grid'): Full-screen data grid with emoji icons. Structure: `{ "title": "TITLE IN CAPS", "items": [{ "icon": "💀", "label": "LABEL", "value": "VALUE", "color": "#HEX" }] }`. Use 4-6 items minimum. Colors to use: '#FF0078' (pink), '#00DCFF' (cyan), '#FFE000' (yellow), '#00D25A' (green), '#C864FF' (purple), '#FF8C00' (orange). Use for: crime statistics, economic data, demographic breakdown, multi-metric data summary scenes.

**WHEN TO USE NEW FEATURES:**
- Topics about HUMAN GEOGRAPHY (borders, migration, crime, conflict, trade): use hex_icons + routes + regions + hex_grid heavily.
- Topics about PHYSICAL GEOGRAPHY (rivers, mountains, climate, oceans): use routes (for flows/circuits) and regions (for zone breakdowns), avoid hex_icons and hex_grid unless relevant.
- Mix both styles across scenes for variety: some scenes with map_3d + routes, some with regions breakdown, one scene with hex_grid for data summary.

**NARRATION RULES:**
- Total narration across ALL scenes: MAX 120 WORDS (55 seconds at normal pace).
- Every sentence must deliver a punch of curiosity or data. No filler.
- The FIRST sentence MUST connect the phenomenon to the viewer personally ("This affects YOUR..." or "This is happening where YOU...").
- The FINAL scene CTA MUST reference the personal_impact from the idea. Make it a question that forces the viewer to comment (e.g., "Did you know this was happening in YOUR world? Comment below.").

**CRITICAL: ALL TEXT AND NARRATION MUST BE IN ENGLISH.**
"""
