from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.fact_split import constants as fact_split_constants


class PexelsQuery(BaseModel):
    query_sujeto_a: str = Field(description="Highly descriptive English search query for stock photo of Subject A (e.g. 'wolf howling in snowy forest').")
    query_sujeto_b: str = Field(description="Highly descriptive English search query for stock photo of Subject B (e.g. 'golden retriever playing in park').")


class TTSNarration(BaseModel):
    texto_a: str = Field(description="Act 1 narration introducing Subject A in English, starts with 'This is...' (e.g. 'This is a gray wolf, the most efficient predator in the forest.').")
    texto_b: str = Field(description="Act 2 narration introducing Subject B in English, starts with 'This is...' (e.g. 'This is a golden retriever, man's best friend.').")
    pregunta: str = Field(description="Act 3 question narration in English (e.g. 'What's the difference?').")
    contraste_final: str = Field(description="Act 4 contrast explanation in English (e.g. 'The difference is that the wolf has twice the jaw pressure of any domestic dog.').")


class VisualSequenceAct(BaseModel):
    tiempo: str = Field(description="Time range for this act (e.g. '0-2s', '2-4s', '4-6s', '6-end').")
    sujeto_visible: str = Field(description="Which subject is visible on screen: 'A', 'B', or 'ambos'.")
    stickman_file: str = Field(description="Character state image file: 'estado_A.png', 'estado_B.png', or 'estado_curiosidad.png'.")
    posicion_sujeto: Optional[str] = Field(default=None, description="FFmpeg overlay position for the subject image (e.g. 'x=100:y=200').")
    texto_visual: Optional[str] = Field(default=None, description="Optional text displayed on screen (e.g. 'Did you know?').")
    explicacion: Optional[str] = Field(default=None, description="Explanation text for the final act.")


class FFmpegFilterComplex(BaseModel):
    input_1: str = Field(description="Input 0: background, Input 1: sujeto A, Input 2: sujeto B, Input 3: stickman estado_A, Input 4: stickman estado_B, Input 5: stickman estado_curiosidad")
    acts: List[VisualSequenceAct] = Field(description="Same as the visual sequence, but with FFmpeg-specific overlay coordinate format.")


class FactSplitIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = fact_split_constants.IDEA_PROMPT_FACT_SPLIT
    tema: str = Field(description="Theme category: 'science', 'animals', 'history', 'mythology', 'technology', 'space', or 'geography'.")
    sujeto_a: str = Field(description="Name of Subject A (the first comparison subject).")
    sujeto_b: str = Field(description="Name of Subject B (the second comparison subject).")
    pexels: PexelsQuery = Field(description="Pexels search queries for both subjects.")
    locucion: TTSNarration = Field(description="English narration for all 4 acts.")
    hook: str = Field(description="Scroll-stopping hook in English (10-15 words).")
    caption: str = Field(description="Social media caption in English with 5-8 hashtags.")
    contrast_key: str = Field(description="One-line summary of the key difference in English.")
    category: str = "fact_split"


class FactSplitScene(Scene):
    act_number: int = Field(description="Act number: 1, 2, 3, or 4.")
    stickman_state: str = Field(description="Character state: 'estado_A', 'estado_B', or 'estado_curiosidad'.")
    sujeto_visible: str = Field(description="Which subject is visible: 'A', 'B', or 'ambos'.")
    visual_text: Optional[str] = Field(default=None, description="Text overlay shown on screen during this act in English.")
    pexels_query_a: Optional[str] = Field(default=None, description="Pexels query for Subject A image.")
    pexels_query_b: Optional[str] = Field(default=None, description="Pexels query for Subject B image.")
    overlay_positions: str = Field(default="", description="FFmpeg overlay coordinates for this scene.")
    scene_overlay_type: Optional[str] = Field(default=None, description="Visual overlay type: 'title', 'big_number', 'question', 'explanation' or null.")


class FactSplitHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = fact_split_constants.SCRIPT_PROMPT_FACT_SPLIT
    category: str = "fact_split"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [FactSplitIdea]
    scenes: List[FactSplitScene] = Field(description="List of 4 acts for the Fact Split video.")
    pexels: PexelsQuery = Field(description="Pexels queries for subject images.")
    locucion: TTSNarration = Field(description="Full English narration text.")
    ffmpeg_logic: FFmpegFilterComplex = Field(description="FFmpeg compositing logic and visual sequence.")
    whisper_payload: str = Field(description="Complete text for Whisper subtitle segmentation, concatenation of all narration.")
