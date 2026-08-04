from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, VideoScript, CategoryHandler

class FinanceIdea(BaseIdea):
    tema: str = Field(description="Theme category: 'finance', 'history', etc.")
    title: str = Field(description="Short punchy title")
    hook: str = Field(description="Scroll-stopping opening phrase")
    key_takeaway: str = Field(description="One-line summary of the fact")
    caption: str = Field(description="Viral caption for social media")
    category: str = Field(default="finance")

class FinanceScene(BaseModel):
    scene_number: int
    narration: str
    image_prompt: str = Field(description="Image generation prompt including papercraft style")

class FinanceScript(VideoScript):
    scenes: list[FinanceScene]
    whisper_payload: str = Field(description="Full concatenated narration text")

class FinanceHandler(CategoryHandler):
    def get_script_class(self):
        return FinanceScript
