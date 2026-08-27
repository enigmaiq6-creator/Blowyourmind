from typing import Sequence, Tuple, Type, List, Optional
import random
import os
import re

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    VideoScript,
)
from flows.image_content_generator.pipeline.prompt_shorts.finance.models import FinanceHandler, FinanceIdea
from flows.image_content_generator.pipeline.prompt_shorts.finance import constants as finance_constants
from flows.image_content_generator.pipeline.prompt_shorts.fact_split.models import FactSplitHandler, FactSplitIdea
from flows.image_content_generator.pipeline.prompt_shorts.fact_split import constants as fact_split_constants

from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator


class PromptManagerShorts(BasePromptManager):
    """
    Manager omnicanal para contenido corto viral en BlowYourMind.
    Soporta múltiples modos (finance, fact_split, mind_blowing) y 7 estilos visuales rotativos.
    """

    CATEGORIES: Sequence[Type[CategoryHandler]] = [FinanceHandler, FactSplitHandler]

    VOICE_NAME: str = "en-US-Journey-D"

    def get_audio_prompt(self, audio_text: str, mode: str = "finance") -> str:
        if mode == "fact_split":
            return fact_split_constants.AUDIO_PROMPT_FACT_SPLIT.format(audio_text=audio_text)
        return finance_constants.AUDIO_PROMPT_FINANCE.format(audio_text=audio_text)

    def generate_full_story(
        self,
        content_gen: GeminiTextGenerator,
        titles_to_avoid: list[str] = [],
        extra_avoid: str = "",
        mode: str = "finance"
    ) -> Tuple[BaseIdea, VideoScript, str]:
        
        # 1. Normalización de Modo
        mode_clean = mode.lower().strip() if mode else "finance"

        # 2. Selección de Estilo Visual Dinámico (Evita repetición estética)
        selected_style = random.choice(finance_constants.VISUAL_STYLES)
        Messenger.info(f"🎨 [Visual Director] Estilo Seleccionado: '{selected_style['name']}'")

        # 3. Configuración según el modo
        if mode_clean == "fact_split":
            category = "fact_split"
            idea_model = FactSplitIdea
            idea_prompt_base = fact_split_constants.IDEA_PROMPT_FACT_SPLIT
            script_prompt_base = fact_split_constants.SCRIPT_PROMPT_FACT_SPLIT
            series_name = "BlowYourMind Fact Split"
            handler_class = FactSplitHandler
            focus_areas = fact_split_constants.FOCUS_AREAS_FACT_SPLIT
        else:
            category = "finance"
            idea_model = FinanceIdea
            idea_prompt_base = finance_constants.IDEA_PROMPT_FINANCE
            script_prompt_base = finance_constants.SCRIPT_PROMPT_FINANCE.format(
                visual_style_instruction=f"CRITICAL: Append this visual style suffix to EVERY image_prompt: \"{selected_style['suffix']}\""
            )
            series_name = "BlowYourMind Money & Power"
            handler_class = FinanceHandler
            focus_areas = finance_constants.FOCUS_AREAS_FINANCE

        # 4. Anti-repetición estricta: Filtrar temas ya usados
        used_text_lower = " ".join([str(t).lower() for t in titles_to_avoid] + [extra_avoid.lower()])
        available_areas = [area for area in focus_areas if not any(w.lower() in used_text_lower for w in area.split()[:3])]
        if not available_areas:
            available_areas = focus_areas

        selected_area = random.choice(available_areas)
        Messenger.info(f"🎯 [Topic Focus] Temática Seleccionada: '{selected_area}' ({mode_clean.upper()})")

        # 5. Construcción de lista de prohibición estricta
        combined_avoid = [str(t).strip() for t in titles_to_avoid if str(t).strip()]
        if extra_avoid:
            combined_avoid.append(extra_avoid)

        # Enviar los 80 temas más recientes para no sobrecargar el prompt
        recent_avoid = list(dict.fromkeys(combined_avoid))[-80:]
        avoid_list_str = "\n- ".join(recent_avoid) if recent_avoid else "None"

        avoid_msg = (
            f"\n\n🚨 **CRITICAL ANTI-REPETITION MANDATE:** 🚨\n"
            f"You MUST NOT repeat, borrow or create concepts similar to any of these previously published stories/titles:\n"
            f"- {avoid_list_str}\n\n"
            f"Create a 100% BRAND NEW, UNIQUE, and UNEXPLORED narrative.\n"
        )

        full_idea_prompt = (
            f"{idea_prompt_base}\n\n"
            f"**MANDATORY CENTRAL TOPIC/INSPIRATION:** {selected_area}\n"
            f"**SERIES:** '{series_name}'"
        )

        idea_data = content_gen.generate_text(full_idea_prompt + avoid_msg, idea_model)
        Messenger.info(f"\n--- [Idea Generada] '{idea_data.title}' ({category}) ---")

        # 6. Generación del Guion Técnico
        if mode_clean == "fact_split":
            full_script_prompt = (
                script_prompt_base +
                f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
                f"HOOK: {idea_data.hook}\n"
                f"SUBJECT A: {getattr(idea_data, 'sujeto_a', '')}\n"
                f"SUBJECT B: {getattr(idea_data, 'sujeto_b', '')}\n"
                f"CONTRAST KEY: {getattr(idea_data, 'contrast_key', '')}\n"
            )
        else:
            full_script_prompt = (
                script_prompt_base +
                f"\n\nIDEA TO DEVELOP: {idea_data.title}\n"
                f"HOOK: {idea_data.hook}\n"
                f"KEY TAKEAWAY: {idea_data.key_takeaway}\n"
            )

        script = content_gen.generate_text(full_script_prompt, handler_class)

        # 7. Asegurar estilo visual en cada escena si no lo incluyó
        if mode_clean != "fact_split":
            for sc in script.scenes:
                if hasattr(sc, "image_prompt") and sc.image_prompt:
                    if selected_style["suffix"].strip() not in sc.image_prompt:
                        sc.image_prompt = sc.image_prompt.rstrip(". ") + selected_style["suffix"]

        # 8. Pie de página de transparencia
        transparency_footer = (
            "\n\n---\n"
            "💡 **Transparency**: This content was produced with AI support for educational and entertainment purposes.\n\n"
            "✨ Produced by the BlowYourMind team."
        )

        if "caption" in idea_data.model_fields:
            new_val = str(getattr(idea_data, "caption", "")) + transparency_footer
            setattr(idea_data, "caption", new_val)

        return idea_data, script, category
