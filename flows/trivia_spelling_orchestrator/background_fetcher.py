"""Fetches background images/videos for trivia questions."""

import os
from pathlib import Path
from typing import Optional, Union

from tools.common.messenger import Messenger
from tools.common.base_model import BaseModelTool
from tools.video_generation.pexels import PexelsTool
from tools.video_generation.pixabay import PixabayTool
from tools.image_generation.vertex_ai import VertexAIImageGenerator
from tools.image_generation.gemini import GeminiImageGenerator


class BackgroundFetcher(BaseModelTool):
    pexels: PexelsTool = PexelsTool()
    pixabay: PixabayTool = PixabayTool()
    vertex_ai: Optional[VertexAIImageGenerator] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.vertex_ai is None:
            use_vertex = os.getenv("USE_VERTEX_AI_IMAGE", "false").lower() == "true"
            if use_vertex:
                project_id = os.getenv("GCP_PROJECT_ID")
                location = os.getenv("GCP_LOCATION", "us-central1")
                if project_id:
                    self.vertex_ai = VertexAIImageGenerator(
                        project_id=project_id, location=location
                    )

    def fetch_video(self, query: str, output_path: Path) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.pexels.fetch_video(query, output_path):
            Messenger.info(f"Pexels video fetched: {output_path.name}")
            return True
        if self.pixabay.fetch_video(query, output_path):
            Messenger.info(f"Pixabay video fetched: {output_path.name}")
            return True
        Messenger.warning(f"No stock video found for: {query}")
        return False

    def generate_image(self, prompt: str, output_path: Path) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.vertex_ai is not None:
            try:
                self.vertex_ai.generate_image(prompt, output_path)
                Messenger.info(f"Vertex AI image generated: {output_path.name}")
                return True
            except Exception as e:
                Messenger.error(f"Vertex AI image failed: {e}")
        try:
            gemini_gen = GeminiImageGenerator(aspect_ratio="9:16")
            gemini_gen.generate_image(prompt, output_path)
            Messenger.info(f"Gemini image generated: {output_path.name}")
            return True
        except Exception as e:
            Messenger.error(f"Gemini image failed: {e}")
            return False

    def resolve_background(
        self, vertex_prompt: str, pexels_query: str,
        output_video: Path, output_image: Path
    ) -> tuple[Optional[Path], Optional[Path]]:
        video_path: Optional[Path] = None
        image_path: Optional[Path] = None
        if self.fetch_video(pexels_query, output_video):
            video_path = output_video
        if not video_path and self.generate_image(vertex_prompt, output_image):
            image_path = output_image
        return video_path, image_path
