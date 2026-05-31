from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class State(str, Enum):
    NEW = "NEW"
    SCRIPT_GENERATED = "SCRIPT_GENERATED"
    IMAGES_GENERATED = "IMAGES_GENERATED"
    CLIPS_GENERATED = "CLIPS_GENERATED"
    AUDIO_GENERATED = "AUDIO_GENERATED"
    VIDEO_GENERATED = "VIDEO_GENERATED"
    VIDEO_SUBTITLED = "VIDEO_SUBTITLED"
    VIDEO_PRO_SUBTITLED = "VIDEO_PRO_SUBTITLED"
    VIDEO_MUSIC_GENERATED = "VIDEO_MUSIC_GENERATED"
    COMPLETED = "COMPLETED"
    UPLOADED = "UPLOADED"


class VideoOrientation(str, Enum):
    SHORT = "short"
    LONG = "long"


class SceneAlignment(BaseModel):
    scene_number: int
    start_time: float
    end_time: float


class AudioAlignment(BaseModel):
    alignments: List[SceneAlignment]


class NarrationCue(BaseModel):
    word: str = Field(description="The word that triggers the visual event")
    start_ms: float = Field(description="Start timestamp in ms")
    end_ms: float = Field(description="End timestamp in ms")
    event_type: str = Field(default="pin_drop", description="Type of visual event: pin_drop, label_flash, vignette_slide, arrow_animate, camera_zoom")
    target: str = Field(default="", description="Target visual element name (e.g., pin label, vignette title)")


class IdeaRaw(BaseModel):
    id: int
    title: str
    state: State
    category: str
