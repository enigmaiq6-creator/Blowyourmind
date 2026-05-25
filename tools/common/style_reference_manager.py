from pathlib import Path
from typing import Any, List

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class StyleReferenceManager(BaseModelTool):
    """
    Manages loading and providing style reference images from a specified directory.
    """
    style_ref_path: Path

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_reference_images(self) -> List[Path]:
        """
        Retrieves a list of absolute paths for style reference images.
        """
        if not self.style_ref_path.exists():
            Messenger.warning(f"Style reference directory not found: {self.style_ref_path}")
            return []

        extensions = [".png", ".jpg", ".jpeg"]
        style_references = [
            f.absolute()
            for f in self.style_ref_path.glob("*")
            if f.suffix.lower() in extensions
        ]

        Messenger.info(
            f"Loaded {len(style_references)} style reference images from {self.style_ref_path}"
        )
        return style_references
