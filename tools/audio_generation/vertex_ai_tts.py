import os
from pathlib import Path
from typing import Any

from google.cloud import texttospeech
from pydantic import PrivateAttr
from tools.common.messenger import Messenger
from tools.common.base_model import BaseModelTool


class VertexAIAudioGenerator(BaseModelTool):
    """
    Generator that uses Google Cloud Text-to-Speech (Professional)
    to generate high-quality audio using your GCP credits.
    """
    _client: Any = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Auth is handled via ADC (gcloud auth application-default login)
        self._client = texttospeech.TextToSpeechClient()

    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        return self._client

    def text_to_speech(
        self,
        text: str,
        audio_path: Path,
    ) -> None:
        """
        Generates audio using Google Cloud TTS and saves it as a 16kHz WAV.
        (Optimal for Whisper transcription).
        """
        Messenger.info(f"Synthesizing Audio (Vertex Pro): {text[:50]}...")
        
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        # We'll use a high-quality English Studio voice
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Studio-Q" # High quality male Studio voice
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000, # Native 16kHz for Whisper!
            speaking_rate=1.08 # Slightly faster for a more natural, less robotic flow
        )

        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(audio_path, "wb") as out:
            out.write(response.audio_content)
        
        Messenger.audio(f"Audio generado (Pro 16k): {audio_path}")
