# Prompt constants for Curiosities Reels

IDEA_PROMPT_STORY = """
Generate an idea for a short video about "Mind-Blowing Curiosities and Bizarre Histories".
The topic must be **EXTREMELY SPECIFIC, CURIOUS AND LITTLE-KNOWN** (insane facts or secrets that almost no one knows about the past or science).
The language must be **VERY CLEAR, DIRECT, AND EASY TO UNDERSTAND** by anyone instantly.
The video must explain the entire concept from beginning to end, with an intriguing hook, a very descriptive and easy-to-digest development, and a **CLOSED CONCLUSION** that resolves the curiosity completely (without leaving the story halfway).
It must be designed for a fast-paced, highly dynamic video, composed of **6 to 8 short scenes** to maintain visual dynamism.
The total narration of ALL scenes combined MUST NOT EXCEED 120 WORDS so it lasts under 60 seconds.
**IMPORTANT: ALL RESPONSES AND SCRIPT GENERATION MUST BE EXCLUSIVELY IN NATIVE, HIGH-RETENTION ENGLISH.**

**MANDATORY VISUAL STYLE:**
If AI images must be generated as backup, apply this style: "{visual_style}"
"""

IMAGE_INTERACTION_PROMPT = "" # Not used for stories right now

AUDIO_PROMPT = """
Use a narrative tone that is educational but highly intriguing and dynamic. Like you are an expert revealing a great ancient secret.

TEXT TO NARRATE:
{audio_text}
"""


SCRIPT_PROMPT = """
Based on the provided IDEA, write a video script for a Reel that lasts MAXIMUM 50 seconds.
Divide the story into **6 to 8 short scenes** (high visual density, fast clip changes).
For each scene you must define:
1. `visual_type`: Choose `"stock_video"` if it is something common that can be recorded in real life (e.g. desert sand, fire, people smiling). Choose `"ai_image"` if it is historical, fantasy, or impossible to capture (e.g. Roman gladiators fighting, ancient Egyptian doctors, a Mayan temple).
2. `pexels_query`: Only if you chose "stock_video", write 1 to 3 keywords IN ENGLISH.
3. `image_prompt`: The detailed description IN ENGLISH (always mandatory as backup).
4. `narration`: What the voiceover will say. **MUST BE IN ENGLISH.**

CRITICAL RULES:
1. **VISUAL CRITERIA:** Be very smart deciding the `visual_type`. For anything that requires seeing armies, clothing of the era, ancient kings or monuments in their splendor, use "ai_image".
2. **STRICT TIME LIMIT:** The total narration of the entire video combined must have **maximum 120 words**. Write concisely, straight to the point, without beating around the bush.
3. **ABSOLUTE CLARITY:** Explain the curiosity in a very simple and understandable way. The viewer must instantly understand the context of the era, what was happening, and why it was done. Avoid confusing metaphors.
4. **COMPLETE STORY:** The explanation must be 100% resolved in the last scene.
5. Scene 1 must be a brutal hook (a very specific question or shocking fact) about the civilization that stops the scroll.
6. The `intrigue_header` must be a persistent title of 3-5 words in UPPERCASE ENGLISH (e.g. "THE ROMAN TAX", "SECRETS OF EGYPT").
7. **CALL TO ACTION (CTA):** In the last scene, include a simple interactive CTA in English (e.g. "Did you know this fact? Tell us in the comments!").
**EVERYTHING MUST BE IN ENGLISH.**
"""
