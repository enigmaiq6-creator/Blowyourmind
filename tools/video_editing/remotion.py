import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger

class RemotionTool(BaseModelTool):
    """
    Tool for rendering videos using Remotion CLI.
    """

    def render_subtitles(
        self,
        remotion_path: Path,
        output_path: Path,
        words: List[Dict[str, Any]],
        composition_id: str = "Subtitles",
        top_headline: str = None,
        level_markers: List[Dict[str, Any]] = None
    ) -> None:
        """
        Renders a Remotion composition as an MP4 video (no alpha).
        The Subtitles component renders text on a green (#00FF00) background.
        ffmpeg colorkey makes green transparent during overlay.
        Pass level_markers for 7 Levels mode (level badges, progress bar).
        """
        # 1. Prepare data file
        data_dir = remotion_path / "data"
        data_dir.mkdir(exist_ok=True)
        input_json = data_dir / "input.json"
        
        payload = {"words": words}
        if top_headline:
            payload["topHeadline"] = top_headline
        if level_markers:
            payload["levelMarkers"] = level_markers

        with open(input_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        Messenger.info(f"Rendering Remotion composition '{composition_id}'...")
        
        import platform
        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"

        import tempfile
        staging_root = Path(tempfile.gettempdir()) / "remotion_render"
        staging_root.mkdir(parents=True, exist_ok=True)
        staging_output = staging_root / "subs_overlay.mp4"
        if staging_output.exists():
            staging_output.unlink()
        
        cmd = [
            npx_cmd, "remotion", "render",
            "src/index.ts",
            composition_id,
            str(staging_output.absolute()),
            f"--props={input_json.absolute()}",
            "--codec=h264",
            "-y"
        ]

        try:
            subprocess.run(
                cmd,
                cwd=str(remotion_path),
                capture_output=True,
                text=True,
                check=True
            )
            import shutil
            shutil.copy2(staging_output, output_path)
            Messenger.success(f"Remotion render completed: {output_path.name}")
        except subprocess.CalledProcessError as e:
            Messenger.error(f"Remotion failed: {e.stderr}")
            raise RuntimeError(f"Remotion rendering failed: {e.stderr}")

    def render_composition(
        self,
        remotion_path: Path,
        output_path: Path,
        composition_id: str,
        props: Dict[str, Any]
    ) -> None:
        """
        Renders any Remotion composition with the given props.
        Uses a unique temp file per call so parallel renders don't collide.
        """
        import tempfile, os, platform
        input_json = Path(tempfile.gettempdir()) / f"remotion_props_{composition_id.lower()}_{os.getpid()}_{id(props)}.json"
        
        with open(input_json, "w", encoding="utf-8") as f:
            json.dump(props, f, indent=2)

        Messenger.info(f"Rendering Remotion composition '{composition_id}'...")
        
        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
        
        cmd = [
            npx_cmd, "remotion", "render",
            "src/index.ts",
            composition_id,
            str(output_path.absolute()),
            f"--props={input_json.absolute()}",
            "--codec=h264",
            "-y"
        ]

        try:
            subprocess.run(
                cmd,
                cwd=str(remotion_path),
                capture_output=True,
                text=True,
                check=True
            )
            Messenger.success(f"Remotion render completed: {output_path.name}")
        except subprocess.CalledProcessError as e:
            Messenger.error(f"Remotion failed: {e.stderr}")
            raise RuntimeError(f"Remotion rendering failed: {e.stderr}")
