from typing import ClassVar, List, Optional, Type

from pydantic import Field

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.seven_levels import constants as seven_constants


class SevenLevelsIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = seven_constants.IDEA_PROMPT_SEVEN_LEVELS
    intrigue_header: str = Field(description="A short, punchy 2-4 word phrase in ALL CAPS that persists at the top of the video to create extreme intrigue (e.g., 'FORBIDDEN ZONES', 'DEADLY ISLANDS', 'HIDDEN WORLDS').")
    personal_impact: str = Field(description="A single sentence explaining how this topic connects to the viewer's life or perspective (e.g., 'These hidden places exist in YOUR world, and you walk past them every day.').")
    key_data_stat: str = Field(description="ONE specific, mind-blowing data point in numeric format with units that will be displayed as a floating HUD label (e.g., '10,000 locked doors', '3,000 abandoned sites', '47 secret cities').")
    caption: str = Field(description="A highly viral, educational, and intriguing social media caption (Facebook/Instagram) about the topic in English. MUST include 5 to 8 extremely viral hashtags (e.g., #HiddenWorlds #MindBlowing #7Levels #BlowYourMind #SecretPlaces).")
    category: str = "seven_levels"


class SevenLevelsScene(Scene):
    nivel: int = Field(ge=0, le=7, description="Level number: 0 for the intro scene, 1-7 for each progression level. Level 1 is the least intense, Level 7 is the most mind-blowing.")
    level_title: str = Field(description="A short, punchy title for this level in ALL CAPS (e.g., 'THE MOST SECRET BASE', 'THE ISLAND OF DOLLS', 'THE FORBIDDEN CITY').")
    impact: str = Field(description="Impact level of this scene: 'Low' (levels 1-2, interesting), 'Medium' (levels 3-4, surprising), 'High' (levels 5-6, disturbing), 'Extreme' (level 7, mind-blowing). Must escalate with each level.")


class SevenLevelsHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = seven_constants.SCRIPT_PROMPT_SEVEN_LEVELS
    category: str = "seven_levels"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [SevenLevelsIdea]
    scenes: List[SevenLevelsScene] = Field(description="List of exactly 8 scenes: 1 intro (nivel=0) + 7 levels (nivel=1-7) with escalating impact.")
