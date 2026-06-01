"""Video assembly using Remotion and FFmpeg."""

import shutil
import tempfile
from pathlib import Path
from typing import Optional

from tools.video_editing.ffmpeg import FFmpegTool
from tools.video_editing.remotion import RemotionTool
from tools.common.messenger import Messenger
from tools.utils.text import slugify
from flows.trivia_spelling_orchestrator.schemas import TriviaVideoPlan


class VideoAssembler:
    REMOTION_DIR = Path("flows/image_content_generator/remotion")
    FPS = 30

    def __init__(
        self,
        output_dir: Path,
        remotion: Optional[RemotionTool] = None,
        ffmpeg: Optional[FFmpegTool] = None,
    ):
        self.output_dir = output_dir
        self.remotion = remotion or RemotionTool()
        self.ffmpeg = ffmpeg or FFmpegTool()

    def render_question_clip(
        self,
        question_id: int,
        step: str,
        plan: TriviaVideoPlan,
        audio_duration_ms: int,
        output_path: Path,
        background_image_url: str = "",
        video_url: str = "",
        static_file_name: str = "",
    ) -> Path:
        q = plan.questions[question_id - 1]
        props = {
            "question": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "correct_option": q.correct_answer,
            "trivia_step": step,
            "question_number": question_id,
            "total_questions": len(plan.questions),
            "audioDurationMs": audio_duration_ms,
        }
        if video_url:
            props["videoUrl"] = video_url
        if static_file_name:
            props["staticFileName"] = static_file_name
        if background_image_url:
            props["backgroundImageUrl"] = background_image_url

        composition_id = "SpellingTriviaQuiz"
        self.remotion.render_composition(
            remotion_path=self.REMOTION_DIR,
            output_path=output_path,
            composition_id=composition_id,
            props=props,
        )
        return output_path

    def assemble_final_video(
        self,
        plan: TriviaVideoPlan,
        clip_paths: list[Path],
        audio_paths: list[Path],
        final_path: Path,
    ) -> Path:
        final_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as td_str:
            td = Path(td_str)

            # Re-encode concat to ensure consistent timestamps (no -c copy)
            concat_file = td / "concat_list.txt"
            with open(concat_file, "w") as f:
                for clip in clip_paths:
                    f.write(f"file '{clip.resolve()}'\n")
            merged_video = td / "merged_video.mp4"
            concat_cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-vf", "setpts=PTS-STARTPTS",
                "-an",
                "-v", "error",
                str(merged_video),
            ]
            self.ffmpeg._run(concat_cmd)

            # Merge audio tracks sequentially
            merged_audio = td / "merged_audio.wav"
            concat_audio_cmd = [
                "ffmpeg", "-y",
            ]
            for ap in audio_paths:
                concat_audio_cmd.extend(["-i", str(ap)])
            filter_parts = []
            for i in range(len(audio_paths)):
                filter_parts.append(f"[{i}:a]")
            audio_filter = "".join(filter_parts) + f"concat=n={len(audio_paths)}:v=0:a=1[a]"
            concat_audio_cmd.extend(["-filter_complex", audio_filter, "-map", "[a]", str(merged_audio)])
            self.ffmpeg._run(concat_audio_cmd)

            # Replace audio track (no -shortest: let audio play fully, pad video if needed)
            replace_audio_cmd = [
                "ffmpeg", "-y",
                "-i", str(merged_video),
                "-i", str(merged_audio),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-af", "apad",
                "-shortest",
                "-v", "error",
                str(final_path),
            ]
            self.ffmpeg._run(replace_audio_cmd)

        Messenger.success(f"Final video assembled: {final_path}")
        return final_path
