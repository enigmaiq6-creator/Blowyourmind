from typing import Sequence, Tuple, Type
import random
import os

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    VideoScript,
    ImagePrompt,
)
from flows.image_content_generator.pipeline.prompt_shorts.geography.models import GeographyHandler, GeographyIdea
from flows.image_content_generator.pipeline.prompt_shorts.geography import constants as geo_constants
from flows.image_content_generator.pipeline.prompt_shorts.seven_levels.models import SevenLevelsHandler, SevenLevelsIdea
from flows.image_content_generator.pipeline.prompt_shorts.seven_levels import constants as seven_constants
from flows.image_content_generator.pipeline.prompt_shorts.stories.models import StoryHandler, StoryIdea
from flows.image_content_generator.pipeline.prompt_shorts.stories import constants as story_constants
from flows.image_content_generator.pipeline.prompt_shorts.finance.models import FinanceHandler, FinanceIdea
from flows.image_content_generator.pipeline.prompt_shorts.finance import constants as finance_constants

from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator


class PromptManagerShorts(BasePromptManager):
    """Manager specific to Geography / Mind-Blowing Science Reels."""

    GEOGRAPHY_AUDIO_PROMPT: str = geo_constants.AUDIO_PROMPT_GEOGRAPHY

    CATEGORIES: Sequence[Type[CategoryHandler]] = [GeographyHandler, SevenLevelsHandler, StoryHandler, FinanceHandler]

    def get_audio_prompt(self, audio_text: str, mode: str = "standard") -> str:
        if mode == "seven_levels":
            return seven_constants.AUDIO_PROMPT_SEVEN_LEVELS.format(audio_text=audio_text)
        if mode == "finance":
            return finance_constants.AUDIO_PROMPT_FINANCE.format(audio_text=audio_text)
        if mode == "stories" or mode == "standard":
            return story_constants.AUDIO_PROMPT_STORIES.format(audio_text=audio_text)
        return self.GEOGRAPHY_AUDIO_PROMPT.format(audio_text=audio_text)

    def generate_full_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = "", mode: str = "standard"
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop for the specified mode.
        Supports 'geography', 'seven_levels', and 'stories'/'standard' modes.
        """
        if mode == "seven_levels":
            return self._generate_seven_levels_story(content_gen, titles_to_avoid, extra_avoid)
        if mode == "finance":
            return self._generate_finance_story(content_gen, titles_to_avoid, extra_avoid)
        if mode in ("stories", "standard"):
            return self._generate_stories_story(content_gen, titles_to_avoid, extra_avoid)

        # --- DEFAULT: Geography mode ---
        category = "geography"
        idea_model = GeographyIdea
        idea_prompt = geo_constants.IDEA_PROMPT_GEOGRAPHY
        script_prompt = geo_constants.SCRIPT_PROMPT_GEOGRAPHY
        series_name = "BlowYourMind Geography"
        
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

        focus_areas = [
            "HIDDEN RIVERS IN THE SKY: Atmospheric rivers, flying rivers from the Amazon, and how invisible water flows shape YOUR weather and climate.",
            "THE RING OF FIRE: Earth's 40,000km seismic belt — how tectonic plates build islands, create volcanoes, and reshape the Pacific — and why YOUR flight routes avoid it.",
            "GRAVITY ANOMALIES AND EARTH'S SECRETS: Places where gravity is weaker, magnetic poles shift, or Earth's core does something unexpected that affects YOUR GPS and compass.",
            "EXTREME GEOGRAPHICAL BARRIERS: Mountains, deserts, and oceans that block winds, isolate ecosystems, create otherworldly climates — and determine WHERE you can live.",
            "OCEAN MYSTERIES: Underwater mountains taller than Everest, the place where two oceans meet without mixing, rogue waves that sink YOUR ships, and hidden currents that control YOUR climate.",
            "WEIRD BORDERS AND BIZARRE GEOGRAPHY: Absurd borders that affect YOUR travel, exclaves you didn't know existed, and the strangest maps that explain modern geopolitics.",
            "DESERTS AND ICE: How the Atacama became the driest place, Antarctica's hidden valleys, the expanding Sahara that affects YOUR global food prices.",
            "FORCES THAT SHAPE LIFE: How geography creates biodiversity hotspots, isolated islands evolve unique species, and mountains divide worlds — explaining why YOUR region has certain animals and plants.",
            "HUMANITY AGAINST GEOGRAPHY: Impossible roads, cities built on water, tunnels through mountains, and how we conquer Earth's obstacles — and why YOUR commute exists where it does.",
            "EARTH VS SPACE: How solar winds create auroras visible from YOUR backyard, Earth's magnetic shield that protects YOUR electronics, and what would happen if it flipped tomorrow.",
            "THE HIDDEN OCEAN: Earth's largest mountain range is underwater, there are lakes within the ocean, and YOUR drinking water traveled through this hidden world.",
            "WEATHER WEAPONS OF NATURE: How a volcanic eruption in one country changes YOUR winter, why a Pacific storm becomes YOUR hurricane, and the atmospheric waves you've never heard of.",
            "THE UNDERGROUND WORLD: Cities of microbes miles beneath YOUR feet, the deepest hole humans ever dug, and geological forces brewing under YOUR house.",
            "VANISHING GEOGRAPHY: Islands sinking into the ocean, the fastest-eroding coastline near YOU, and lakes that disappear overnight — what's left when the map changes.",
            "CLIMATE TIME BOMBS: Methane reserves under YOUR permafrost, freshwater glaciers that feed YOUR cities, and ocean currents that keep YOUR country warm — how they're all connected.",
        ]
        selected_area = random.choice(focus_areas)
        Messenger.info(f"🎯 Random Focus Area: {selected_area}")

        avoid_msg = ""
        
        combined_avoid = list(titles_to_avoid)
        if extra_avoid:
            combined_avoid.append(extra_avoid)
            
        if combined_avoid:
            avoid_list_str = "\n".join([str(t) for t in combined_avoid])
            avoid_msg = (
                f"\n\n🚨 **ABSOLUTE NO-REPEAT GOLDEN RULE:** 🚨\n"
                f"It is STRICTLY FORBIDDEN to repeat ANY of these topics, stories, or concepts that were already published:\n"
                f"{avoid_list_str}\n\n"
                f"If you generate a story similar to the previous ones, the system will fail. YOU MUST INVENT A COMPLETELY NEW TOPIC.\n"
            )

        # 3. Dynamic Visual Style Selector
        styles = [
            "Style: Satellite photography style, realistic earth colors, highly detailed 3D terrain, glowing neon cyan and magenta highlights, futuristic HUD overlay, 4K resolution.",
            "Style: Vintage map illustration with modern tech overlay. Sepia map background, bright glowing neon blue and cyan digital interfaces, animated data streams, topographical contour lines.",
            "Style: Stylized infographic map. High-contrast dark blue background, vibrant neon orange and cyan borders, sharp glowing vector lines, data visualization aesthetic.",
            "Style: Cinematic National Geographic 3D terrain flight. Vibrant natural colors, dramatic volumetric lighting, detailed texture, ultra-realistic atmosphere with haze and god rays.",
            "Style: Cyberpunk geography aesthetic. Dark neon-noir map style with magenta/purple grid lines, glowing data nodes, digital rain overlay, high-tech satellite interface."
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
        
        personal_impact = getattr(idea_data, "personal_impact", "This phenomenon affects you more than you realize.")
        key_data = getattr(idea_data, "key_data_stat", "")
        full_script_prompt = (
            script_prompt +
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"**RECOMMENDED VISUAL STYLES FOR IMAGES/MAPS:** {selected_style}\n"
            f"**KEY DATA STAT FOR HUD (MANDATORY - use this in a floating_label):** {key_data}\n"
            f"**PERSONAL IMPACT (MANDATORY - use this for the final CTA):** {personal_impact}\n"
        )
        script = content_gen.generate_text(full_script_prompt, GeographyHandler)

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

    def _generate_stories_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = ""
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop for Standard (Curiosity Reels) mode.
        """
        category = "stories"
        idea_model = StoryIdea
        idea_prompt = story_constants.IDEA_PROMPT_STORIES
        script_prompt = story_constants.SCRIPT_PROMPT_STORIES

        Messenger.info(f"🎯 Generating Standard Curiosity Idea...")

        avoid_msg = ""

        combined_avoid = list(titles_to_avoid)
        if extra_avoid:
            combined_avoid.append(extra_avoid)

        if combined_avoid:
            avoid_list_str = "\n".join([str(t) for t in combined_avoid])
            avoid_msg = (
                f"\n\n🚨 **ABSOLUTE NO-REPEAT GOLDEN RULE:** 🚨\n"
                f"It is STRICTLY FORBIDDEN to repeat ANY of these topics, stories, or concepts that were already published:\n"
                f"{avoid_list_str}\n\n"
                f"If you generate a story similar to the previous ones, the system will fail. YOU MUST INVENT A COMPLETELY NEW TOPIC.\n"
            )

        # Select a random focus area
        selected_area = random.choice(story_constants.FOCUS_AREAS_STORIES)
        Messenger.info(f"🎯 Random Focus Area: {selected_area}")

        # Visual styles for Standard mode
        styles = [
            "Style: Hyper-realistic cinematic photography, dark moody colors, dramatic volumetric lighting, National Geographic documentary quality, 4K resolution.",
            "Style: Vintage illustration on aged parchment, warm sepia tones, hand-drawn aesthetic, historical engraving style.",
            "Style: Dark digital art with neon accents, high contrast, cyber-noir aesthetic, glowing highlights, modern infographic style.",
            "Style: Surreal fantasy realism with cosmic colors, ethereal lighting, dreamlike quality, bioluminescent accents.",
            "Style: Clean modern documentary style, bright vibrant colors, sharp focus, educational channel aesthetic, 4K resolution.",
        ]
        selected_style = random.choice(styles)
        Messenger.info(f"🎨 Selected Visual Style: {selected_style}")

        # Inject style, focus area, and avoid into idea prompt
        full_idea_prompt = (
            f"{idea_prompt}\n\n"
            f"**MANDATORY CENTRAL TOPIC:** {selected_area}\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )

        idea_data = content_gen.generate_text(
            full_idea_prompt + avoid_msg,
            idea_model
        )

        # Generate the script
        Messenger.info(f"\n--- Generating Standard Script: {idea_data.title} ---")

        full_script_prompt = (
            script_prompt +
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"**HOOK:** {idea_data.hook}\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )
        script = content_gen.generate_text(full_script_prompt, StoryHandler)

        # --- Transparency footer ---
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content has been produced with the support of Artificial Intelligence for educational and entertainment purposes.\n\n"
            "✨ Created by the BlowYourMind team."
        )

        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)
        elif "hook" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "hook", "")) + transparency_footer
            setattr(idea_data, "hook", new_val)

        return idea_data, script, category

    def _generate_seven_levels_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = ""
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop for 7 Levels (English) mode.
        """
        category = "seven_levels"
        idea_model = SevenLevelsIdea
        idea_prompt = seven_constants.IDEA_PROMPT_SEVEN_LEVELS
        script_prompt = seven_constants.SCRIPT_PROMPT_SEVEN_LEVELS

        Messenger.info(f"🎯 Generating 7 Levels Idea...")

        avoid_msg = ""

        combined_avoid = list(titles_to_avoid)
        if extra_avoid:
            combined_avoid.append(extra_avoid)

        if combined_avoid:
            avoid_list_str = "\n".join([str(t) for t in combined_avoid])
            avoid_msg = (
                f"\n\n🚨 **ABSOLUTE NO-REPEAT GOLDEN RULE:** 🚨\n"
                f"It is STRICTLY FORBIDDEN to repeat ANY of these topics, stories, or concepts that were already published:\n"
                f"{avoid_list_str}\n\n"
                f"If you generate a story similar to the previous ones, the system will fail. YOU MUST INVENT A COMPLETELY NEW TOPIC.\n"
            )

        # Select a random focus area
        selected_area = random.choice(seven_constants.FOCUS_AREAS_SEVEN_LEVELS)
        Messenger.info(f"🎯 Random Focus Area: {selected_area}")

        # Cinematic visual styles for 7 Levels
        styles = [
            "Style: Hyper-realistic cinematic photography, dark moody colors, dramatic volumetric lighting, deep shadows, National Geographic documentary quality, 4K resolution.",
            "Style: Dark digital art with neon accents, high contrast, cyber-noir aesthetic, glowing highlights on dark backgrounds, cinematic depth of field.",
            "Style: Vintage documentary aesthetic, warm sepia tones, grainy texture, historical photograph quality, dramatic chiaroscuro lighting.",
            "Style: Surreal fantasy realism with cosmic colors, ethereal lighting, otherworldly atmosphere, bioluminescent accents, dreamlike quality.",
            "Style: Dark documentary style, desaturated colors with selective color pops, high contrast shadows, gritty realistic textures, true crime documentary aesthetic.",
        ]
        selected_style = random.choice(styles)
        Messenger.info(f"🎨 Selected Visual Style: {selected_style}")

        # Inject style and avoid message into idea prompt
        full_idea_prompt = (
            f"{idea_prompt}\n\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )

        idea_data = content_gen.generate_text(
            full_idea_prompt + avoid_msg,
            idea_model
        )

        # 4. Generate the script
        Messenger.info(f"\n--- Generating 7 Levels Script: {idea_data.title} ---")

        personal_impact = getattr(idea_data, "personal_impact", "This will change how you see your world.")
        key_data = getattr(idea_data, "key_data_stat", "")
        full_script_prompt = (
            script_prompt +
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"**INTRIGUE HEADER:** {getattr(idea_data, 'intrigue_header', '')}\n"
            f"**KEY DATA STAT:** {key_data}\n"
            f"**PERSONAL IMPACT (use for final CTA):** {personal_impact}\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )
        script = content_gen.generate_text(full_script_prompt, SevenLevelsHandler)

        # --- Transparency footer ---
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content has been produced with the support of Artificial Intelligence for educational and entertainment purposes.\n\n"
            "✨ Created by the BlowYourMind team."
        )

        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)
        elif "hook" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "hook", "")) + transparency_footer
            setattr(idea_data, "hook", new_val)

        return idea_data, script, category

    def _generate_finance_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = ""
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop for Finance mode.
        """
        category = "finance"
        idea_model = FinanceIdea
        idea_prompt = finance_constants.IDEA_PROMPT_FINANCE
        script_prompt = finance_constants.SCRIPT_PROMPT_FINANCE

        Messenger.info(f"🎯 Generating Finance Idea...")

        avoid_msg = ""

        combined_avoid = list(titles_to_avoid)
        if extra_avoid:
            combined_avoid.append(extra_avoid)

        if combined_avoid:
            avoid_list_str = "\n".join([str(t) for t in combined_avoid])
            avoid_msg = (
                f"\n\n🚨 **ABSOLUTE NO-REPEAT GOLDEN RULE:** 🚨\n"
                f"It is STRICTLY FORBIDDEN to repeat ANY of these topics, stories, or concepts that were already published:\n"
                f"{avoid_list_str}\n\n"
                f"If you generate a story similar to the previous ones, the system will fail. YOU MUST INVENT A COMPLETELY NEW TOPIC.\n"
            )

        # Select focus area sequentially without repeating
        selected_area = None
        for area in finance_constants.FOCUS_AREAS_FINANCE:
            # Clean up prefix key for check (e.g. "THE DEBT SNOWBALL TRICK" -> "debt snowball")
            area_title = area.split(":")[0].strip()
            area_key = area_title.replace("THE ", "").replace("TRICK", "").replace("SECRETS", "").replace("TRAP", "").replace("LOOPS", "").replace("REVOLUTION", "").strip().lower()
            
            already_used = False
            for title in combined_avoid:
                if area_key in title.lower():
                    already_used = True
                    break
            
            if not already_used:
                selected_area = area
                break

        if not selected_area:
            selected_area = random.choice(finance_constants.FOCUS_AREAS_FINANCE)
            Messenger.info(f"🎯 Focus Area (Fallback Random): {selected_area}")
        else:
            Messenger.info(f"🎯 Focus Area (Sequential Queue): {selected_area}")

        # Visual styles for Finance mode (exclusively 2D Flat Cartoon)
        styles = [
            "Style: Flat 2D vector cartoon illustration, bold outlines, simple geometric shapes, clean minimal style, pastel color background.",
            "Style: Webcomic illustration style, bold black ink outlines, solid flat color fills, simple cartoon shading, modern financial infographic concept.",
            "Style: Flat corporate Memphis vector art, clean sharp paths, vibrant harmonious pastel color palette, geometric cartoon character."
        ]
        selected_style = random.choice(styles)
        Messenger.info(f"🎨 Selected Visual Style: {selected_style}")

        # Inject style, focus area, and avoid into idea prompt
        full_idea_prompt = (
            f"{idea_prompt}\n\n"
            f"**MANDATORY CENTRAL TOPIC:** {selected_area}\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )

        idea_data = content_gen.generate_text(
            full_idea_prompt + avoid_msg,
            idea_model
        )

        # Generate the script
        Messenger.info(f"\n--- Generating Finance Script: {idea_data.title} ---")

        personal_impact = getattr(idea_data, "personal_impact", "This phenomenon affects your wallet more than you realize.")
        key_data = getattr(idea_data, "key_data_stat", "")

        full_script_prompt = (
            script_prompt +
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"**HOOK:** {idea_data.hook}\n"
            f"**INTRIGUE HEADER:** {getattr(idea_data, 'intrigue_header', '')}\n"
            f"**KEY DATA STAT:** {key_data}\n"
            f"**PERSONAL IMPACT (use for final CTA):** {personal_impact}\n"
            f"**RECOMMENDED VISUAL STYLE:** {selected_style}\n"
        )
        script = content_gen.generate_text(full_script_prompt, FinanceHandler)

        # --- Transparency footer ---
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content has been produced with the support of Artificial Intelligence for educational and entertainment purposes.\n\n"
            "✨ Created by the BlowYourMind team."
        )

        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)
        elif "hook" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "hook", "")) + transparency_footer
            setattr(idea_data, "hook", new_val)

        return idea_data, script, category
