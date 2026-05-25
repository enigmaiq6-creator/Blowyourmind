from typing import Dict
from tools.common.messenger import Messenger

class CostTracker:
    """
    Tracks the cost of AI API calls for each video run.
    """
    # Prices in USD
    PRICES = {
        "gemini_text_1k": 0.0001,  # Gemini 2.0 Flash is extremely cheap
        "imagen_3_image": 0.03,    # Imagen 3 standard
        "veo_video_clip": 0.25,    # Veo 3.1 fast preview (Estimate)
        "vertex_tts_1k_chars": 0.004, # Studio voices
    }

    def __init__(self):
        self.costs: Dict[str, float] = {
            "text": 0.0,
            "image": 0.0,
            "video": 0.0,
            "audio": 0.0
        }

    def add_text_cost(self, tokens: int):
        self.costs["text"] += (tokens / 1000) * self.PRICES["gemini_text_1k"]

    def add_image_cost(self, count: int = 1):
        self.costs["image"] += count * self.PRICES["imagen_3_image"]

    def add_video_cost(self, count: int = 1):
        self.costs["video"] += count * self.PRICES["veo_video_clip"]

    def add_audio_cost(self, characters: int):
        self.costs["audio"] += (characters / 1000) * self.PRICES["vertex_tts_1k_chars"]

    def get_total_cost(self) -> float:
        return sum(self.costs.values())

    def report(self):
        total = self.get_total_cost()
        Messenger.info("------------------------------------------")
        Messenger.info("💰 COST REPORT FOR THIS VIDEO:")
        Messenger.info(f"   - Text (Script/Idea): ${self.costs['text']:.4f}")
        Messenger.info(f"   - Images (Imagen 3):  ${self.costs['image']:.4f}")
        Messenger.info(f"   - Video (Veo AI):     ${self.costs['video']:.4f}")
        Messenger.info(f"   - Audio (TTS):        ${self.costs['audio']:.4f}")
        Messenger.info(f"   ---------------------------------------")
        Messenger.info(f"   ⭐ TOTAL COST:        ${total:.4f} USD")
        Messenger.info(f"   (Approx. ${total * 3950:.2f} COP)")
        Messenger.info("------------------------------------------")
