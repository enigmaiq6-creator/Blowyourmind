"""Text-to-Speech generation for trivia narration."""

from pathlib import Path
from typing import Optional, Union

from tools.audio_generation.vertex_ai_tts import VertexAIAudioGenerator
from tools.audio_generation.gemini import GeminiAudioGenerator
from tools.common.messenger import Messenger


class TtsGenerator:
    def __init__(self, engine: Optional[Union[VertexAIAudioGenerator, GeminiAudioGenerator]] = None):
        self.engine = engine or VertexAIAudioGenerator()

    def generate(self, text: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Messenger.info(f"Generating TTS: {text[:60]}...")
        self.engine.text_to_speech(text, output_path)
        Messenger.audio(f"TTS saved: {output_path}")
        return output_path
