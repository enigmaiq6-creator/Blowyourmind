import json
import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Type

from pydantic import BaseModel, Field, ConfigDict

from flows.image_content_generator.pipeline.prompt_base import constants


class BaseIdea(BaseModel):
    """
    Base model for all AI-generated ideas, ensuring every idea has a title and a hook.
    Forces all subclasses to define an IDEA_PROMPT.
    """
    title: str = Field(description="Creative and descriptive title of the idea in English.")
    hook: str = Field(description="Scroll-stopping hook (10-15 words) in English.")
    IDEA_PROMPT: ClassVar[str] = ""


class Subject(BaseModel):
    description: str = Field(description="Physical description in ENGLISH. Include clothing, key features, and expression. IMPORTANT: This MUST align with the global 'style' (e.g., if stickman, keep outlines thick and features stylized).")  # noqa: E501
    action: str = Field(description="Specific action, pose, or interaction with other subjects in ENGLISH")  # noqa: E501


class ImagePrompt(BaseModel):
    subjects: List[Subject] = Field(description="List of the main subjects present in the scene")
    environment: str = Field(description="Location and background details in ENGLISH (e.g. professional office, busy street, cozy room). Style it to match the global 'style'.")  # noqa: E501
    lighting: str = Field(description="Lighting mood and color palette in ENGLISH")
    composition: str = Field(description="Shot framing and camera angle (e.g. Close-up, Wide shot) in ENGLISH")  # noqa: E501
    style: str = Field(description="EXACT visual style in ENGLISH. Match the specific visual identity requested (e.g. 'Modern webcomic sketch style').")  # noqa: E501

    @property
    def formatted_prompt(self) -> str:
        """
        Dynamically builds the prompt string from the structured image prompt fields.
        """
        prompt_parts: List[str] = []

        # 1. Subjects description and specific actions
        if self.subjects:
            subj_desc: List[str] = []
            for s in self.subjects:
                subj_desc.append(f"{s.description.strip()} ({s.action.strip()})")
            prompt_parts.append(f"Subjects: {'; '.join(subj_desc)}")

        # 2. Other fields
        # Dynamically handle other string fields (environment, lighting, composition)
        for key, value in self.model_dump().items():
            if key == "subjects":
                continue
            if value and isinstance(value, str):
                prompt_parts.append(f"{key.capitalize()}: {value.strip()}")

        return ". ".join(prompt_parts) + "."


class Scene(BaseModel):
    model_config = ConfigDict(extra='ignore')
    scene_number: int = Field(description="Sequential number of the scene (Integer)")
    visual_type: str = Field(default="stock_video", description="Choose 'stock_video' if the scene is common/realistic, or 'ai_image' if it is historical, fantasy-based, or highly specific and hard to film.")
    image_prompt: str = Field(description="Physical description and style in ENGLISH. Use a unified block of text.")
    pexels_query: str = Field(default="", description="1-3 English keywords to search for a free stock video on Pexels (e.g. 'cat sleeping'). Leave empty if visual_type is 'ai_image'.")
    narration: str = Field(description="Spoken narration for this scene. CRITICAL: MUST be written 100% in English. Never use Spanish or other languages under any circumstances.")
    movement_instruction: Optional[str] = Field(default=None, description="Instructions for video animation/movement")


class VideoScript(BaseModel):
    model_config = ConfigDict(extra='ignore')
    intrigue_header: Optional[str] = None
    scenes: List[Scene]
    SCRIPT_PROMPT: ClassVar[str]
    CHUNK_INSTRUCTIONS: ClassVar[str] = constants.CHUNK_INSTRUCTIONS

    @classmethod
    def get_json_format_instructions(cls) -> str:
        """
        Returns the mandatory JSON format for the script.
        This is standardized for all script generations.
        """

        def get_format_recursive(model_class: Type[BaseModel]) -> Dict[str, Any]:
            format_dict: Dict[str, Any] = {}
            for name, field in model_class.model_fields.items():
                # Get the underlying type, handling List and Optional
                annotation = field.annotation
                origin = getattr(annotation, "__origin__", None)
                args = getattr(annotation, "__args__", (None,))

                if origin is list:
                    # Assume list of models or primitives
                    item_type = args[0]
                    if isinstance(item_type, type):
                        if issubclass(item_type, BaseModel):
                            format_dict[name] = [get_format_recursive(item_type)]
                        else:
                            format_dict[name] = [str(field.description or item_type.__name__)]
                    else:
                        format_dict[name] = [str(field.description or str(item_type))]
                elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    format_dict[name] = get_format_recursive(annotation)
                else:
                    format_dict[name] = str(field.description or name)
            return format_dict

        # Generate sample structure
        sample_dict = get_format_recursive(cls)
        json_format = json.dumps(sample_dict, indent=2, ensure_ascii=False)

        schema_block = (
            "\n**Formato de Salida Obligatorio (JSON):**\n"
            "```json\n"
            f"{json_format}\n"
            "```\n"
        )
        return schema_block

    @classmethod
    def get_full_script_prompt(cls, selected_idea_data: BaseIdea) -> str:
        """
        Formats the script prompt using the provided selected idea data
        and appends the mandatory JSON schema.
        """
        base_prompt = cls.SCRIPT_PROMPT.strip()

        base_context = (
            "\n\nTU IDEA DE BASE (CONTEXTO EN JSON):\n"
            f"{selected_idea_data.model_dump_json(indent=2)}\n"
        )

        return base_prompt + base_context + cls.get_json_format_instructions()

    @classmethod
    def get_chunked_script_prompt(
        cls,
        base_prompt: str,
        start_scene: int,
        end_scene: int,
        context: str,
    ) -> str:
        """Formats the script prompt with chunking instructions and previous context."""

        instructions = cls.CHUNK_INSTRUCTIONS.format(
            start_scene=start_scene, end_scene=end_scene, context=context
        )

        return base_prompt + "\n" + instructions


class CategoryHandler(VideoScript):
    """
    Manages a group of specialized configurations for a category.
    Responsible for selecting variety within its group.
    """

    idea_variants: ClassVar[Sequence[Type[BaseIdea]]]

    @classmethod
    def get_random_idea_variant(cls) -> Type[BaseIdea]:
        """Picks a random specialized configuration from the available idea variants."""

        return random.choice(cls.idea_variants)


class SelectedConfig(BaseModel):
    """
    Holds all necessary data after a random category selection.
    """
    category: str
    handler: Type[CategoryHandler]
    idea_prompt: str
    idea_model: Type[BaseIdea]
