from typing import List, Type, ClassVar
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.stories import constants as story_constants
from pydantic import Field

class StoryIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = story_constants.IDEA_PROMPT_STORY
    top_headline: str = Field(description="A Curiosity Gap headline for the video (e.g., 'THEY LIED TO US ABOUT THIS'). Static, Bold, Uppercase.")
    caption: str = Field(description="A highly viral, intriguing social media caption in English that invites comments. MUST include 5 to 8 extremely viral hashtags (e.g., #Mystery #MindBlowingFacts).")

class StoryHandler(CategoryHandler):
    category: str = "stories"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [StoryIdea]
