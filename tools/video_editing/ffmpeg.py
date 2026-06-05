import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class FFmpegTool(BaseModelTool):
    """
    Tool for basic video editing operations using FFmpeg.
    """

    def _run(self, args: List[str]) -> None:
        p = subprocess.run(args, capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {' '.join(args)}\nError: {p.stderr}")

    def split_audio(
        self,
        audio_in: Path,
        audio_out: Path,
        start_time: float,
        duration: float
    ) -> None:
        """
        Splits an audio file into a segment starting at start_time with duration.
        """
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(audio_in),
            "-t", str(duration),
            "-c:a", "pcm_s16le",
            "-v", "error",
            str(audio_out)
        ]
        self._run(cmd)

    def make_transition_video(
        self,
        img_a: Path,
        img_b: Path,
        out_path: Path,
        seconds: int = 4
    ) -> None:
        offset = max(0, seconds - 1)
        xfade_filter = f"[0:v][1:v]xfade=transition=slideright:duration=0.6:offset={offset},format=yuv420p"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(seconds), "-i", str(img_a),
            "-loop", "1", "-t", str(seconds), "-i", str(img_b),
            "-filter_complex", xfade_filter,
            "-t", str(seconds), str(out_path)
        ]
        self._run(cmd)

    def concat_videos(
        self,
        video_list: List[Path],
        out_path: Path,
    ) -> None:
        with tempfile.TemporaryDirectory() as td_str:
            td = Path(td_str)
            list_path = td / "files.txt"
            with open(list_path, "w", encoding="utf-8") as f:
                for v in video_list:
                    abs_v = v.absolute()
                    f.write(f"file '{abs_v}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(out_path)
            ]
            self._run(cmd)

    def concat_with_crossfade(
        self,
        video_list: List[Path],
        out_path: Path,
        transition_duration: float = 0.5,
    ) -> None:
        """
        Concatenates videos with crossfade transitions between scenes.
        Uses FFmpeg xfade for video. Audio is copied from first input
        since master audio is overlaid later in the pipeline.
        """
        if len(video_list) == 0:
            raise RuntimeError("No videos to concatenate.")
        if len(video_list) == 1:
            self._run(["ffmpeg", "-y", "-i", str(video_list[0]), "-c", "copy", str(out_path)])
            return

        inputs = []
        durations = []

        for v in video_list:
            dur = self.get_video_duration(v)
            durations.append(dur)
            inputs.extend(["-i", str(v)])

        total_duration = durations[0]

        transitions = ['fade', 'slideleft', 'slideright', 'fade']
        filter_parts = []
        for i in range(1, len(video_list)):
            offset = total_duration - transition_duration
            xfade_type = transitions[(i - 1) % len(transitions)]
            if i == 1:
                filter_parts.append(
                    f"[0:v][1:v]xfade=transition={xfade_type}:duration={transition_duration}:offset={offset}[v{i}]"
                )
            else:
                filter_parts.append(
                    f"[v{i-1}][{i}:v]xfade=transition={xfade_type}:duration={transition_duration}:offset={offset}[v{i}]"
                )
            total_duration = offset + durations[i]

        filter_complex = ";".join(filter_parts)
        last_idx = len(video_list) - 1

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", f"[v{last_idx}]",
            "-an",
            "-c:v", "libx264",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out_path)
        ]
        self._run(cmd)

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Retrieves the duration of an audio file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        try:
            output = subprocess.check_output(cmd, text=True).strip()
            if not output or output == "N/A":
                # Try getting from stream instead of format
                cmd[3] = "stream=duration"
                output = subprocess.check_output(cmd, text=True).strip().split('\n')[0]
            
            if not output or output == "N/A":
                return 0.0
            return float(output)
        except Exception:
            return 0.0

    def get_video_duration(self, video_path: Path) -> float:
        """
        Retrieves the duration of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        try:
            output = subprocess.check_output(cmd, text=True).strip()
            if not output or output == "N/A":
                return 0.0
            return float(output)
        except Exception:
            return 0.0

    def sync_video_and_audio(
        self,
        video_in: Path,
        audio_in: Path,
        video_out: Path
    ) -> None:
        """
        Synchronizes a video file to an audio file's duration.
        """
        audio_dur = self.get_audio_duration(audio_in)
        video_dur = self.get_video_duration(video_in)

        if video_dur <= 0:
            raise RuntimeError(f"Invalid video duration: {video_dur} for {video_in}")

        scale = audio_dur / video_dur
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-i", str(audio_in),
            "-filter_complex", f"[0:v]setpts={scale:.6f}*PTS[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-v", "error", str(video_out)
        ]
        self._run(cmd)

    def create_animated_scene_video(
        self,
        image_sequence_pattern: str,
        audio_in: Path,
        video_out: Path
    ) -> None:
        """
        Creates a video from an image sequence and synchronizes it with an audio track.
        Assumes 5 frames per scene to create a 'Flipbook' effect.
        """
        audio_dur = self.get_audio_duration(audio_in)
        # We have 5 frames. To make them span the whole audio duration:
        # framerate = total_frames / duration
        framerate = 5.0 / audio_dur if audio_dur > 0 else 1.0

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(framerate),
            "-i", image_sequence_pattern,
            "-i", str(audio_in),
            "-c:v", "libx264",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest", # End when the shortest stream ends (usually the video sequence ends exactly with audio)
            "-v", "error",
            str(video_out)
        ]
        self._run(cmd)

    def get_video_height(self, video_path: Path) -> int:
        """
        Retrieves the height of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=height",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, text=True).strip()
        return int(output)

    def get_video_width(self, video_path: Path) -> int:
        """
        Retrieves the width of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, text=True).strip()
        return int(output)

    def create_composite_scene_video(
        self,
        source_path: Path,
        audio_path: Path,
        out_path: Path,
        apply_glitch: bool = False
    ) -> None:
        """
        Creates a video clip for a scene using either an image or a video as source.
        Optionally applies a cyber-glitch transition for the first 0.5 seconds.
        """
        duration = self.get_audio_duration(audio_path)
        fps = 25
        is_video = source_path.suffix.lower() == ".mp4"

        # Glitch effect for transitions
        glitch_filter = ""
        if apply_glitch:
            # rgbashift separates colors like a VHS tape, noise adds static
            glitch_filter = ",rgbashift=rh=-15:bv=15:enable='between(t,0,0.5)',noise=alls=80:allf=t+u:enable='between(t,0,0.5)'"

        if is_video:
            # Scale to fill screen and crop excess (No black bars)
            vf_fill = "scale='max(1080,iw*1920/ih)':'max(1920,ih*1080/iw)':flags=lanczos,crop=1080:1920"
            cmd = [
                "ffmpeg", "-y", "-stream_loop", "-1",
                "-i", str(source_path),
                "-i", str(audio_path),
                "-t", str(duration),
                "-vf", f"{vf_fill},format=yuv420p{glitch_filter}",
                "-sws_flags", "lanczos",
                "-r", "30",
                "-fps_mode", "cfr",
                "-video_track_timescale", "30000",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-pix_fmt", "yuv420p",
                "-v", "error", str(out_path)
            ]
        else:
            # Scale to fill screen, crop excess, then apply Ken Burns (Increased Speed)
            vf_fill = "scale='max(1080,iw*1920/ih)':'max(1920,ih*1080/iw)':flags=lanczos,crop=1080:1920"
            z_expr = "1.0 + 0.0008*on" # Slower, smoother zoom
            pos_filter = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            
            # Pro Vignette Effect
            vignette = "vignette=PI/4"
            
            vf = f"{vf_fill},zoompan=z='{z_expr}':d=1:{pos_filter}:s=1080x1920,format=yuv420p,{vignette}{glitch_filter}"

            cmd = [
                "ffmpeg", "-y", "-loop", "1",
                "-i", str(source_path),
                "-i", str(audio_path),
                "-vf", vf,
                "-r", "30",
                "-fps_mode", "cfr",
                "-video_track_timescale", "30000",
                "-t", str(duration),
                "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-pix_fmt", "yuv420p",
                "-v", "error", str(out_path)
            ]
        
        self._run(cmd)

    def mix_sfx(self, base_audio: Path, sfx_audio: Path, out_path: Path, volume: float = 0.5) -> None:
        """
        Mixes a short Sound Effect (SFX) into the base audio stream, starting at 0s.
        Uses amix to combine them without extending the original audio duration.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", str(base_audio),
            "-i", str(sfx_audio),
            "-filter_complex", f"[0:a]volume=1.0[a0];[1:a]volume={volume}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "[a]",
            "-v", "error",
            str(out_path)
        ]
        self._run(cmd)

    def extract_audio(self, video_in: Path, audio_out: Path) -> None:
        """
        Extracts audio from a video file, optimized for Whisper STT.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-vn", "-ac", "1", "-ar", "16000",
            str(audio_out)
        ]
        self._run(cmd)
    def add_subtitles_to_video(
        self,
        video_in: Path,
        srt_path: Path,
        video_out: Path,
        font_size: int = 64
    ) -> None:
        """
        Adds subtitles to a video.
        """
        width = self.get_video_width(video_in)
        height = self.get_video_height(video_in)
        margin_v = int(height * 0.15)
        safe_srt = str(srt_path).replace("\\", "/").replace(":", "\\:")
        style = (
            f"PlayResX={width},PlayResY={height},"
            f"FontName=Impact,FontSize={font_size},PrimaryColour=&HFFFFFF,"
            f"OutlineColour=&H000000,BorderStyle=1,Outline=3,"
            f"Alignment=2,MarginV={margin_v}"
        )
        sub_filter = f"subtitles={safe_srt}:force_style='{style}'"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-vf", sub_filter,
            "-c:a", "copy",
            str(video_out)
        ]
        self._run(cmd)

    def add_background_music(
        self,
        video_in: Path,
        audio_bg: Path,
        video_out: Path,
        bg_volume: float = 0.12
    ) -> None:
        """
        Mixes a background audio track into a video.
        """
        filter_complex = (
            f"[0:a]volume=1.0[v_a]; "
            f"[1:a]volume={bg_volume}[bg_a]; "
            "[v_a][bg_a]amix=inputs=2:duration=first[fixed_a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-stream_loop", "-1",
            "-i", str(audio_bg),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[fixed_a]",
            "-c:v", "copy", "-c:a", "aac",
            str(video_out)
        ]
        self._run(cmd)

