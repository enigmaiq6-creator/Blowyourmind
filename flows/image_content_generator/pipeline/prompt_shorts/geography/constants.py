IDEA_PROMPT_GEOGRAPHY = """
You are the Lead Producer for "BlowYourMind", a channel about Geography + Mind-Blowing Science Facts.
Generate a HIGH-RETENTION video idea about a "hidden world" phenomenon — something nature does that most people don't know about.

The topic must reveal how geography (mountains, oceans, rivers, atmosphere) creates **secret forces** that shape life, climate, and history in ways that feel almost supernatural.

Examples of the vibe:
- "The Flying Rivers of the Amazon — invisible waterways in the sky that create rainforests thousands of miles away."
- "The Antarctic Ice Wall — why no one can cross certain ocean coordinates."
- "The Pacific Ring of Fire — Earth's 40,000km wound that builds and destroys continents."
- "The Gravity Anomaly of Hudson Bay — where you literally weigh less than anywhere else on Earth."
- "The Door to Hell — a crater that has been burning for 50 years."
- "The Place Where Two Oceans Meet But Never Mix."

**MANDATORY OUTPUT FIELDS (ALL IN ENGLISH):**
- `title`: An SEO-optimized, curiosity-driven title for the video.
- `intrigue_header`: A 3-5 word ALL CAPS hook that persists at the top (e.g., 'THE FLYING RIVERS', 'THE BURNING DOOR', 'THE GRAVITY HOLE'). Must include a key DATA NUMBER in the header when possible (e.g., '40,000 KM WOUND', '8,000 MM RAIN').
- `hook`: The initial scroll-stopping sentence (10-15 words). Must sound like a secret being revealed that DIRECTLY affects the viewer's world.
- `personal_impact`: A single sentence explaining how this phenomenon affects the viewer personally (e.g., "This river in the sky determines if YOUR city has rain or drought."). This will be used in the video CTA.
- `key_data_stat`: ONE specific, mind-blowing data point in numeric format with units (e.g., "8,000 mm/year", "40,000 km", "200 mph"). This will be displayed as the floating HUD label.
- `caption`: A deep, educational social media caption explaining the phenomenon. Include 5-8 viral hashtags like #GeographySecrets #MindBlowingFacts #HiddenWorld #HowNatureWorks.
- `category`: Must be "geography"

**CRITICAL: ALL CONTENT MUST BE IN ENGLISH. Topics should be GLOBAL (not limited to Latin America). Choose topics that resonate with a US/UK/global audience.**

**PERSONAL CONNECTION RULE:** Every topic MUST have a clear "so what?" for the viewer. If you can't explain how it affects people's daily lives, pick a different topic.
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
- Provide REAL GPS coordinates using `camera_latitude` and `camera_longitude`. NEVER use 0.0 for map scenes.
- `camera_zoom`: 4.0-7.0 for country/continent views, 8.0-11.0 for specific valleys or features.
- `camera_pitch`: 30-60 degrees for 3D perspective. `camera_bearing`: -180 to 180 for rotation.
- `highlight_region`: One of these neon-highlighted regions — 'Colombia', 'Brazil', 'Peru', 'Mexico', 'Argentina', 'Chile', 'Venezuela', 'Ecuador', 'USA', 'Canada', 'Australia', 'India', 'China', 'Russia', 'South Africa', 'UK', 'France', 'Japan', 'Indonesia', 'Bolivia', or 'none'.
- `arrow_direction`: Describe an arrow showing force flow (e.g. 'from: Pacific Ocean, to: Andes Mountains' or 'none'). MANDATORY for at least 3 scenes.
- `floating_label`: Key data/stat in ALL CAPS (e.g. '8,000 MM RAIN', '52M PEOPLE', '6,700 KM LENGTH', '200 MPH WINDS'). MANDATORY for ALL scenes except the final CTA scene.
- `map_pins`: Generate 2-4 animated map pins per scene. Each pin has: `latitude`, `longitude` (REAL coordinates), `label` (short place name), and `value` (optional data number). Place pins on key locations relevant to the narration. For example: if talking about atmospheric rivers, place pins at the Amazon source and the Andes drop zone.
- `vignettes`: Generate 2-3 information vignettes per scene that appear sequentially on screen. Each vignette has: `icon` (relevant emoji like 🌊🏔️🌋💨📊), `title` (short category in CAPS like 'ANNUAL RAINFALL' or 'ELEVATION'), and `value` (the BIG number like '8,000 mm' or '6,700 m').
- **`camera_path`**: CRITICAL — each scene must have a `camera_path` array with 3-7 waypoints for a cinematic fly-through. Each waypoint has `latitude`, `longitude`, `zoom` (1-20), `pitch` (0-90), `bearing` (-180 to 180). The camera smoothly flies through these points during the scene. ALWAYS start wide (zoom 4-6), fly IN to the specific location (zoom 10-14 for cities, 8-11 for valleys/features), then fly back OUT to wide again. Example pattern: [wide over country → zoom to region → extreme close-up → back to region → back to wide country]. This creates dramatic "Google Earth" cinematic transitions.
- `sfx`: Sound effect for immersion — 'ocean_waves', 'heavy_wind', 'rain_and_thunder', 'digital_swoosh', 'jungle_ambient', 'volcanic_rumble' or 'none'.

**NARRATION RULES:**
- Total narration across ALL scenes: MAX 120 WORDS (55 seconds at normal pace).
- Every sentence must deliver a punch of curiosity or data. No filler.
- The FIRST sentence MUST connect the phenomenon to the viewer personally ("This affects YOUR..." or "This is happening where YOU...").
- The FINAL scene CTA MUST reference the personal_impact from the idea. Make it a question that forces the viewer to comment (e.g., "Did you know this was happening in YOUR world? Comment below.").

**CRITICAL: ALL TEXT AND NARRATION MUST BE IN ENGLISH.**
"""
