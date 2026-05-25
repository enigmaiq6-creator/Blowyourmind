from typing import List, Type, Dict, Any, ClassVar
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.finances import constants as finance_constants

from pydantic import BaseModel, Field

class MindsetFinanceIdea(BaseIdea):
    # Usar ClassVar es CRÍTICO para que Pydantic no lance AttributeError
    IDEA_PROMPT: ClassVar[str] = finance_constants.IDEA_PROMPT_MINDSET

class InteractionImageIdea(BaseIdea):
    """Modelo para generar acertijos y contenido de alta interacción."""
    IDEA_PROMPT: ClassVar[str] = finance_constants.IMAGE_INTERACTION_PROMPT
    idea_visual: str = Field(description="Descripción clara de la escena visual")
    image_prompt: str = Field(description="Prompt detallado en INGLÉS, estilo sketch/dibujo")
    caption: str = Field(description="Caption para Facebook corto y llamativo")
    objetivo_psicologico: str = Field(description="Curiosidad, duda, comparación, etc.")

class RiddlePost(BaseModel):
    """Modelo estructurado para la respuesta del generador de acertijos."""
    idea_visual: str = Field(description="Descripción clara de la escena visual")
    image_prompt: str = Field(description="Prompt detallado en INGLÉS, estilo cinematográfico")
    caption: str = Field(description="Caption para Facebook corto y llamativo")
    objetivo_psicologico: str = Field(description="Curiosidad, duda, comparación, etc.")

class FinanceHandler(CategoryHandler):
    category: str = "finances"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [MindsetFinanceIdea, InteractionImageIdea]
