from typing import Sequence, Tuple, Type
import random
import os

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    VideoScript,
)
from flows.image_content_generator.pipeline.prompt_shorts.finance.models import FinanceHandler, FinanceIdea
from flows.image_content_generator.pipeline.prompt_shorts.finance import constants as finance_constants

from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator


class PromptManagerShorts(BasePromptManager):
    """Manager for Finance Papercraft short-form video content."""

    CATEGORIES: Sequence[Type[CategoryHandler]] = [FinanceHandler]

    FINANCE_AUDIO_PROMPT: str = finance_constants.AUDIO_PROMPT_FINANCE

    def get_audio_prompt(self, audio_text: str, mode: str = "finance") -> str:
        return self.FINANCE_AUDIO_PROMPT.format(audio_text=audio_text)

    def generate_full_story(
        self, content_gen: GeminiTextGenerator, titles_to_avoid: list[str] = [], extra_avoid: str = "", mode: str = "finance"
    ) -> Tuple[BaseIdea, VideoScript, str]:
        category = "finance"
        idea_model = FinanceIdea
        idea_prompt = finance_constants.IDEA_PROMPT_FINANCE
        script_prompt = finance_constants.SCRIPT_PROMPT_FINANCE
        series_name = "MoneyMysteries Finance History"
        handler_class = FinanceHandler
        focus_areas = finance_constants.FOCUS_AREAS_FINANCE

        # Count parts to avoid repetition
        parts_count = sum(1 for t in titles_to_avoid if series_name in str(t))
        if extra_avoid and series_name in extra_avoid:
            import re
            parts_found = re.findall(rf"{series_name} - Parte (\d+)", extra_avoid)
            if parts_found:
                max_part = max(int(p) for p in parts_found)
                parts_count = max(parts_count, max_part)

        next_part = parts_count + 1
        Messenger.info(f"🎞️ Series: {series_name} | Next Part: {next_part}")

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

        full_idea_prompt = (
            f"{idea_prompt}\n\n"
            f"**MANDATORY CENTRAL TOPIC:** {selected_area}\n"
            f"**THIS CONTENT IS PART {next_part}** of the series '{series_name}'."
        )

        idea_data = content_gen.generate_text(full_idea_prompt + avoid_msg, idea_model)

        Messenger.info(f"\n--- Generating FINANCE Script: {idea_data.title} ---")

        full_script_prompt = (
            script_prompt +
            f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
            f"HOOK: {idea_data.hook}\n"
            f"KEY TAKEAWAY: {idea_data.key_takeaway}\n"
        )
        script = content_gen.generate_text(full_script_prompt, handler_class)

        # Transparency footer
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content has been produced with the support of Artificial Intelligence for educational and entertainment purposes.\n\n"
            "✨ Created by the MoneyMysteries team."
        )

        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)

        return idea_data, script, category
