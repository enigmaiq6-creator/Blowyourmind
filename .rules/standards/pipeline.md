# Standard: pipeline.py

The central orchestrator for the project. Handles the flow of data through AI tools, manages the project's state, and handles the filesystem hierarchy.

## Core Patterns
- **Base Class:** Inherit from `tools.common.base_model.BaseModelTool`.
- **Private Attributes:** Use `PrivateAttr` for tool instances to maintain Pydantic compatibility.
- **Lazy Loading:** Initialize tools via `@property` to minimize startup overhead.
- **Section Headers:** Use `# --- SECTION NAME ---` to divide the class into logical blocks (JSON HELPERS, DIRECTORY HELPERS, PIPELINE STEPS).
- **Step Documentation:** Every step method must contain a docstring with a numbered list of its sub-tasks.

---

## Standard Methods & Helpers

### JSON Sidecars
- `load_json(idea_id: int, filename: str, model_class: Type[T]) -> T`
- `save_json(idea_id: int, filename: str, data: BaseModel)`

### Directory Management
- `get_out_dir() -> Path`
- `get_ideas_dir() -> Path`
- `get_idea_path(idea_id: int) -> Path`
- `get_idea_subdir(idea_id: int, subdir: str) -> Path`
- `get_idea_asset_path(idea_id: int, subdir: str, filename: str) -> Path`

---

## Example Structure (Full Detail)
```python
from pydantic import PrivateAttr
from tools.common.base_model import BaseModelTool

class Pipeline(BaseModelTool):
    out_base: Path
    resource_base: Path

    # PRIVATE TOOL ATTRS
    _ffmpeg: Optional[FFmpegTool] = PrivateAttr(default=None)
    _store: Optional[CsvStore] = PrivateAttr(default=None)

    # Standard Output Directories
    IDEAS_DIR: ClassVar[str] = "ideas"
    # ... (other DIR ClassVars)

    # Standard Output Files
    IDEA_JSON: ClassVar[str] = "idea.json"
    SCRIPT_JSON: ClassVar[str] = "script.json"

    # Standard Scene Patterns
    SCENE_IMAGE_PATTERN: ClassVar[str] = "scene_{}.png"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def ffmpeg(self) -> FFmpegTool:
        if self._ffmpeg is None:
            self._ffmpeg = FFmpegTool()
        return self._ffmpeg

    # --- JSON HELPERS ---
    def load_json(self, idea_id: int, filename: str, model_class: Type[T]) -> T:
        """Loads and validates a JSON file from the idea's root directory."""
        path = self.get_idea_path(idea_id) / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {filename} for project {idea_id}")
        return model_class.model_validate_json(path.read_text(encoding="utf-8"))

    # --- DIRECTORY HELPERS ---
    def get_ideas_dir(self) -> Path:
        """Returns the absolute path to the global ideas folder."""
        path = self.out_base / self.IDEAS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_path(self, idea_id: int) -> Path:
        """Returns the absolute path to an idea's folder."""
        folder_name = f"idea_{idea_id:06d}"
        path = self.get_ideas_dir() / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    # --- PIPELINE STEPS ---
    def step1_generate_concept(self):
        """
        Generate Concept: Creates an engaging story idea in a modern context.
        1. Gets the next ID from the tracking CSV.
        2. Generates a concept using Gemini LLM.
        3. Registers the new idea in tracking CSV.
        4. Saves idea.json sidecar.
        5. Updates state to CONCEPT_GENERATED.
        """
        Messenger.info("\n--- Generating story concept ---")

        # 1. Selects thematic category
        next_id = self.store.get_next_id()
        # ... logic ...

        # 4. Saves idea.json
        self.save_json(idea_obj.id, self.IDEA_JSON, idea_data)

        # 5. Updates state
        idea_obj.state = State.CONCEPT_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 1 ready: {State.CONCEPT_GENERATED} finalized.\n")
```
