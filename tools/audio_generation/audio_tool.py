import random
from pathlib import Path
from typing import Any, Optional

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class AudioTool(BaseModelTool):
    """
    Tool for audio-related operations, like selecting random files.
    """
    bg_music_dir: Path

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_random_audio(self) -> Optional[Path]:
        """
        Lists audio files in the background music directory and returns a random one.
        Supported formats: .wav, .mp3, .aac, .m4a.
        """
        if not self.bg_music_dir.exists():
            Messenger.warning(f"Audio directory not found: {self.bg_music_dir}")
            return None

        extensions = {".wav", ".mp3", ".aac", ".m4a"}
        bg_audios = [
            f for f in self.bg_music_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if not bg_audios:
            Messenger.warning(f"No audio files found in: {self.bg_music_dir}")
            return None

        selected = random.choice(bg_audios)
        Messenger.info(f"Selected background audio: {selected.name}")
        return selected
