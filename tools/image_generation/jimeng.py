import os
import time
import requests
from pathlib import Path
from typing import List, Optional

from tools.common.messenger import Messenger
from tools.image_generation.midjourney import ImageTask


class JimengImageGenerator:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "jimeng-image-4.5",
        aspect_ratio: str = "9:16",
    ):
        self.api_key = api_key or os.getenv("JIMENG_API_KEY", "")
        self.base_url = base_url or os.getenv("JIMENG_BASE_URL", "https://api.jimeng.ai/v1")
        self.model = model
        self.aspect_ratio = aspect_ratio

        if not self.api_key:
            Messenger.warning("JIMENG_API_KEY not set. Jimeng generator will be skipped.")

    @property
    def _size_map(self) -> dict:
        return {
            "9:16": "720x1280",
            "16:9": "1280x720",
            "1:1": "1024x1024",
            "4:3": "1152x896",
            "3:4": "896x1152",
        }

    def generate_image(self, prompt: str, output_path: Path) -> None:
        if not self.api_key:
            raise RuntimeError("Jimeng API key not configured.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        size = self._size_map.get(self.aspect_ratio, "720x1280")

        Messenger.info(f"Jimeng generating: {prompt[:60]}...")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.base_url}/images/generations",
            json=payload,
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        image_url = data.get("data", [{}])[0].get("url") or data.get("data", [{}])[0].get("b64_json")
        if not image_url:
            raise RuntimeError("Jimeng response missing image data.")

        if image_url.startswith("http"):
            img_resp = requests.get(image_url, timeout=60)
            img_resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_resp.content)
        else:
            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_url))

        Messenger.image(f"Jimeng image saved: {output_path}")

    def generate_images(self, tasks: List[ImageTask]) -> None:
        total = len(tasks)
        Messenger.info(f"Jimeng Batch: {total} images")

        for i, task in enumerate(tasks, start=1):
            try:
                Messenger.info(f"Jimeng {i}/{total}: {task.output_path.name}")
                self.generate_image(prompt=task.prompt, output_path=task.output_path)
            except Exception as e:
                Messenger.error(f"Jimeng failed for {task.output_path.name}: {e}")
                raise

        Messenger.step_success(f"Jimeng batch complete: {total} images.")
