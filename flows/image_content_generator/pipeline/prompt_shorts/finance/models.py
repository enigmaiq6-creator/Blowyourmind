from typing import ClassVar, List, Type

from pydantic import Field

from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.finance import constants as finance_constants


class FinanceIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = finance_constants.IDEA_PROMPT_FINANCE
    intrigue_header: str = Field(description="A short, punchy 2-4 word phrase in ALL CAPS that persists at the top of the video to create extreme intrigue (e.g., 'DIRTY TAX TRAPS', 'WEALTH SECRETS', 'BANKING TRICKS').")
    personal_impact: str = Field(description="A single sentence explaining how this topic connects to the viewer's life or wallet (e.g., 'The system is quietly taxing you, and you are losing money every day.').")
    key_data_stat: str = Field(description="ONE specific, mind-blowing data point in numeric format with units that will be displayed as a floating HUD label (e.g., '40% tax rate', '$1.2 billion collected', '9% interest trap').")
    caption: str = Field(description="A highly viral, educational, and intriguing social media caption (Facebook/Instagram) in English about this finance topic. Include 5-8 hashtags like #FinanceSecrets #MoneyTips #BlowYourMind #SmartMoney #TaxHacks.")
    category: str = "finance"


class FinanceScene(Scene):
    list_number: int = Field(ge=0, le=8, description="Item list number: 0 for the intro scene, 1 to N for the list items (counting down or ranking, e.g. from 6 to 1).")
    scene_title: str = Field(description="A short, punchy title for this specific list item or concept in ALL CAPS (e.g., 'INHERITANCE TAX', 'FUEL DUTY', 'FISCAL DRAG').")


class FinanceHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = finance_constants.SCRIPT_PROMPT_FINANCE
    category: str = "finance"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [FinanceIdea]
    scenes: List[FinanceScene] = Field(description="List of exactly 6 scenes: 1 intro (list_number=0) + 4 breakdown items (list_number=1 to 4) + 1 CTA/outro.")
