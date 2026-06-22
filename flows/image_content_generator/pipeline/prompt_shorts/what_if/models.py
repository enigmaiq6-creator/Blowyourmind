from typing import ClassVar, List, Optional, Type

from pydantic import Field

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.geography.models import GeographyScene
from flows.image_content_generator.pipeline.prompt_shorts.what_if import constants as what_if_constants


class WhatIfIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = what_if_constants.IDEA_PROMPT_WHAT_IF
    intrigue_header: str = Field(description="A punchy 2-4 word phrase in ALL CAPS that hooks the viewer (e.g., 'SWAPPED WORLDS', 'FROZEN EMPIRE', 'UNITED CONTINENT').")
    personal_impact: str = Field(description="A single sentence explaining how this alternate geography would affect the viewer's life or world (e.g., 'Your country's borders would disappear overnight.').")
    key_data_stat: str = Field(description="ONE specific, mind-blowing data point in numeric format with units for the floating HUD label (e.g., '1.4 billion displaced', '$25 trillion GDP', '70% oil control').")
    caption: str = Field(description="A highly viral, educational social media caption (Facebook/Instagram) in English about this alternate geography scenario. Include 5-8 hashtags like #WhatIf #Geography #BlowYourMind #AlternateHistory #MindBlowing.")
    category: str = "what_if"


class WhatIfScene(GeographyScene):
    visual_type: str = Field(default="map_3d", description="Type of scene. Use 'map_3d' for 3D political map visuals (default) or 'ai_image' for conceptual illustrations. Always use 'map_3d' for geographic/region-specific scenes.")
    image_prompt: Optional[str] = Field(default=None, description="Physical description in ENGLISH for AI image generation fallback. Include map colors, highlighted regions, labels, arrows, data boxes. Required for all scenes as a fallback description.")


class WhatIfHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = what_if_constants.SCRIPT_PROMPT_WHAT_IF
    category: str = "what_if"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [WhatIfIdea]
    scenes: List[WhatIfScene] = Field(description="List of exactly 5-6 scenes: 1 hook intro + 3-4 geopolitical breakdowns + 1 powerful conclusion/CTA.")
