from typing import Sequence, Tuple, Type, Optional
import random
import os

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    VideoScript,
    ImagePrompt,
)
from flows.image_content_generator.pipeline.prompt_shorts.finances import (
    constants as finance_constants,
)
from flows.image_content_generator.pipeline.prompt_shorts.stories import constants as story_constants
from flows.image_content_generator.pipeline.prompt_shorts.stories.models import StoryHandler, StoryIdea
try:
    from flows.image_content_generator.pipeline.prompt_shorts.geography.models import GeographyHandler, GeographyIdea
    from flows.image_content_generator.pipeline.prompt_shorts.geography import constants as geo_constants
    HAS_GEOGRAPHY = True
except ImportError:
    GeographyHandler = None
    GeographyIdea = None
    geo_constants = None
    HAS_GEOGRAPHY = False

from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator


class PromptManagerShorts(BasePromptManager):
    """Manager specific to Viral Content (Videos, Riddles, and Stories)."""

    AUDIO_PROMPT: str = story_constants.AUDIO_PROMPT # Defaulting to story audio

    CATEGORIES: Sequence[Type[CategoryHandler]] = [StoryHandler] + ([GeographyHandler] if (HAS_GEOGRAPHY and GeographyHandler) else [])

    def generate_full_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = "", mode: str = "standard"
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the viral generation loop for Story/Geography Reels.
        """
        if mode == "geography":
            if not HAS_GEOGRAPHY or geo_constants is None or GeographyIdea is None:
                raise ValueError("Geography mode is not available in this environment (local-only module missing).")
            category = "geography"
            idea_model = GeographyIdea
            idea_prompt = geo_constants.IDEA_PROMPT_GEOGRAPHY
            script_prompt = geo_constants.SCRIPT_PROMPT_GEOGRAPHY
            series_name = "BlowYourMind Geography"
        else:
            category = "stories"
            idea_model = StoryIdea
            idea_prompt = story_constants.IDEA_PROMPT_STORY
            script_prompt = story_constants.SCRIPT_PROMPT
            series_name = "BlowYourMind"
        
        # Scan both the list and the extra_avoid string for the series name
        parts_count = sum(1 for t in titles_to_avoid if series_name in str(t))
        if extra_avoid and series_name in extra_avoid:
            import re
            parts_found = re.findall(rf"{series_name} - Parte (\d+)", extra_avoid)
            if parts_found:
                max_part = max(int(p) for p in parts_found)
                parts_count = max(parts_count, max_part)

        next_part = parts_count + 1
        Messenger.info(f"🎞️ Series: {series_name} | Next Part: {next_part}")

        if mode == "geography":
            focus_areas = [
                "EXTREME GEOGRAPHICAL BARRIERS: Mountains, deserts, or oceans that block winds, isolate countries, and create otherworldly climates.",
                "COLOSSAL RIVERS AND BASINS: Hydrological mysteries, subterranean rivers, flying rivers, and the impact of basins like the Amazon.",
                "RAPID RAINFALL ZONES AND EXTREME CLIMATES: Why it rains so much in the South American Pacific or how the Atacama Desert became bone-dry.",
                "BIODIVERSITY AND MOUNTAIN RANGES: How the three cordilleras of the Andes divide a single country into isolated ecological worlds.",
                "BIZARRE HISTORICAL GEOGRAPHY: Absurd borders formed by capricious rivers or impassable mountains."
            ]
        else:
            focus_areas = [
                "ANCIENT EGYPT CURIOSITIES: Bizarre secrets, strange medicine (like using honey as an antibiotic), police baboons, or protective makeup.",
                "ROMAN EMPIRE MYSTERIES: Curious and little-known habits like the urine tax, ammonia laundry, or the use of gladiator blood.",
                "ANCIENT GREECE SECRETS: Extreme life in Sparta, the mysterious Antikythera mechanism (the first computer), or weird rituals.",
                "MAYAN AND AZTEC CURIOSITIES: Chocolate as currency, decorative jade dentistry, or the sacred ball game.",
                "MESOPOTAMIA AND BABYLON MYSTERIES: Bizarre laws from the Code of Hammurabi, the oldest beer recipe, or forgotten inventions.",
                "ANCIENT CHINESE EMPIRE CURIOSITIES: Secrets of the terracotta warriors, magical uses of gunpowder, or peculiar inventions.",
                "ANCIENT JAPAN AND SAMURAI SECRETS: Unusual daily customs, the real origin of ninjas, and psychological warfare tactics.",
                "VIKING CULTURE CURIOSITIES: Peculiar hygiene methods, bleaching hair with lye, or how they used urine to make fire.",
                "ANCIENT INDIA MYSTERIES: Pioneering plastic surgeries of Sushruta, ancient Ayurvedic medicine, or war elephant tactics.",
                "INCA EMPIRE AND ANDEAN CULTURE SECRETS: The quipu knot system, the incredibly fast chasqui messengers, or Andean mummification techniques.",
                "HEALTH BODY SECRETS: Mind-blowing facts about the human body, bizarre medical mysteries, health myths debunked, or hidden biological superpowers.",
                "HEALTH BRAIN SCIENCE: How the brain really works, memory manipulation secrets, sleep mysteries, or the science of habits and addiction.",
                "RELATIONSHIPS ATTRACTION SCIENCE: The psychology of love, chemical reactions behind falling in love, pheromones, or what really creates attraction.",
                "RELATIONSHIPS SOCIAL DYNAMICS: Hidden rules of social behavior, body language secrets, persuasion techniques, or the science of first impressions.",
                "MONEY PSYCHOLOGY: Cognitive biases that keep people poor, the psychology of spending, how rich people think differently, or hidden money traps.",
                "MONEY ECONOMIC CURIOSITIES: Bizarre historical economic facts, how money really works, hidden inflation mechanisms, or surprising wealth statistics."
            ]
        selected_area = random.choice(focus_areas)
        Messenger.info(f"🎯 Random Focus Area: {selected_area}")

        avoid_msg = ""
        banned_words = "Poor, Rich, Mentality, Scarcity, Abundance, Mindset, Millionaire"
        
        combined_avoid = list(titles_to_avoid)
        if extra_avoid:
            # extra_avoid already comes as a formatted string from get_recent_topics
            combined_avoid.append(extra_avoid)
            
        if combined_avoid:
            avoid_list_str = "\n".join([str(t) for t in combined_avoid])
            avoid_msg = (
                f"\n\n🚨 **ABSOLUTE NO-REPEAT GOLDEN RULE:** 🚨\n"
                f"It is STRICTLY FORBIDDEN to repeat ANY of these topics, stories, or concepts that were already published:\n"
                f"{avoid_list_str}\n\n"
                f"If you generate a story similar to the previous ones, the system will fail. YOU MUST INVENT A COMPLETELY NEW TOPIC.\n"
                f"🚫 **BANNED WORDS (DO NOT USE):** {banned_words}"
            )

        # 3. Dynamic Visual Style Selector
        if mode == "geography":
            styles = [
                "Style: Satellite photography style, realistic earth colors, highly detailed 3D terrain, glowing neon highlights.",
                "Style: Vintage map illustration with modern tech overlay. Sepia map background, bright glowing neon blue and cyan highlights, digital interfaces.",
                "Style: Stylized infographic map. High-contrast dark blue background, vibrant neon borders, sharp glowing vector lines.",
                "Style: Cinematic National Geographic 3D terrain flight. Vibrant natural colors, dramatic lighting, detailed texture."
            ]
        else:
            styles = [
                "Style: Cinematic Dark Documentary. Volumetric lighting, dramatic chiaroscuro (heavy shadows), moody atmosphere, teal and orange or deep amber color grading. Macro photography or wide-angle cinematic shots, 85mm lens, shallow depth of field (blurred background), sharp textures. 8k resolution, hyper-realistic, unreal engine 5 render style, highly detailed skin/material textures."
            ]
        selected_style = random.choice(styles)
        
        Messenger.info(f"🎨 Selected Visual Style: {selected_style}")

        # Inject the selected style and focus area into the prompt

        full_idea_prompt = (
            f"{idea_prompt.format(visual_style=selected_style)}\n\n"
            f"**MANDATORY CENTRAL TOPIC:** {selected_area}\n"
            f"**THIS CONTENT IS PART {next_part}** of the series '{series_name}'."
        )
        
        idea_data = content_gen.generate_text(
            full_idea_prompt + avoid_msg, 
            idea_model
        )

        # 4. Viral Script / Content Generation
        Messenger.info(f"\n--- Generating Viral {category.upper()} Content: {idea_data.title} ---")
        
        full_script_prompt = (
            script_prompt + 
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"**RECOMMENDED VISUAL STYLES FOR IMAGES/MAPS:** {selected_style}\n"
        )
        script = content_gen.generate_text(full_script_prompt, GeographyHandler if mode == "geography" else VideoScript)

        # --- BAN SHIELD: Append transparency footer to caption/hook ---
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content has been produced with the support of Artificial Intelligence for educational and entertainment purposes.\n\n"
            "✨ Created by the BlowYourMind team."
        )
        
        # Inject transparency footer into caption or hook field
        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)
        elif "hook" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "hook", "")) + transparency_footer
            setattr(idea_data, "hook", new_val)

        return idea_data, script, category
