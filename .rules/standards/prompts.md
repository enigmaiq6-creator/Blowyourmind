# Standard: Prompt Manager Architecture (`prompt_*/`)

Manages all LLM prompt templates, dynamic instructions, and formatting logic. This logic is modularized into directories (e.g., `prompt_base/`, `prompt_shorts/`, `prompt_longs/`) rather than a single file.

## Core Patterns
- **Base Models as Logic Holders:** Pydantic domain models (like `BaseIdea`, `VideoScript`) are responsible for generating their own structural prompts (e.g., `get_json_format_instructions()`, `get_idea_prompt()`).
- **Encapsulation:** Prompt string formatting and JSON schema generation MUST live within the Pydantic data model it corresponds to, NOT in the Orchestration Manager.
- **Inheritance vs Dictionary:** Use a Base `CategoryHandler` class that manages specialized variants (BaseIdea types), instead of giant Enum dictionaries.
- **Hierarchy:** Structure advanced prompt pipelines into specific directories with dedicated `models.py`, `manager.py`, and `constants.py`.
- **Dynamic JSON Schema:** Use recursion to dynamically append mandatory output formats (e.g., JSON schemas) to prompts based on Pydantic `Field(description=...)` metadata.
- **Category Handlers:** Specific prompt niches (e.g., motivational, storytelling) reside in their own subdirectories and implement a handler class inheriting from `CategoryHandler` to manage specialized execution and constants.

## Directory Structure Example
```text
prompt_base/
├── constants.py      # Base constraints (e.g., IMAGE_PROMPT)
├── manager.py        # BasePromptManager wrapper/orchestrator
└── models.py         # All prompt-related Pydantic models (BaseIdea, Scene, VideoScript)

prompt_shorts/
├── manager.py        # specific configurations and subclasses
└── storytelling/
    ├── constants.py  # Specific prompt texts (IDEA_PROMPT_CLASSIC, SCRIPT_PROMPT)
    └── models.py     # StorytellingHandler (inherits from CategoryHandler)
```

## Implementation Example
```python
# prompt_base/models.py
class BaseIdea(BaseModel):
    title: str
    IDEA_PROMPT: ClassVar[str]

    @classmethod
    def get_json_format_instructions(cls) -> str:
        # Dynamically extracts fields to build JSON output requirement
        ...

    @classmethod
    def get_idea_prompt(cls) -> str:
        return cls.IDEA_PROMPT.strip() + "\n" + cls.get_json_format_instructions()

class CategoryHandler(VideoScript):
    idea_variants: ClassVar[Sequence[Type[BaseIdea]]]

    @classmethod
    def get_random_idea_variant(cls) -> Type[BaseIdea]:
        return random.choice(cls.idea_variants)
```
