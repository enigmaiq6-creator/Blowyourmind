
import os
from pathlib import Path
from typing import Any, ClassVar, List, Optional, Type, TypeVar, Union
import concurrent.futures
import subprocess

from pydantic import BaseModel, PrivateAttr

from flows.image_content_generator.pipeline.prompt_base.models import VideoScript
from flows.image_content_generator.pipeline.prompt_shorts.manager import PromptManagerShorts
from flows.image_content_generator.pipeline.schemas import AudioAlignment, State, VideoOrientation
from flows.image_content_generator.pipeline.storage_csv import CsvStore

from tools.audio_generation.audio_tool import AudioTool
from tools.audio_generation.gemini import GeminiAudioGenerator
from tools.audio_generation.vertex_ai_tts import VertexAIAudioGenerator
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger
from tools.image_generation.gemini import GeminiImageGenerator
from tools.image_generation.vertex_ai import VertexAIImageGenerator
from tools.text_generation.gemini import GeminiTextGenerator
from tools.utils.text import slugify
from tools.utils.time import retry
from tools.social_media.facebook import FacebookTool
from tools.social_media.instagram import InstagramTool
from tools.video_generation.gemini import GeminiVideoGenerator
from tools.video_editing.ffmpeg import FFmpegTool
from tools.video_editing.whisper import WhisperTool
from tools.video_editing.remotion import RemotionTool
from tools.common.cost_tracker import CostTracker

T = TypeVar("T", bound=BaseModel)
PromptManager = PromptManagerShorts


class Pipeline(BaseModelTool):
    """
    Main pipeline for the Image Content Generator project.
    Orchestrates the creation of shorts using AI tools.
    """
    out_base: Path
    tracking_base: Optional[Path] = None
    resource_base: Path
    orientation: VideoOrientation
    mode: str = "fact_split"

    @property
    def _category(self) -> str | None:
        return self.mode if self.mode else "fact_split"

    _text_gen: Optional[GeminiTextGenerator] = PrivateAttr(default=None)
    _image_gen: Optional[Union[GeminiImageGenerator, VertexAIImageGenerator]] = PrivateAttr(default=None)
    _audio_gen: Optional[Union[GeminiAudioGenerator, VertexAIAudioGenerator]] = PrivateAttr(default=None)
    _ffmpeg: Optional[FFmpegTool] = PrivateAttr(default=None)
    _whisper: Optional[WhisperTool] = PrivateAttr(default=None)
    _prompt_manager: Optional[PromptManager] = PrivateAttr(default=None)
    _audio_tool: Optional[AudioTool] = PrivateAttr(default=None)
    _store: Optional[CsvStore] = PrivateAttr(default=None)
    _facebook: Optional[FacebookTool] = PrivateAttr(default=None)
    _instagram: Optional[InstagramTool] = PrivateAttr(default=None)
    _remotion: Optional[Any] = PrivateAttr(default=None)
    _video_gen: Optional[Any] = PrivateAttr(default=None)
    _cost_tracker: Optional[Any] = PrivateAttr(default=None)

    # Standard Output Directories
    IDEAS_DIR: ClassVar[str] = "ideas"
    IMAGES_DIR: ClassVar[str] = "images"
    AUDIOS_DIR: ClassVar[str] = "audios"
    CLIPS_DIR: ClassVar[str] = "clips"
    VIDEOS_DIR: ClassVar[str] = "videos"
    EDITIONS_DIR: ClassVar[str] = "editions"
    REMOTION_DIR: ClassVar[str] = "flows/image_content_generator/remotion"

    # Standard Output Files
    IDEA_JSON: ClassVar[str] = "idea.json"
    SCRIPT_JSON: ClassVar[str] = "script.json"
    RAW_VIDEO: ClassVar[str] = "raw_video.mp4"
    SUBTITLED_VIDEO: ClassVar[str] = "subtitled_video.mp4"
    REMOTION_VIDEO: ClassVar[str] = "remotion_overlay.mp4"
    PRO_SUBTITLED_VIDEO: ClassVar[str] = "pro_subtitled_video.mp4"
    FINAL_AUDIO: ClassVar[str] = "final_audio.wav"
    FINAL_SUBS: ClassVar[str] = "final_subs.srt"
    FINAL_VIDEO: ClassVar[str] = "final_video.mp4"

    # Standard Scene Patterns
    SCENE_IMAGE_PATTERN: ClassVar[str] = "scene_{}.png"
    SCENE_AUDIO_PATTERN: ClassVar[str] = "scene_{}.wav"
    SCENE_VIDEO_PATTERN: ClassVar[str] = "scene_{}.mp4"
    BATCH_AUDIO_PATTERN: ClassVar[str] = "batch_{}.wav"

    # Standard Resource Directories
    BG_MUSIC_DIR: ClassVar[str] = "bg-music"
    SFX_DIR: ClassVar[str] = "sfx"
    REFERENCES_DIR: ClassVar[str] = "reference"

    # Standard Tracking Files
    IDEAS_TRACKING_CSV: ClassVar[str] = "ideas_tracking.csv"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def store(self) -> CsvStore:
        if self._store is None:
            # If tracking_base is set, use it (git-tracked folder).
            # Otherwise fall back to out_base for local runs.
            base = self.tracking_base if self.tracking_base is not None else self.out_base
            base.mkdir(parents=True, exist_ok=True)
            csv_path = base / self.IDEAS_TRACKING_CSV
            self._store = CsvStore(csv_path=csv_path)
        return self._store

    @property
    def text_gen(self) -> GeminiTextGenerator:
        if self._text_gen is None:
            self._text_gen = GeminiTextGenerator()
        return self._text_gen

    @property
    def image_gen(self) -> Union[GeminiImageGenerator, VertexAIImageGenerator]:
        if self._image_gen is None:
            import os
            use_vertex = os.getenv("USE_VERTEX_AI_IMAGE", "false").lower() == "true"
            ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
            
            if use_vertex:
                project_id = os.getenv("GCP_PROJECT_ID")
                location = os.getenv("GCP_LOCATION", "us-central1")
                if not project_id:
                    raise ValueError("GCP_PROJECT_ID is required for Vertex AI.")
                self._image_gen = VertexAIImageGenerator(
                    project_id=project_id,
                    location=location,
                    aspect_ratio=ar_value
                )
            else:
                self._image_gen = GeminiImageGenerator(
                    aspect_ratio=ar_value,
                    reference_dir=self.resource_base / self.REFERENCES_DIR,
                )
        return self._image_gen

    @property
    def audio_gen(self) -> Union[GeminiAudioGenerator, VertexAIAudioGenerator]:
        if self._audio_gen is None:
            import os
            use_vertex = os.getenv("USE_VERTEX_AI_AUDIO", "false").lower() == "true"
            if use_vertex:
                self._audio_gen = VertexAIAudioGenerator()
            else:
                self._audio_gen = GeminiAudioGenerator(
                    voice_name=self.prompt_manager.VOICE_NAME
                )
        return self._audio_gen

    @property
    def ffmpeg(self) -> FFmpegTool:
        if self._ffmpeg is None:
            self._ffmpeg = FFmpegTool()
        return self._ffmpeg

    @property
    def video_gen(self) -> GeminiVideoGenerator:
        if self._video_gen is None:
            self._video_gen = GeminiVideoGenerator()
        return self._video_gen

    @property
    def cost_tracker(self) -> CostTracker:
        if self._cost_tracker is None:
            self._cost_tracker = CostTracker()
        return self._cost_tracker

    @property
    def whisper(self) -> WhisperTool:
        if self._whisper is None:
            self._whisper = WhisperTool()
        return self._whisper

    @property
    def audio_tool(self) -> AudioTool:
        if self._audio_tool is None:
            # Use mode-specific subdirectory if it exists, otherwise fall back to base
            mode_dir = self.resource_base / self.BG_MUSIC_DIR / self.mode
            if mode_dir.exists():
                bg_music_dir = mode_dir
            else:
                bg_music_dir = self.resource_base / self.BG_MUSIC_DIR
            self._audio_tool = AudioTool(bg_music_dir=bg_music_dir)
        return self._audio_tool

    @property
    def prompt_manager(self) -> PromptManager:
        if self._prompt_manager is None:
            self._prompt_manager = PromptManagerShorts()
        return self._prompt_manager

    @property
    def remotion(self) -> RemotionTool:
        if self._remotion is None:
            self._remotion = RemotionTool()
        return self._remotion

    @property
    def facebook(self) -> FacebookTool:
        if self._facebook is None:
            import os
            page_id = os.getenv("FACEBOOK_PAGE_ID")
            access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
            if not page_id or not access_token:
                raise ValueError("FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN are required.")
            self._facebook = FacebookTool(page_id=page_id, access_token=access_token)
        return self._facebook

    @property
    def instagram(self) -> InstagramTool:
        if self._instagram is None:
            import os
            page_id = os.getenv("FACEBOOK_PAGE_ID")
            access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
            if not page_id or not access_token:
                raise ValueError("FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN are required.")
            self._instagram = InstagramTool(page_id=page_id, access_token=access_token)
        return self._instagram

    def load_json(
        self,
        idea_id: int,
        filename: str,
        model_class: Type[T],
    ) -> T:
        """
        Loads and validates a JSON file from the idea's root directory.
        """
        path = self.get_idea_path(idea_id) / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {filename} for project {idea_id}")
        return model_class.model_validate_json(path.read_text(encoding="utf-8"))

    def load_script(self, idea_obj) -> VideoScript:
        category = getattr(idea_obj, "category", "fact_split")
        if category == "fact_split":
            from flows.image_content_generator.pipeline.prompt_shorts.fact_split.models import FactSplitHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, FactSplitHandler)
        return self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

    def save_json(self, idea_id: int, filename: str, data: BaseModel):
        """
        Saves a Pydantic model as a JSON file in the idea's root directory.
        """
        path = self.get_idea_path(idea_id) / filename
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_out_dir(self) -> Path:
        """
        Returns the absolute path to the base output directory.
        """
        self.out_base.mkdir(parents=True, exist_ok=True)
        return self.out_base

    def get_ideas_dir(self) -> Path:
        """
        Returns the absolute path to the global ideas folder.
        """
        path = self.get_out_dir() / self.IDEAS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_path(self, idea_id: int) -> Path:
        """
        Returns the absolute path to an idea's folder.
        """
        folder_name = f"idea_{idea_id:06d}"
        path = self.get_ideas_dir() / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_subdir(self, idea_id: int, subdir: str) -> Path:
        """
        Returns the absolute path to a subdirectory within an idea's folder
        """
        path = self.get_idea_path(idea_id) / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_asset_path(self, idea_id: int, subdir: str, filename: str) -> Path:
        """
        Returns the absolute path to a file within an idea's subdirectory.
        """
        return self.get_idea_subdir(idea_id, subdir) / filename

    def get_named_video_path(self, idea_id: int, title: str) -> Path:
        """
        Derives the path for the final named video based on the idea title.
        """
        title_slug = slugify(title)
        return self.get_idea_path(idea_id) / f"{title_slug}.mp4"

    def step1_generate_story(self, extra_avoid: str = ""):
        """
        Generate Concept & Script: Creates a cinematic idea and expands it into a storyboard.
        A/B TESTING (Fase 3): Generates two versions (A and B) with different hooks.
        """
        Messenger.info(f"\n--- Generating cinematic concept and script ({self.mode.upper()} mode) ---")

        # Merge tracking CSV titles with extra avoid list
        titles = self.store.get_all_titles()

        # 1. Selection of Manager based on mode
        idea_data, script, category = self.prompt_manager.generate_full_story(
            self.text_gen, titles_to_avoid=titles, extra_avoid=extra_avoid, mode=self.mode
        )

        # Cost tracking (approx 2000 tokens)
        self.cost_tracker.add_text_cost(2000)

        # --- FASE 3: A/B TESTING (Generar Gancho B) ---
        Messenger.info("   Generating alternative Hook B...")
        prompt_b = f"""
    You have the following video script:
    Title: {idea_data.title}
    Hook A (Original): {script.scenes[0].narration}

    Write a COMPLETELY DIFFERENT new Hook (Scene 1).
    If the original was aggressive/direct, make this one curious/mysterious (or vice versa).
    Must last maximum 3 seconds (15 words). Must be in English.
    Respond ONLY with the narrative text of the new hook, no quotes or extra text.
    """
        hook_b = self.text_gen.generate(prompt_b)
        self.cost_tracker.add_text_cost(200)

        # Create alternative version B
        import copy
        script_b = copy.deepcopy(script)
        script_b.scenes[0].narration = hook_b

        idea_b = copy.deepcopy(idea_data)
        idea_b.title = f"{idea_data.title} [Hook B]"

        # Save Idea B
        idea_obj_b = self.store.add_new_idea(idea_b.title, category)
        self.save_json(idea_obj_b.id, self.IDEA_JSON, idea_b)
        self.save_json(idea_obj_b.id, self.SCRIPT_JSON, script_b)
        self.store.update_state(idea_obj_b.id, State.SCRIPT_GENERATED)
        Messenger.info(f"   Hook B generated and queued as Idea {idea_obj_b.id}.")

        # Save Idea A (or the only one if stickman)
        idea_obj_a = self.store.add_new_idea(idea_data.title, category)
        self.save_json(idea_obj_a.id, self.IDEA_JSON, idea_data)
        self.save_json(idea_obj_a.id, self.SCRIPT_JSON, script)
        self.store.update_state(idea_obj_a.id, State.SCRIPT_GENERATED)

        Messenger.success(f"   Step 1 ready: State.SCRIPT_GENERATED finalized.")

    def step2_generate_images(self):
        """
        Generate Images: For fact_split tries Pexels first, falls back to Vertex AI Imagen.
        """
        idea_obj = self.store.get_first_by_state(State.SCRIPT_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.warning("Step 2 skipped: No idea in SCRIPT_GENERATED state.")
            return

        Messenger.info(f"Step 2 started: Generating images for '{idea_obj.title}'")
        Messenger.info(f"   Loading script for Idea {idea_obj.id}...")
        script = self.load_script(idea_obj)
        Messenger.info(f"   Script loaded. Scenes: {len(script.scenes)}")

        from tools.video_generation.pexels import PexelsTool
        pexels = PexelsTool()

        def fetch_one(subject_label: str, query: str, out_path):
            if out_path.exists():
                return True
            if pexels.fetch_image(query, out_path):
                return True
            Messenger.warning(f"   ⚠️ Pexels sin resultado para '{query}'. Generando con Vertex AI...")
            try:
                self.image_gen.generate_image(
                    prompt=f"A high-quality stock photo of {query}, professional photography, well-lit, centered subject, clean background",
                    output_path=out_path
                )
                return True
            except Exception as e:
                Messenger.error(f"   ❌ Vertex AI fallback falló para {subject_label}: {e}")
                return False

        def generate_one(scene):
            cat = getattr(idea_obj, "category", "")
            if cat == "fact_split":
                query_a = getattr(scene, "pexels_query_a", None) or ""
                query_b = getattr(scene, "pexels_query_b", None) or ""
                out_a = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "subject_a.png")
                out_b = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "subject_b.png")
                if query_a and not out_a.exists():
                    fetch_one(f"Subject A", query_a, out_a)
                if query_b and not out_b.exists():
                    fetch_one(f"Subject B", query_b, out_b)
                return

            action_prompt = getattr(scene, "image_prompt", None) or getattr(scene, "narration", f"A cinematic scene about {idea_obj.title}")
            out_name = f"scene_{scene.scene_number:02d}.png"
            out_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, out_name)
            if out_path.exists():
                return
            try:
                self.image_gen.generate_image(prompt=action_prompt, output_path=out_path)
            except Exception as e:
                Messenger.warning(f"   ⚠️ Primary image gen failed for scene {scene.scene_number}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(generate_one, scene) for scene in script.scenes]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    Messenger.error(f"   ❌ Image generation failed: {e}")
                    raise

        self.cost_tracker.add_image_cost(len(script.scenes))
        idea_obj.state = State.IMAGES_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2 ready: {State.IMAGES_GENERATED} finalized.\n")


    def step3_generate_audios(self):
        """Step 3: Generating voiceover audio for each scene."""
        idea_obj = self.store.get_first_by_state(State.IMAGES_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.warning("Step 3 skipped: No idea in IMAGES_GENERATED state.")
            return

        Messenger.info(f"\\n--- Step 3 started: Generating audios for '{idea_obj.title}' ---")
        script = self.load_script(idea_obj)

        for scene in script.scenes:
            sn = getattr(scene, 'scene_number', 1)
            audio_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(sn))
            
            if audio_path.exists() and audio_path.stat().st_size > 1024:
                Messenger.info(f"   Audio for scene {sn} already exists.")
                continue

            text = getattr(scene, 'narration', '')
            if not text:
                continue

            prompt = self.prompt_manager().get_audio_prompt(text, mode=self.mode)
            try:
                self.audio_gen().generate_audio(
                    prompt=prompt,
                    output_path=str(audio_path)
                )
                Messenger.success(f"   ✅ Audio {sn} generated.")
            except Exception as e:
                Messenger.error(f"   ❌ Failed to generate audio for scene {sn}: {e}")
                return

        idea_obj.state = State.AUDIO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 3 ready: {State.AUDIO_GENERATED} finalized.\\n")

    def step2b_generate_video_clips(self):
        """
        Step 2b: Componer cada escena con el estilo cinemático (Ken Burns)
        """
        idea_obj = self.store.get_first_by_state(State.AUDIO_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.warning("Step 2b skipped: No idea in AUDIO_GENERATED state.")
            return

        Messenger.info(f"\n--- Step 2b started: Rendering clips for '{idea_obj.title}' ---")
        script = self.load_script(idea_obj)
        
        from tools.video_editing.composer import compose_scene_from_image, get_duration

        width, height = (1080, 1920) if self.orientation == VideoOrientation.SHORT else (1920, 1080)
        
        for scene in script.scenes:
            sn = getattr(scene, 'scene_number', 1)
            audio_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(sn))
            img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, f"scene_{sn:02d}.png")
            out_clip = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, self.SCENE_VIDEO_PATTERN.format(sn))
            
            if not audio_path.exists() or not img_path.exists():
                Messenger.warning(f"   Missing audio or image for scene {sn}. Skipping.")
                continue
                
            if out_clip.exists() and out_clip.stat().st_size > 1024:
                Messenger.info(f"   Scene {sn} already exists.")
                continue
                
            audio_dur = get_duration(str(audio_path))
            
            text = getattr(scene, "narration", "")
            motion = 1 if text.strip().endswith("?") else (0 if sn == 1 or text.strip().endswith("!") else sn % 2)
            
            try:
                compose_scene_from_image(
                    image_path=str(img_path),
                    audio_path=str(audio_path),
                    duration=audio_dur,
                    output=str(out_clip),
                    pattern_idx=motion,
                    width=width,
                    height=height
                )
                Messenger.success(f"   ✅ Scene {sn} composed.")
            except Exception as e:
                Messenger.error(f"   ❌ Failed to compose scene {sn}: {e}")
                return

        idea_obj.state = State.CLIPS_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2b ready: {State.CLIPS_GENERATED} finalized.\n")

    def step4_generate_videos(self):
        """
        Step 4: Concatenate scenes with cinematic crossfades.
        """
        idea_obj = self.store.get_first_by_state(State.CLIPS_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.error("No clips ready for video generation.")
            return

        Messenger.info("\n--- Generating final concatenated video ---")
        script = self.load_script(idea_obj)
        
        scene_clips = []
        for scene in script.scenes:
            sn = getattr(scene, 'scene_number', 1)
            clip_path = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, self.SCENE_VIDEO_PATTERN.format(sn))
            if clip_path.exists():
                scene_clips.append(str(clip_path))
                
        if not scene_clips:
            Messenger.error("No scene clips found.")
            return
            
        concat_out = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        
        from tools.video_editing.composer import concat_videos_audio
        try:
            concat_videos_audio(scene_clips, str(concat_out), transition_duration=0.6)
            Messenger.success(f"   ✅ Concatenated video generated.")
        except Exception as e:
            Messenger.error(f"   ❌ Failed to concatenate: {e}")
            return
            
        idea_obj.state = State.VIDEO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 4 ready: {State.VIDEO_GENERATED} finalized.\n")

    def step5_generate_subtitles(self):
        """
        Step 5: ASS Subtitles + CTA + Final Compose
        """
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.error("No video ready for subtitle generation.")
            return

        Messenger.info("\n--- Applying cinematic subtitles and final effects ---")
        
        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        full_audio = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_AUDIO)
        ass_path = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, "subtitles.ass")
        final_out = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.SUBTITLED_VIDEO)
        
        width, height = (1080, 1920) if self.orientation == VideoOrientation.SHORT else (1920, 1080)
        
        import subprocess
        subprocess.run([
            'ffmpeg', '-y', '-i', str(raw_video), '-acodec', 'pcm_s16le', '-ar', '16000', str(full_audio)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        script = self.load_script(idea_obj)
        scene_texts = [getattr(s, 'narration', '') for s in script.scenes]
        full_original_text = ' '.join(scene_texts)
        
        from tools.video_editing.transcribe import transcribe_to_ass_word
        import re
        scene_end_words = []
        cum = 0
        for t in scene_texts:
            cum += len(re.findall(r"\b[\w']+\b", t))
            scene_end_words.append(cum)
        scene_word_boundaries = [e + 1 for e in scene_end_words[:-1]]
        
        try:
            transcribe_to_ass_word(str(full_audio), str(ass_path), correct_text=full_original_text, scene_word_boundaries=scene_word_boundaries)
            Messenger.success("   ✅ ASS subtitles generated.")
        except Exception as e:
            Messenger.error(f"   ❌ Failed to generate subtitles: {e}")
            return
            
        from tools.video_editing.composer import compose_final
        try:
            compose_final(str(raw_video), str(ass_path), str(final_out), width=width, height=height)
            Messenger.success("   ✅ Final composed video generated.")
        except Exception as e:
            Messenger.error(f"   ❌ Final composition failed: {e}")
            return
            
        idea_obj.state = State.VIDEO_SUBTITLED
        self.store.save(idea_obj)
        Messenger.success(f"Step 5 ready: {State.VIDEO_SUBTITLED} finalized.\n")
        
    def step5_pro_subtitles(self):
        self.step5_generate_subtitles()

    def step6_add_background_music(self):
        """
        Background Music: Adds a random background track to the subtitled video.
        """
        # 1. Retrieves subtitled video (PRO takes priority)
        idea_obj = self.store.get_first_by_state(State.VIDEO_PRO_SUBTITLED, category=self._category)
        is_pro = True
        if not idea_obj:
            idea_obj = self.store.get_first_by_state(State.VIDEO_SUBTITLED, category=self._category)
            is_pro = False
            
        if not idea_obj:
            Messenger.error("No subtitled video (Standard or PRO) found to add music.")
            return

        Messenger.info(f"\n--- Adding background music to {'PRO' if is_pro else 'Standard'} video ---")

        # 2. Prepares directories.
        subtitled_video = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, 
            self.PRO_SUBTITLED_VIDEO if is_pro else self.SUBTITLED_VIDEO
        )
        final_with_music = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO
        )

        # 3. Picks a random audio file
        selected_music = self.audio_tool.get_random_audio()
        if not selected_music:
            return

        # 4. Mixes it with low volume and looping.
        self.ffmpeg.add_background_music(
            subtitled_video,
            selected_music,
            final_with_music,
            bg_volume=0.18  # Subtle atmosphere
        )

        # 5. Updates state.
        idea_obj.state = State.VIDEO_MUSIC_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 6 ready: {State.VIDEO_MUSIC_GENERATED} finalized.\n")

    def step7_rename_final_video(self):
        """
        Rename Final Video: Renames the final video to match the script title.
        1. Retrieves the VIDEO_MUSIC_GENERATED idea.
        2. Prepares directories.
        3. Renames the final video.
        4. Updates state.
        """
        # 1. Retrieves VIDEO_MUSIC_GENERATED idea.
        idea_obj = self.store.get_first_by_state(State.VIDEO_MUSIC_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.error("No video with music found to rename.")
            return

        Messenger.info("\n--- Final Renaming: Naming video after script title ---")

        # 2. Prepares directories.
        final_video = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO
        )
        if not final_video.exists():
            Messenger.error(f"Final video with music not found: {final_video}")
            return

        # 3. Renames the final video.
        video_title = idea_obj.title if idea_obj.title else f"video_{idea_obj.id}"
        named_final = self.get_named_video_path(idea_obj.id, video_title)
        final_video.rename(named_final)

        # 4. Updates state.
        idea_obj.state = State.COMPLETED
        self.store.save(idea_obj)
        Messenger.success(f"Step 7 ready: {State.COMPLETED} finalized.\n")
        
        # FINAL COST REPORT
        self.cost_tracker.report()

    def generate_facebook_description(self, title: str) -> str:
        """
        Generates an ultra-short, high-engagement description for Facebook/Instagram Reels.
        Goal: drive comments and shares. 300k views in 25 days = need viral engagement.
        """
        import re
        title = re.sub(r"\s*\[Hook\s+[A-Z]\]", "", title, flags=re.IGNORECASE).strip()

        prompt = f"""
        You write viral Reels captions for "BlowYourMind". Caption for: "{title}"
        
        RULES (strict):
        1. MAX 2 lines. Ultra short. TikTok/Reels style.
        2. Start with a question or controversial statement that forces a comment.
        3. End with a call-to-action asking for an opinion (e.g. "Which side are you on? 👇").
        4. EXACTLY 10 hashtags. Always include: #BlowYourMind #MindBlowing #ViralReel
        5. NEVER explain the video. The caption should ADD mystery, not summarize.
        6. Use 1-2 emojis max.
        
        Examples of good captions:
        - "Wait till you see where this is going 🤯 Which country surprised you most? 👇"
        - "This changes EVERYTHING you know about geography. Are you team REALITY or team WHAT IF? 👇"
        - "Most people don't know this. And that's the problem. Comment your reaction 👇"
        
        Respond ONLY with the caption + hashtags.
        """
        try:
            return self.text_gen.generate(prompt).strip()
        except Exception as e:
            Messenger.warning(f"AI Description generation failed: {e}. Using fallback.")
            return f"🤯 {title}\n\nThis changes everything. Which side are you on? 👇\n\n#BlowYourMind #MindBlowing #ViralReel #GeographyFacts #WhatIf #DidYouKnow #Foryou #HiddenWorld #NatureIsCrazy #Mysteries"

    def step8_upload_to_facebook(self):
        """
        Upload to Facebook: Uploads all COMPLETED videos to the configured Facebook Page.
        1. Retrieves all COMPLETED ideas.
        2. For each idea:
            a. Generates an AI-optimized description.
            b. Finds the final named video.
            c. Uploads via FacebookTool.
            d. Updates state to UPLOADED.
        """
        # 1. Retrieves COMPLETED ideas.
        # We use a loop to process all completed ones as requested by the user
        while True:
            idea_obj = self.store.get_first_by_state(State.COMPLETED, category=self._category)
            if not idea_obj:
                break

            Messenger.info(f"\n--- Uploading Idea {idea_obj.id}: {idea_obj.title} ---")

            # 2. Finds the final named video.
            video_title = idea_obj.title if idea_obj.title else f"video_{idea_obj.id}"
            video_path = self.get_named_video_path(idea_obj.id, video_title)

            if not video_path.exists():
                Messenger.error(f"Final video not found: {video_path}")
                # We skip this one to avoid infinite loop or mark it as error?
                # For now, let's just mark it as something else or break
                break

            # 3. Generates optimized description
            Messenger.info("   Generating AI-optimized description...")
            import re
            cleaned_video_title = re.sub(r"\s*\[Hook\s+[A-Z]\]", "", video_title, flags=re.IGNORECASE).strip()
            description = self.generate_facebook_description(cleaned_video_title)

            # --- BLINDAJE CONTRA BANEOS (TODO ES TODO) ---
            # 1. AI Transparency (Mandatory Meta 2026)
            # 2. Disclaimer (For YMYL niches)
            # 3. Human Signature (To avoid pure Bot detection)
            transparency_footer = (
                "\n\n---\n"
                "🤖 **AI-Generated Content**: This video has been created with the support of Artificial Intelligence for entertainment and educational purposes.\n\n"
                "✨ Published by BlowYourMind.\n"
                "#MadeWithAI #AIContent #BlowYourMind #ViralVideo"
            )
            
            final_description = description + transparency_footer

            # 4. Uploads via FacebookTool.
            try:
                save_as_draft_env = os.getenv("SAVE_AS_DRAFT", "false").lower() in ("true", "1", "yes")
                
                if save_as_draft_env:
                    # Mode: Only Draft (Draft Mode manually enabled)
                    Messenger.info("   Draft Mode active. Performing single upload as draft...")
                    video_id = self.facebook.upload_video(
                        file_path=video_path,
                        description=final_description,
                        title=cleaned_video_title,
                        published=False
                    )
                    
                    if video_id:
                        # --- FASE 5: MULTILINGUAL CAPTIONS ---
                        try:
                            subs_srt = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_SUBS)
                            if subs_srt.exists():
                                Messenger.info("   Uploading native English captions to Facebook...")
                                self.facebook.upload_captions(video_id, subs_srt, locale="en_US")
                        except Exception as cap_e:
                            Messenger.warning(f"   ⚠️ Failed to upload English captions: {cap_e}")
                        
                        Messenger.info("   Skipping polemic comment (draft mode active).")
                else:
                    # Mode: Double Upload (Publish to Facebook + Save Draft for Instagram cross-posting)
                    Messenger.info("   Normal Mode. Performing double upload (Public Facebook Reel + Instagram Draft)...")
                    
                    # 1. PUBLIC Facebook Upload
                    Messenger.info("   Uploading public Facebook Reel...")
                    video_id = self.facebook.upload_video(
                        file_path=video_path,
                        description=final_description,
                        title=cleaned_video_title,
                        published=True
                    )
                    
                    if video_id:
                        # --- FASE 5: MULTILINGUAL CAPTIONS ---
                        try:
                            subs_srt = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_SUBS)
                            if subs_srt.exists():
                                Messenger.info("   Uploading native English captions to Facebook...")
                                self.facebook.upload_captions(video_id, subs_srt, locale="en_US")
                        except Exception as cap_e:
                            Messenger.warning(f"   ⚠️ Failed to upload English captions: {cap_e}")

                        # --- FASE 4: AUTO-COMENTARIO (Cebo de engagement) ---
                        Messenger.info("   Generating polemic auto-comment...")
                        prompt_comment = f"""
                        You are the creator of the series "BlowYourMind". You just uploaded a video titled: "{video_title}".
                        Write a short comment (1 line) in the form of a POLEMIC QUESTION to pin as the first comment of the video.
                        The goal is for people to debate or argue in the replies. 
                        Do not use hashtags. Be direct, a bit cynical, and very controversial.
                        """
                        try:
                            polemic_comment = self.text_gen.generate(prompt_comment).strip()
                            self.facebook.add_comment(video_id, polemic_comment)
                        except Exception as e:
                            Messenger.warning(f"Failed to generate or post auto-comment: {e}")
                    
                    # 2. DRAFT Upload (Instagram Cross-posting placeholder)
                    Messenger.info("   Uploading Instagram Draft placeholder to Facebook...")
                    draft_title = f"[Instagram Draft] {cleaned_video_title}"
                    try:
                        self.facebook.upload_video(
                            file_path=video_path,
                            description=final_description,
                            title=draft_title,
                            published=False
                        )
                    except Exception as draft_e:
                        # Don't fail the entire process if the secondary draft upload fails
                        Messenger.error(f"   ⚠️ Failed to upload Instagram draft placeholder: {draft_e}")

                    # 3. DIRECT Instagram Reels Upload (only if INSTAGRAM_PUBLISH=true)
                    instagram_publish = os.getenv("INSTAGRAM_PUBLISH", "false").lower() in ("true", "1", "yes")
                    if instagram_publish:
                        try:
                            Messenger.info("   Uploading direct to Instagram Reels...")
                            self.instagram.publish_reel(
                                file_path=video_path,
                                caption=final_description
                            )
                        except Exception as insta_e:
                            # Don't fail the entire process if Instagram upload fails
                            Messenger.error(f"   ⚠️ Failed to upload directly to Instagram: {insta_e}")
                    else:
                        Messenger.info(
                            "\n" +
                            "━" * 60 + "\n"
                            "📱 INSTAGRAM — MANUAL UPLOAD REQUIRED\n"
                            "━" * 60 + "\n"
                            f"  Video title : {cleaned_video_title}\n"
                            f"  Video file  : {video_path}\n"
                            "\n"
                            "  Steps to publish with translations:\n"
                            "  1. Open the Instagram app on your phone\n"
                            "  2. Create new Reel → select the video file\n"
                            "  3. Add caption, hashtags and activate 'Add Translation'\n"
                            "  4. Publish the Reel\n"
                            "━" * 60
                        )

                # 5. Updates state to UPLOADED.
                idea_obj.state = State.UPLOADED
                self.store.save(idea_obj)
                Messenger.success(f"   Idea {idea_obj.id} uploaded and marked as {State.UPLOADED}.\n")
            except Exception as e:
                Messenger.error(f"   Failed to upload Idea {idea_obj.id}: {str(e)}")
                break


