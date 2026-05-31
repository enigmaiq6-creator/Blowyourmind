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
        top_headline: str = None
    ) -> None:
        """
        Renders a Remotion composition with provided data.
        """
        # 1. Prepare data file
        data_dir = remotion_path / "data"
        data_dir.mkdir(exist_ok=True)
        input_json = data_dir / "input.json"
        
        payload = {"words": words}
        if top_headline:
            payload["topHeadline"] = top_headline

        with open(input_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        Messenger.info(f"Rendering Remotion composition '{composition_id}'...")
        
        # 2. Run Remotion render
        import platform
        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
        
        # If output has no extension or is a pattern, it's a sequence
        is_sequence = output_path.suffix not in ['.mp4', '.webm', '.mov', '.mkv']
        
        # Remotion's getExtensionOfFilename splits on '.' and the path
        # has dots (e.g. C:\Users\Vanes\.gemini). Use temp dir with no dots.
        import tempfile, os
        staging_root = Path(tempfile.gettempdir()) / "remotion_render"
        staging_root.mkdir(parents=True, exist_ok=True)
        staging_output = staging_root / "frames" if is_sequence else staging_root / "subs.mp4"
        # Clean any previous staging files
        if staging_output.exists():
            if staging_output.is_dir():
                import shutil
                shutil.rmtree(staging_output)
            else:
                staging_output.unlink()
        
        cmd = [
            npx_cmd, "remotion", "render",
            "src/index.ts",
            composition_id,
            str(staging_output.absolute()),
            f"--props={input_json.absolute()}",
        ]

        if is_sequence:
            cmd.append("--sequence")
            cmd.append("--image-sequence-pattern=[frame].[ext]")
        else:
            cmd.append("--codec=vp9")

        try:
            subprocess.run(
                cmd,
                cwd=str(remotion_path),
                capture_output=True,
                text=True,
                check=True
            )
            # Copy from staging to final output path
            import shutil
            if staging_output.is_dir():
                if output_path.exists():
                    shutil.rmtree(output_path)
                shutil.copytree(staging_output, output_path)
            else:
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
