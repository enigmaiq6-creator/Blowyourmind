import requests
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

from tools.common.messenger import Messenger
from tools.image_generation.midjourney import ImageTask


class PollinationsImageGenerator:
    def __init__(
        self,
        model: str = "flux",
        aspect_ratio: str = "9:16",
    ):
        self.model = model
        self.aspect_ratio = aspect_ratio

    @property
    def _size_map(self) -> dict:
        return {
            "9:16": (720, 1280),
            "16:9": (1280, 720),
            "1:1": (1024, 1024),
            "4:3": (1152, 896),
            "3:4": (896, 1152),
        }

    def generate_image(self, prompt: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        w, h = self._size_map.get(self.aspect_ratio, (720, 1280))

        Messenger.info(f"Pollinations generating: {prompt[:60]}...")

        url = (
            f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            f"?width={w}&height={h}&nologo=true&model={self.model}"
        )

        resp = requests.get(url, timeout=120)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(resp.content)

        Messenger.image(f"Pollinations image saved: {output_path}")

    def generate_images(self, tasks: List[ImageTask]) -> None:
        total = len(tasks)
        Messenger.info(f"Pollinations Batch: {total} images")

        for i, task in enumerate(tasks, start=1):
            try:
                Messenger.info(f"Pollinations {i}/{total}: {task.output_path.name}")
                self.generate_image(prompt=task.prompt, output_path=task.output_path)
            except Exception as e:
                Messenger.error(f"Pollinations failed for {task.output_path.name}: {e}")
                raise

        Messenger.step_success(f"Pollinations batch complete: {total} images.")
