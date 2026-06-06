from typing import ClassVar, List, Type

from pydantic import Field

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.stories import constants as story_constants


class StoryIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = story_constants.IDEA_PROMPT_STORIES
    caption: str = Field(description="A viral social media caption (Facebook/Instagram) about the curiosity topic in English. Include 5-8 hashtags like #Curiosities #MindBlowing #BlowYourMind #DidYouKnow #Facts.")
    category: str = "stories"


class StoryHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = story_constants.SCRIPT_PROMPT_STORIES
    category: str = "stories"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [StoryIdea]
    scenes: List[Scene] = Field(description="List of 6-8 scenes for the curiosity reel. Each scene has narration, image prompt, and stock video query.")
