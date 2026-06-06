from typing import Any, Type, TypeVar

from pydantic import BaseModel

from tools.common.gemini_base import GeminiBase
from tools.common.messenger import Messenger

T = TypeVar("T", bound=BaseModel)


class GeminiTextGenerator(GeminiBase):
    text_model: str = "gemini-2.0-flash"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def generate_text(self, prompt: str, schema: Type[T]) -> T:
        """
        Generates content with Gemini and parses it into a Pydantic model.
        """
        if not prompt:
             Messenger.error("❌ ERROR: PROMPT VACÍO")
        else:
             Messenger.info(f"DEBUG PROMPT LEN: {len(prompt)}")

        response = self._execute_with_retry(
            "models.generate_content",
            model=self.text_model,
            contents=[prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': schema,
            }
        )
        self._extract_usage(response, self.text_model)

        if not response.text:
            raise RuntimeError("❌ No hay respuesta de Gemini")

        return schema.model_validate_json(response.text)

    def generate(self, prompt: str) -> str:
        """
        Generates raw text with Gemini with retry logic (30s wait, 3 attempts on ServerError).
        """
        response = self._execute_with_retry(
            "models.generate_content",
            model=self.text_model,
            contents=[prompt]
        )
        self._extract_usage(response, self.text_model)

        if not response.text:
            raise RuntimeError("No hay respuesta de Gemini")

        return response.text.strip()

    def translate_srt(self, srt_content: str, target_language: str = "English") -> str:
        """
        Translates an SRT subtitle file to the target language while strictly preserving timestamps and SRT format.
        """
        prompt = f"""
You are a professional subtitle translator. Translate the following SRT file to {target_language}.
CRITICAL RULES:
1. Preserve the exact SRT format (subtitle number, timestamps).
2. DO NOT change or modify the timestamps (e.g. 00:00:01,000 --> 00:00:04,000).
3. Translate ONLY the subtitle text.
4. Keep the translation concise so it fits the timing on screen.
5. Do NOT add any markdown formatting, headers, or conversational text. Output ONLY the raw SRT format.

SRT CONTENT:
{srt_content}
"""
        response = self._execute_with_retry(
            "models.generate_content",
            model=self.text_model,
            contents=[prompt]
        )
        self._extract_usage(response, self.text_model)
        
        if not response.text:
            raise RuntimeError("❌ No hay respuesta de Gemini en la traducción.")
            
        translated_srt = response.text.strip()
        # Remove markdown code blocks if gemini added them accidentally
        if translated_srt.startswith("```srt"):
            translated_srt = translated_srt[6:]
        if translated_srt.startswith("```"):
            translated_srt = translated_srt[3:]
        if translated_srt.endswith("```"):
            translated_srt = translated_srt[:-3]
            
        return translated_srt.strip()
