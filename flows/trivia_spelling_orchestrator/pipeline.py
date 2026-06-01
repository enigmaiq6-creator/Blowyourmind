"""Main pipeline orchestrator for spelling trivia video generation."""

import os
from pathlib import Path
from typing import Optional, Union

from tools.audio_generation.vertex_ai_tts import VertexAIAudioGenerator
from tools.audio_generation.gemini import GeminiAudioGenerator
from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator
from tools.video_editing.ffmpeg import FFmpegTool
from tools.video_editing.remotion import RemotionTool

from flows.trivia_spelling_orchestrator.schemas import TriviaVideoPlan
from flows.trivia_spelling_orchestrator.generator import SpellingTriviaGenerator
from flows.trivia_spelling_orchestrator.background_fetcher import BackgroundFetcher
from flows.trivia_spelling_orchestrator.tts_generator import TtsGenerator
from flows.trivia_spelling_orchestrator.video_assembler import VideoAssembler


REMOTION_DIR = Path("flows/image_content_generator/remotion")


class SpellingTriviaPipeline:
    def __init__(self, output_base: Path, resource_base: Optional[Path] = None):
        self.output_base = output_base
        self.resource_base = resource_base or Path("resources")

        self.text_gen = GeminiTextGenerator()
        self.ffmpeg = FFmpegTool()
        self.remotion = RemotionTool()

        use_vertex_tts = os.getenv("USE_VERTEX_AI_AUDIO", "true").lower() == "true"
        if use_vertex_tts:
            self.tts_engine = VertexAIAudioGenerator()
        else:
            voice = os.getenv("TTS_VOICE", "Charon")
            self.tts_engine = GeminiAudioGenerator(voice_name=voice)

        self.bg_fetcher = BackgroundFetcher()
        self.tts = TtsGenerator(engine=self.tts_engine)
        self.generator = SpellingTriviaGenerator(text_gen=self.text_gen)
        self.assembler = VideoAssembler(
            output_dir=output_base,
            remotion=self.remotion,
            ffmpeg=self.ffmpeg,
        )

        self.scripts_dir = output_base / "scripts"
        self.audios_dir = output_base / "audios"
        self.backgrounds_dir = output_base / "backgrounds"
        self.clips_dir = output_base / "clips"
        self.final_dir = output_base / "final"

    def run(self, plan: Optional[TriviaVideoPlan] = None) -> Path:
        Messenger.step_success("=== SPELLING TRIVIA VIDEO PIPELINE ===")

        if plan is None:
            plan = self.generator.generate()

        script_path = self.scripts_dir / "trivia_plan.json"
        self.generator.save_plan(plan, script_path)

        for q in plan.questions:
            self._process_question(q, plan)

        final_path = self._assemble_video(plan)
        Messenger.step_success(f"Pipeline complete! Video: {final_path}")
        return final_path

    def _process_question(self, q, plan: TriviaVideoPlan) -> None:
        q_id = q.id
        Messenger.info(f"\n--- Processing Question {q_id}/3 ---")

        bg_video = self.backgrounds_dir / f"q{q_id}_bg.mp4"
        bg_image = self.backgrounds_dir / f"q{q_id}_bg.png"
        video_path, image_path = self.bg_fetcher.resolve_background(
            vertex_prompt=q.visuals.vertex_ai_prompt,
            pexels_query=q.visuals.pexels_search_query,
            output_video=bg_video,
            output_image=bg_image,
        )

        intro_audio = self.audios_dir / f"q{q_id}_intro.wav"
        reveal_audio = self.audios_dir / f"q{q_id}_reveal.wav"
        silence_audio = self.audios_dir / f"q{q_id}_silence.wav"

        self.tts.generate(q.tts_scripts.intro_and_options, intro_audio)
        self.tts.generate(q.tts_scripts.reveal, reveal_audio)

        intro_duration_ms = int(self.ffmpeg.get_audio_duration(intro_audio) * 1000)
        reveal_duration_ms = int(self.ffmpeg.get_audio_duration(reveal_audio) * 1000)
        countdown_duration_ms = 5000

        # Generate 5s of silence for countdown so video/audio durations match
        silence_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
            "-t", str(countdown_duration_ms / 1000),
            str(silence_audio),
        ]
        self.ffmpeg._run(silence_cmd)

        intro_clip = self.clips_dir / f"q{q_id}_intro.mp4"
        countdown_clip = self.clips_dir / f"q{q_id}_countdown.mp4"
        reveal_clip = self.clips_dir / f"q{q_id}_reveal.mp4"

        bg_image_url = ""
        static_file_name = ""
        if image_path:
            remotion_img_dir = REMOTION_DIR / "public" / "temp_images"
            remotion_img_dir.mkdir(parents=True, exist_ok=True)
            dest = remotion_img_dir / f"q{q_id}_bg.png"
            import shutil
            shutil.copy2(image_path, dest)
            bg_image_url = f"http://localhost:3000/temp_images/q{q_id}_bg.png"
        elif video_path:
            remotion_vid_dir = REMOTION_DIR / "public" / "temp_images"
            remotion_vid_dir.mkdir(parents=True, exist_ok=True)
            dest = remotion_vid_dir / f"q{q_id}_bg.mp4"
            import shutil
            shutil.copy2(video_path, dest)
            static_file_name = f"temp_images/q{q_id}_bg.mp4"

        self.assembler.render_question_clip(
            question_id=q_id, step="question", plan=plan,
            audio_duration_ms=intro_duration_ms,
            output_path=intro_clip,
            background_image_url=bg_image_url,
            static_file_name=static_file_name,
        )

        self.assembler.render_question_clip(
            question_id=q_id, step="countdown", plan=plan,
            audio_duration_ms=countdown_duration_ms,
            output_path=countdown_clip,
            background_image_url=bg_image_url,
            static_file_name=static_file_name,
        )

        self.assembler.render_question_clip(
            question_id=q_id, step="reveal", plan=plan,
            audio_duration_ms=reveal_duration_ms,
            output_path=reveal_clip,
            background_image_url=bg_image_url,
            static_file_name=static_file_name,
        )

    def _assemble_video(self, plan: TriviaVideoPlan) -> Path:
        clip_paths = []
        audio_paths = []
        for q in plan.questions:
            q_id = q.id
            clip_paths.extend([
                self.clips_dir / f"q{q_id}_intro.mp4",
                self.clips_dir / f"q{q_id}_countdown.mp4",
                self.clips_dir / f"q{q_id}_reveal.mp4",
            ])
            audio_paths.extend([
                self.audios_dir / f"q{q_id}_intro.wav",
                self.audios_dir / f"q{q_id}_silence.wav",
                self.audios_dir / f"q{q_id}_reveal.wav",
            ])

        final_path = self.final_dir / "spelling_trivia_final_no_music.mp4"
        self.assembler.assemble_final_video(plan, clip_paths, audio_paths, final_path)

        # Add background music at low volume
        bg_music_path = self._generate_bg_music()
        final_with_music = self.final_dir / "spelling_trivia_final.mp4"
        self.ffmpeg.add_background_music(final_path, bg_music_path, final_with_music, bg_volume=0.08)

        return final_with_music

    def _generate_bg_music(self) -> Path:
        bg_dir = self.resource_base / "bg-music"
        bg_dir.mkdir(parents=True, exist_ok=True)
        bg_music = bg_dir / "ambient_loop.wav"
        if not bg_music.exists():
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "sine=frequency=220:duration=60",
                "-f", "lavfi", "-i", "sine=frequency=277:duration=60",
                "-f", "lavfi", "-i", "sine=frequency=329:duration=60",
                "-filter_complex",
                "[0:a]volume=0.3[a];[1:a]volume=0.2[b];[2:a]volume=0.15[c];[a][b][c]amix=inputs=3:duration=first,lowpass=f=500",
                str(bg_music),
            ]
            self.ffmpeg._run(cmd)
        return bg_music
