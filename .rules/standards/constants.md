# Standard: constants.py

Central source of truth for raw prompt strings, morals, and configuration flags.

## Requirements
- **Centralization:** All LLM prompts MUST be defined here, never in the pipeline or manager logic.
- **Categorization:** Group constants logically: `IDEA_PROMPTS`, `SCRIPT_PROMPTS`, `IMAGE_PROMPTS`, `AUDIO_PROMPTS`.
- **Naming Conventions:**
    - Use `UPPER_CASE` for all constants.
    - Use descriptive prefixes: `IDEA_PROMPT_...`, `SCRIPT_PROMPT_...`.
- **Moral Libraries:** Store large lists (e.g., `STORY_THEMES`) here as `List[str]`.
- **String Formatting:** Use `{}` placeholders for dynamic values, ensuring they match the keys expected by `PromptManager`.

## Example
```python
# Constants for the Project

# General Themes
STORY_THEMES = [
    "Resilience in the face of adversity",
    "The importance of community"
]

# Prompt Templates
IDEA_PROMPT_STORYYELLING = """
Create a compelling story idea based on: {theme}.
Context: Modern style.
Format: JSON.
"""

SCRIPT_PROMPT_STORYTELLING = """
Expand the title: {title} into a 7-scene script.
Theme: {theme}.
Everyday situation: {everyday_situation}.
"""
```
