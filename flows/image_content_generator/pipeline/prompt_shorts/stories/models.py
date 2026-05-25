from typing import List, Type, ClassVar
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.stories import constants as story_constants
from pydantic import Field

class StoryIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = story_constants.IDEA_PROMPT_STORY
    intrigue_header: str = Field(description="A short, punchy 3-5 word phrase to persist at the top of the video to create extreme intrigue (e.g., 'EL SECRETO DEL MILLONARIO', 'MIRA HASTA EL FINAL').")
    caption: str = Field(description="Una descripción para redes sociales (Facebook/Instagram) altamente viral, intrigante y que invite a comentar. DEBE incluir entre 5 y 8 hashtags extremadamente virales acordes al tema (Ej: #Curiosidades #Misterio #DatosCuriosos + específicos del tema).")

class StoryHandler(CategoryHandler):
    category: str = "stories"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [StoryIdea]
