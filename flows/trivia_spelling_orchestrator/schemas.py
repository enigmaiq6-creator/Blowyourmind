from typing import Literal
from pydantic import BaseModel, Field


class QuestionTiming(BaseModel):
    start: int = Field(description="Start time in seconds")
    countdown_start: int = Field(description="Countdown start time in seconds")
    reveal_start: int = Field(description="Reveal start time in seconds")
    end: int = Field(description="End time in seconds")


class QuestionVisuals(BaseModel):
    vertex_ai_prompt: str = Field(description="Prompt for Vertex AI Imagen to generate background")
    pexels_search_query: str = Field(description="Search query for Pexels/Pixabay stock videos")


class TtsScripts(BaseModel):
    intro_and_options: str = Field(description="TTS script for intro and options reading")
    reveal: str = Field(description="TTS script for answer reveal")


class Question(BaseModel):
    id: int = Field(description="Question number (1, 2, or 3)")
    question_text: str = Field(description="The trivia question text")
    option_a: str = Field(description="Option A text")
    option_b: str = Field(description="Option B text")
    option_c: str = Field(description="Option C text")
    correct_answer: Literal["A", "B", "C"] = Field(description="The correct option letter")
    visuals: QuestionVisuals
    tts_scripts: TtsScripts
    timing: QuestionTiming


class VideoMetadata(BaseModel):
    topic: str = Field(description="Topic of the video")
    total_duration_seconds: int = Field(description="Total video duration in seconds")
    language: str = Field(description="Language of the video")


class TriviaVideoPlan(BaseModel):
    video_metadata: VideoMetadata
    questions: list[Question]
