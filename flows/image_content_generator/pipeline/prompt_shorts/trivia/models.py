from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.trivia import constants as trivia_constants


class TriviaIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = trivia_constants.IDEA_PROMPT_TRIVIA
    topic: str = Field(description="The general topic of the trivia package (e.g. 'History', 'General Knowledge', 'English Vocabulary', 'Science').")
    intrigue_header: str = Field(description="A short, catchy, 3-5 word challenge in ALL CAPS to display at the top of the video (e.g. 'CAN YOU GET 3/3?', 'IMPOSSIBLE TRIVIA', 'TEST YOUR BRAIN').")
    caption: str = Field(description="A viral, engaging social media caption in English. Invite users to comment their score (e.g., 'What was your score? 🧠 I bet you can't get 3/3! #TriviaChallenge #GeneralKnowledge...').")
    category: str = "trivia"


class TriviaScene(Scene):
    question: str = Field(description="The trivia question itself (same for all 3 scenes of a single question).")
    option_a: str = Field(description="Option A text.")
    option_b: str = Field(description="Option B text.")
    option_c: str = Field(description="Option C text.")
    correct_option: str = Field(description="The correct option letter ('A', 'B', or 'C').")
    explanation: str = Field(description="Brief 1-sentence explanation of why it is correct.")
    trivia_step: str = Field(description="The exact phase of the question. MUST be 'question' (reading options), 'countdown' (tension time), or 'reveal' (highlighting correct answer).")
    question_number: int = Field(description="The question index (1, 2, 3, 4, or 5).")


class TriviaHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = trivia_constants.SCRIPT_PROMPT_TRIVIA
    category: str = "trivia"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [TriviaIdea]
    scenes: List[TriviaScene] = Field(description="The exact sequence of 15 scenes: 5 questions each with [question, countdown, reveal] steps. Scenes 1-3=Q1, 4-6=Q2, 7-9=Q3, 10-12=Q4, 13-15=Q5.")
