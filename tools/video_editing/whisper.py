import json
import whisper
from pathlib import Path
from typing import List, Any

from pydantic import PrivateAttr
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger
from tools.video_editing.whisper_schemas import (
    WhisperTranscription,
    WhisperSegment,
    WhisperOffsets,
    WhisperToken,
    WhisperTranscriptionSegment,
    WhisperWord,
)


class WhisperTool(BaseModelTool):
    """
    Tool for transcribing audio using the openai-whisper Python library.
    Stable and reliable on all systems.
    """
    _model: Any = PrivateAttr(default=None)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # Model will be loaded on first use to save memory
        self._model = None

    def _load_model(self):
        if self._model is None:
            Messenger.info("Loading Whisper Model (Small)...")
            self._model = whisper.load_model("small")

    def _get_transcription_json(
        self,
        audio_path: Path,
        prompt: str = None
    ) -> WhisperTranscription:
        """
        Transcribes audio and returns a structured WhisperTranscription object.
        Uses a local JSON cache to avoid redundant transcriptions.
        """
        json_path = audio_path.with_name(audio_path.name + ".json")
        
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return WhisperTranscription.model_validate(json.load(f))

        self._load_model()
        Messenger.info(f"Transcribing {audio_path.name} with OpenAI Whisper...")
        
        # Run transcription with word-level timestamps and initial prompt context
        result = self._model.transcribe(
            str(audio_path),
            language="es",
            word_timestamps=True,
            initial_prompt=prompt,
            condition_on_previous_text=False, # Previene que Whisper alucine o se quede en un bucle infinito repitiendo letras raras
            no_speech_threshold=0.6
        )
        
        # Convert result to our custom schema
        segments = []
        for s in result["segments"]:
            tokens = []
            if "words" in s and s["words"]:
                for w in s["words"]:
                    tokens.append(WhisperToken(
                        text=w["word"],
                        offsets=WhisperOffsets(**{"from": int(w["start"] * 1000), "to": int(w["end"] * 1000)})
                    ))
            else:
                # FALLBACK: If Whisper fails to align words, keep the text so subtitles don't disappear
                tokens.append(WhisperToken(
                    text=s["text"].strip(),
                    offsets=WhisperOffsets(**{"from": int(s["start"] * 1000), "to": int(s["end"] * 1000)})
                ))
            
            segments.append(WhisperSegment(
                text=s["text"],
                offsets=WhisperOffsets(**{"from": int(s["start"] * 1000), "to": int(s["end"] * 1000)}),
                tokens=tokens
            ))
        
        transcription = WhisperTranscription(transcription=segments)
        
        # Save cache
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(transcription.model_dump_json(indent=2))
            
        return transcription

    def get_transcription_segments(
        self,
        audio_path: Path,
        prompt: str = None
    ) -> List[WhisperTranscriptionSegment]:
        """
        Returns a list of segments with text and timestamps (seconds).
        """
        data = self._get_transcription_json(audio_path, prompt=prompt)
        return [
            WhisperTranscriptionSegment(
                text=s.text.strip(),
                start=s.offsets.from_ms / 1000.0,
                end=s.offsets.to_ms / 1000.0
            )
            for s in data.transcription
        ]

    def get_word_tokens(
        self,
        audio_path: Path,
        prompt: str = None
    ) -> List[WhisperWord]:
        """
        Returns a list of all words with their start/end timestamps (ms).
        """
        data = self._get_transcription_json(audio_path, prompt=prompt)
        words: List[WhisperWord] = []
        for s in data.transcription:
            for t in s.tokens:
                words.append(WhisperWord(
                    text=t.text.strip(),
                    start=t.offsets.from_ms,
                    end=t.offsets.to_ms
                ))
        return words

    def generate_srt(
        self,
        audio_path: Path,
        output_srt: Path,
        prompt: str = None
    ) -> None:
        """
        Generates an SRT file with dynamic word grouping.
        """
        data = self._get_transcription_json(audio_path, prompt=prompt)

        # Extract words from tokens
        words: List[WhisperWord] = []
        for s in data.transcription:
            for t in s.tokens:
                words.append(WhisperWord(
                    text=t.text.strip(),
                    start=t.offsets.from_ms,
                    end=t.offsets.to_ms
                ))

        # Group words into blocks (max 3 words or pause > 0.4s)
        blocks: List[List[WhisperWord]] = []
        current: List[WhisperWord] = []
        
        # Compensate for "ahead" feeling by adding a small offset (200ms)
        offset_ms = 200 
        
        for w in words:
            pause = (float(w.start) - float(current[-1].end)) / 1000.0 if current else 0.0
            if len(current) >= 3 or pause > 0.4:
                blocks.append(current)
                current = []
            current.append(w)
        if current:
            blocks.append(current)

        def fmt(ms: int) -> str:
            # Apply global offset to sync text with audio
            ms = max(0, ms + offset_ms)
            s, ms = divmod(ms, 1000)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        # Write SRT
        with open(output_srt, 'w', encoding='utf-8') as f:
            for i, block in enumerate(blocks):
                f.write(f"{i+1}\n{fmt(block[0].start)} --> {fmt(block[-1].end)}\n")
                f.write(" ".join(w.text for w in block) + "\n\n")
