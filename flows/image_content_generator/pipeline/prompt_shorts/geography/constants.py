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
- `intrigue_header`: A 3-5 word ALL CAPS hook that persists at the top (e.g., 'THE FLYING RIVERS', 'THE BURNING DOOR', 'THE GRAVITY HOLE').
- `hook`: The initial scroll-stopping sentence (10-15 words). Must sound like a secret being revealed.
- `caption`: A deep, educational social media caption explaining the phenomenon. Include 5-8 viral hashtags like #GeographySecrets #MindBlowingFacts #HiddenWorld #HowNatureWorks.
- `category`: Must be "geography"

**CRITICAL: ALL CONTENT MUST BE IN ENGLISH. Topics should be GLOBAL (not limited to Latin America).**
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
1. **Scene 1 - The Hook [0-8s]**: Start with a shocking question or a "most people think X, but nature secretly does Y" statement. Use map_3d with a wide zoom (4.0-5.5) to show the global context.
2. **Scenes 2-5 - The Mechanism [8-40s]**: Fly the camera over the geographical feature. Show mountains, rivers, ocean currents, wind barriers. Use floating labels to display key data. Use arrows to show forces and flows.
3. **Scenes 6-7 - The Reveal [40-50s]**: The mind-blowing conclusion. Show the impact data in the floating HUD. Use ai_image if needed to illustrate a concept that can't be mapped.
4. **Final Scene - The CTA [50-55s]**: End with a paradoxical question that forces re-watching or commenting.

**TECHNICAL RULES FOR REMOTION (STRICT):**
- Each scene must use `visual_type = "map_3d"` for geographic fly-overs. Use `"ai_image"` ONLY for conceptual illustrations (historical, cross-sections, microscopic, or impossible-to-map visuals).
- Provide REAL GPS coordinates using `camera_latitude` and `camera_longitude`. NEVER use 0.0 for map scenes.
- `camera_zoom`: 4.0-7.0 for country/continent views, 8.0-11.0 for specific valleys or features.
- `camera_pitch`: 30-60 degrees for 3D perspective. `camera_bearing`: -180 to 180 for rotation.
- `highlight_region`: One of these neon-highlighted regions — 'Colombia', 'Brazil', 'Peru', 'Mexico', 'Argentina', 'Chile', 'Venezuela', 'Ecuador', 'USA', 'Bolivia', or 'none'.
- `arrow_direction`: Describe an arrow showing force flow (e.g. 'from: Pacific Ocean, to: Andes Mountains' or 'none').
- `floating_label`: Key data/stat in ALL CAPS (e.g. '8,000 MM RAIN', '52M PEOPLE', '6,700 KM LENGTH', '200 MPH WINDS' or 'none').
- `sfx`: Sound effect for immersion — 'ocean_waves', 'heavy_wind', 'rain_and_thunder', 'digital_swoosh', 'jungle_ambient', 'volcanic_rumble' or 'none'.

**NARRATION RULES:**
- Total narration across ALL scenes: MAX 120 WORDS (55 seconds at normal pace).
- Every sentence must deliver a punch of curiosity or data. No filler.
- The final scene must be a CTA question that invites comments (e.g. "If nature can do this, what else is hiding beneath our feet?").

**CRITICAL: ALL TEXT AND NARRATION MUST BE IN ENGLISH.**
"""
