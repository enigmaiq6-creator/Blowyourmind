from typing import List

from pydantic import BaseModel, Field, ConfigDict


class WhisperOffsets(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_ms: int = Field(alias="from")
    to_ms: int = Field(alias="to")


class WhisperToken(BaseModel):
    text: str
    offsets: WhisperOffsets


class WhisperSegment(BaseModel):
    text: str
    offsets: WhisperOffsets
    tokens: List[WhisperToken] = []


class WhisperTranscription(BaseModel):
    transcription: List[WhisperSegment]


class WhisperTranscriptionSegment(BaseModel):
    text: str
    start: float  # s
    end: float    # s


class WhisperWord(BaseModel):
    text: str
    start: int  # ms
    end: int    # ms
