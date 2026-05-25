# Standard: schemas.py

The source of truth for the project's data structures, state machines, and Enums using Pydantic. Note: Models that contain logic for *prompt generation* (like `BaseIdea` or `VideoScript`) belong in `models.py` within the `prompt_*/` modules, not here.

## Requirements
- **Enums:** Always use `(str, Enum)` for `State`, `Category`, and `Column`.
- **States:** Standardized `State` lifecycle: `NEW`, `CONCEPT_GENERATED`, `SCRIPT_GENERATED`, `IMAGES_GENERATED`, `AUDIO_GENERATED`, `VIDEO_GENERATED`, `COMPLETED`.
- **Separation of Concerns:**
    - `BaseIdea` / `VideoScript` / `Scene`: Reside in modular `prompt_base` logic.
    - `State` / `VideoOrientation`: Universal enums reside in `schemas.py`.
    - `Tracking Model`: (e.g., `StateTracking`, `IdeaRaw`) for CSV storage only.
- **Structured Prompts:** Use sub-models like `ImagePrompt` with specific fields (`subject`, `action`, `environment`, etc.) instead of raw strings.

## Common Models
- `State`: Pipeline state machine tracking enum.
- `AudioAlignment`: Mapping scenes to audio timestamps.
- `TrackingModel`: The lightweight object stored in the CSV.

## Example
```python
class State(str, Enum):
    NEW = "NEW"
    CONCEPT_GENERATED = "CONCEPT_GENERATED"
    COMPLETED = "COMPLETED"

class VideoOrientation(str, Enum):
    SHORTS = "SHORTS"
    LONG = "LONG"

class IdeaRaw(BaseModel):
    id: int
    title: str
    state: State
    category: str
```
