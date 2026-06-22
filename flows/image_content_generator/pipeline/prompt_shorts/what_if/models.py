from typing import ClassVar, List, Type

from pydantic import Field

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.what_if import constants as what_if_constants


class WhatIfIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = what_if_constants.IDEA_PROMPT_WHAT_IF
    intrigue_header: str = Field(description="A punchy 2-4 word phrase in ALL CAPS that hooks the viewer (e.g., 'SWAPPED WORLDS', 'FROZEN EMPIRE', 'UNITED CONTINENT').")
    personal_impact: str = Field(description="A single sentence explaining how this alternate geography would affect the viewer's life or world (e.g., 'Your country's borders would disappear overnight.').")
    key_data_stat: str = Field(description="ONE specific, mind-blowing data point in numeric format with units for the floating HUD label (e.g., '1.4 billion displaced', '$25 trillion GDP', '70% oil control').")
    caption: str = Field(description="A highly viral, educational social media caption (Facebook/Instagram) in English about this alternate geography scenario. Include 5-8 hashtags like #WhatIf #Geography #BlowYourMind #AlternateHistory #MindBlowing.")
    category: str = "what_if"


class WhatIfScene(Scene):
    pass


class WhatIfHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = what_if_constants.SCRIPT_PROMPT_WHAT_IF
    category: str = "what_if"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [WhatIfIdea]
    scenes: List[WhatIfScene] = Field(description="List of exactly 5-6 scenes: 1 hook intro + 3-4 geopolitical breakdowns + 1 powerful conclusion/CTA.")
