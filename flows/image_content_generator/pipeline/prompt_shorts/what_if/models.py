from typing import List, Type, ClassVar, Optional
from pydantic import Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.what_if import constants as what_if_constants


class WhatIfIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = what_if_constants.IDEA_PROMPT_WHAT_IF
    primary_country: str = Field(description="The main country or region involved in the scenario (e.g., 'Brazil', 'India', 'Africa').")
    primary_continent: str = Field(description="The continent where the scenario takes place (e.g., 'South America', 'Asia', 'Africa').")
    scenario_type: str = Field(description="Category of the scenario: 'location_swap', 'country_union', 'territorial_expansion', 'population_change', 'natural_change', 'alternate_history', or 'resource_shift'.")
    consequences: List[str] = Field(description="List of 3-5 specific, measurable consequences of the hypothetical change (e.g., population, territory, resources, military power, economy, culture, trade, conflicts, global influence).")
    unexpected_twist: str = Field(description="A single sentence describing a negative consequence, conflict, or difficulty that would arise from the scenario.")
    closing_question: str = Field(description="A short, engaging question that invites viewers to comment and debate (e.g., 'Would this new Brazil become a superpower?').")
    caption: str = Field(description="A deep, engaging social media caption explaining the scenario in English. MUST include 5 to 8 viral hashtags (e.g., #WhatIf #AlternateGeography #MapFacts #Geography).")
    category: str = "what_if"


class WhatIfScene(Scene):
    visual_type: str = Field(default="ai_image", description="Use 'ai_image' for ALL scenes — AI-generated imagery with cinematic text overlays. No 3D maps.")
    image_prompt: str = Field(description="Detailed visual description in ENGLISH for AI image generation. Describe a photorealistic documentary photograph: setting, lighting, colors, composition, mood. NOT a map or diagram. Show real scenes (landscapes, cityscapes, people, infrastructure) that communicate the alternate geography scenario.")
    sfx: str = Field(default="none", description="Sound effect: 'whoosh', 'digital_swoosh', 'heavy_wind', 'ocean_waves', or 'none'.")
    scene_overlay_type: Optional[str] = Field(default=None, description="Overlay type for this scene: 'title', 'big_number', 'year', 'location', 'nightmare', 'trade', or null.")


class WhatIfHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = what_if_constants.SCRIPT_PROMPT_WHAT_IF
    category: str = "what_if"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [WhatIfIdea]
    scenes: List[WhatIfScene] = Field(description="List of 6 scenes for the What If scenario script")
