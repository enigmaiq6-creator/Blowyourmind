
import os
from pathlib import Path
from typing import Any, ClassVar, List, Optional, Type, TypeVar, Union
import concurrent.futures
import subprocess

from pydantic import BaseModel, PrivateAttr

from flows.image_content_generator.pipeline.prompt_base.models import VideoScript
from flows.image_content_generator.pipeline.prompt_longs.manager import PromptManagerLongs
from flows.image_content_generator.pipeline.prompt_shorts.manager import PromptManagerShorts
from flows.image_content_generator.pipeline.prompt_shorts.stories.stickman_manager import StickmanNoirManager
from flows.image_content_generator.pipeline.schemas import AudioAlignment, State, VideoOrientation
from flows.image_content_generator.pipeline.storage_csv import CsvStore
from tools.audio_generation.audio_tool import AudioTool
from tools.audio_generation.gemini import GeminiAudioGenerator
from tools.audio_generation.vertex_ai_tts import VertexAIAudioGenerator
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger
from tools.image_generation.gemini import GeminiImageGenerator
from tools.image_generation.jimeng import JimengImageGenerator
from tools.image_generation.pollinations import PollinationsImageGenerator
from tools.image_generation.vertex_ai import VertexAIImageGenerator
from tools.image_generation.midjourney import ImageTask
from tools.text_generation.gemini import GeminiTextGenerator
from tools.utils.text import slugify
from tools.utils.time import retry
from tools.social_media.facebook import FacebookTool
from tools.video_generation.gemini import GeminiVideoGenerator
from tools.video_editing.ffmpeg import FFmpegTool
from tools.video_editing.whisper import WhisperTool
from tools.video_editing.remotion import RemotionTool
from tools.common.cost_tracker import CostTracker

T = TypeVar("T", bound=BaseModel)
PromptManager = Union[PromptManagerShorts, PromptManagerLongs]


class Pipeline(BaseModelTool):
    """
    Main pipeline for the Image Content Generator project.
    Orchestrates the creation of shorts using AI tools.
    """
    out_base: Path
    resource_base: Path
    orientation: VideoOrientation
    mode: str = "standard"

    _text_gen: Optional[GeminiTextGenerator] = PrivateAttr(default=None)
    _image_gen: Optional[Union[GeminiImageGenerator, VertexAIImageGenerator]] = PrivateAttr(default=None)
    _jimeng_gen: Optional[JimengImageGenerator] = PrivateAttr(default=None)
    _pollinations_gen: Optional[PollinationsImageGenerator] = PrivateAttr(default=None)
    _audio_gen: Optional[Union[GeminiAudioGenerator, VertexAIAudioGenerator]] = PrivateAttr(default=None)
    _ffmpeg: Optional[FFmpegTool] = PrivateAttr(default=None)
    _whisper: Optional[WhisperTool] = PrivateAttr(default=None)
    _prompt_manager: Optional[PromptManager] = PrivateAttr(default=None)
    _stickman_manager: Optional[StickmanNoirManager] = PrivateAttr(default=None)
    _audio_tool: Optional[AudioTool] = PrivateAttr(default=None)
    _store: Optional[CsvStore] = PrivateAttr(default=None)
    _facebook: Optional[FacebookTool] = PrivateAttr(default=None)
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
    REMOTION_VIDEO: ClassVar[str] = "remotion_frames"
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
    REFERENCES_DIR: ClassVar[str] = "reference"

    # Standard Tracking Files
    IDEAS_TRACKING_CSV: ClassVar[str] = "ideas_tracking.csv"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def store(self) -> CsvStore:
        if self._store is None:
            csv_path = self.out_base / self.IDEAS_TRACKING_CSV
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
    def jimeng_gen(self) -> JimengImageGenerator:
        if self._jimeng_gen is None:
            import os
            ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
            self._jimeng_gen = JimengImageGenerator(aspect_ratio=ar_value)
        return self._jimeng_gen

    @property
    def pollinations_gen(self) -> PollinationsImageGenerator:
        if self._pollinations_gen is None:
            ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
            self._pollinations_gen = PollinationsImageGenerator(aspect_ratio=ar_value)
        return self._pollinations_gen

    @property
    def cost_tracker(self) -> CostTracker:
        if self._cost_tracker is None:
            self._cost_tracker = CostTracker()
        return self._cost_tracker

    @property
    def stickman_manager(self) -> StickmanNoirManager:
        if self._stickman_manager is None:
            self._stickman_manager = StickmanNoirManager()
        return self._stickman_manager

    @property
    def whisper(self) -> WhisperTool:
        if self._whisper is None:
            self._whisper = WhisperTool()
        return self._whisper

    @property
    def audio_tool(self) -> AudioTool:
        if self._audio_tool is None:
            bg_music_dir = self.resource_base / self.BG_MUSIC_DIR
            self._audio_tool = AudioTool(bg_music_dir=bg_music_dir)
        return self._audio_tool

    @property
    def prompt_manager(self) -> PromptManager:
        if self._prompt_manager is None:
            if self.orientation == VideoOrientation.SHORT:
                self._prompt_manager = PromptManagerShorts()
            elif self.orientation == VideoOrientation.LONG:
                self._prompt_manager = PromptManagerLongs()
            else:
                raise ValueError(f"Orientation {self.orientation} not supported.")
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
        """
        Dynamically loads the script JSON using the correct Pydantic model
        based on the idea's category.
        """
        if getattr(idea_obj, "category", "") == "geography":
            from flows.image_content_generator.pipeline.prompt_shorts.geography.models import GeographyHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, GeographyHandler)
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
        if self.mode == "stickman":
            idea_data, script = self.stickman_manager.generate_full_story(
                self.text_gen, titles_to_avoid=titles, extra_avoid=extra_avoid
            )
            category = "stickman_noir"
        else:
            idea_data, script, category = self.prompt_manager.generate_full_story(
                self.text_gen, titles_to_avoid=titles, extra_avoid=extra_avoid, mode=self.mode
            )

        # Cost tracking (approx 2000 tokens)
        self.cost_tracker.add_text_cost(2000)

        # --- FASE 3: A/B TESTING (Generar Gancho B) ---
        # Skip A/B testing for stickman for now to keep it simple and focused on quality
        if self.mode != "stickman":
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
        Generate Images: Batch Image Generation (Gemini).
        Generates 3 frames per scene for Flipbook animation.
        """
        idea_obj = self.store.get_first_by_state(State.SCRIPT_GENERATED)
        if not idea_obj:
            Messenger.warning("Step 2 skipped: No idea in SCRIPT_GENERATED state.")
            return

        Messenger.info(f"Step 2 started: Generating Animated Frames for '{idea_obj.title}'")
        Messenger.info(f"   Loading script for Idea {idea_obj.id}...")
        script = self.load_script(idea_obj)
        Messenger.info(f"   Script loaded. Scenes: {len(script.scenes)}")

        # Determine if we are in Riddle mode or Video mode
        is_riddle = idea_obj.title.lower().startswith("acertijo") or "interaction" in str(type(idea_obj)).lower()
        
        # 5 Frames per scene for high-quality "Flipbook" animation (Videos only)
        # 1 Frame per scene for Riddles/Interaction Images
        frames_per_scene = 1 if is_riddle else 5
        
        tasks: List[ImageTask] = []
        for scene in script.scenes:
            # Revertido a 1 imagen pura y estática por escena
            action_prompt = getattr(scene, "image_prompt", None) or getattr(scene, "narration", f"A cinematic scene about {idea_obj.title}")
            out_name = f"scene_{scene.scene_number:02d}.png"
            out_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, out_name)
            tasks.append(
                ImageTask(
                    prompt=action_prompt,
                    output_path=out_path
                )
            )

        # Ensure directory exists
        if tasks:
            tasks[0].output_path.parent.mkdir(parents=True, exist_ok=True)

        # Distribute load: Vertex AI vs free alternative (Pollinations/Jimeng)
        # VERTEX_IMAGE_RATIO = percentage of images to send to Vertex AI (default 20%)
        # Set to 0 to use only the free alternative, 100 for only Vertex AI
        jimeng_key = os.getenv("JIMENG_API_KEY")
        use_jimeng = bool(jimeng_key)
        alt_name = "Jimeng" if use_jimeng else "Pollinations"
        alt_gen = self.jimeng_gen if use_jimeng else self.pollinations_gen

        vertex_ratio = int(os.getenv("VERTEX_IMAGE_RATIO", "20"))
        vertex_ratio = max(0, min(100, vertex_ratio))

        if vertex_ratio >= 100:
            vertex_tasks = list(tasks)
            alt_tasks = []
            Messenger.info(f"All {len(tasks)} images to Vertex AI (ratio=100%)")
        elif vertex_ratio <= 0:
            vertex_tasks = []
            alt_tasks = list(tasks)
            Messenger.info(f"All {len(tasks)} images to {alt_name} (ratio=0%)")
        elif len(tasks) > 1:
            split_idx = max(1, len(tasks) * vertex_ratio // 100)
            vertex_tasks = tasks[:split_idx]
            alt_tasks = tasks[split_idx:]
            Messenger.info(f"Load balancing: {len(vertex_tasks)} to Vertex AI ({vertex_ratio}%), {len(alt_tasks)} to {alt_name}")
        else:
            vertex_tasks = list(tasks)
            alt_tasks = []

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            if vertex_tasks:
                futures.append(executor.submit(self.image_gen.generate_images, vertex_tasks))
            if alt_tasks:
                futures.append(executor.submit(alt_gen.generate_images, alt_tasks))
            for f in concurrent.futures.as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    Messenger.warning(f"One generator failed: {e}")
        self.cost_tracker.add_image_cost(len(tasks))

        Messenger.step_success(
            f"📸 IMAGES: {len(vertex_tasks)} Vertex AI + {len(alt_tasks)} {alt_name} (ratio={vertex_ratio}%)"
        )

        # Update State
        idea_obj.state = State.IMAGES_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2 ready: {State.IMAGES_GENERATED} finalized.\n")

    def step2b_generate_video_clips(self):
        """
        Step 2b: Render video clips using enhanced Remotion MapRender (3D satellite maps)
        with GeoJSON country borders, neon glow, AI image scenes, and tile fallback.
        Falls back to Pexels/Pixabay stock video or Ken Burns image animation.
        """
        idea_obj = self.store.get_first_by_state(State.IMAGES_GENERATED)
        if not idea_obj:
            Messenger.warning("Step 2b skipped: No idea in IMAGES_GENERATED state.")
            return

        Messenger.info(f"\n--- Step 2b started: Rendering clips for '{idea_obj.title}' ---")
        script = self.load_script(idea_obj)
        
        from tools.video_generation.pexels import PexelsTool
        from tools.video_generation.pixabay import PixabayTool
        pexels_tool = PexelsTool()
        pixabay_tool = PixabayTool()

        # Ensure remotion/public/temp_images/ exists for AI image scenes
        remotion_public_images = Path(self.REMOTION_DIR) / "public" / "temp_images"
        remotion_public_images.mkdir(parents=True, exist_ok=True)

        def _get_camera_attr(scene, attr, default):
            """Extract camera attribute from flat field or nested MapCamera."""
            flat_val = getattr(scene, f"camera_{attr}", None)
            if flat_val and flat_val != 0.0:
                return flat_val
            camera = getattr(scene, "camera", None)
            if camera:
                return getattr(camera, attr, default)
            return default

        def process_scene(scene):
            clip_filename = self.SCENE_VIDEO_PATTERN.format(scene.scene_number)
            clip_path = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, clip_filename)
            img_filename = f"scene_{scene.scene_number:02d}.png"
            img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, img_filename)

            if clip_path.exists() and clip_path.stat().st_size > 10240:
                Messenger.info(f"   Scene {scene.scene_number} clip already exists. Skipping.")
                return True

            visual_type = getattr(scene, "visual_type", "stock_video")
            query = getattr(scene, "pexels_query", "")
            is_geography_mode = getattr(idea_obj, "category", "") == "geography"

            # Pre-extract pins, vignettes and camera_path for geography scenes
            map_pins = getattr(scene, "map_pins", []) if is_geography_mode else []
            vignettes = getattr(scene, "vignettes", []) if is_geography_mode else []
            camera_path_raw = getattr(scene, "camera_path", []) if is_geography_mode else []
            pins_data = []
            for p in map_pins:
                pins_data.append({
                    "latitude": p.latitude if hasattr(p, "latitude") else 0,
                    "longitude": p.longitude if hasattr(p, "longitude") else 0,
                    "label": p.label if hasattr(p, "label") else "",
                    "value": p.value if hasattr(p, "value") else "",
                })
            vignettes_data = []
            for v in vignettes:
                vignettes_data.append({
                    "icon": v.icon if hasattr(v, "icon") else "📊",
                    "title": v.title if hasattr(v, "title") else "",
                    "value": v.value if hasattr(v, "value") else "",
                })
            camera_path_data = []
            for wp in camera_path_raw:
                camera_path_data.append({
                    "latitude": wp.latitude if hasattr(wp, "latitude") else 0,
                    "longitude": wp.longitude if hasattr(wp, "longitude") else 0,
                    "zoom": wp.zoom if hasattr(wp, "zoom") else 5,
                    "pitch": wp.pitch if hasattr(wp, "pitch") else 40,
                    "bearing": wp.bearing if hasattr(wp, "bearing") else 0,
                })

            # ── Remotion-enhanced rendering (geography mode) ──
            if is_geography_mode and visual_type == "map_3d":
                Messenger.info(f"   🗺️ Scene {scene.scene_number}: Rendering 3D satellite map via Remotion...")
                
                lat = _get_camera_attr(scene, "latitude", 4.570868)
                lon = _get_camera_attr(scene, "longitude", -74.297333)
                zoom = _get_camera_attr(scene, "zoom", 5.2)
                pitch = _get_camera_attr(scene, "pitch", 45.0)
                bearing = _get_camera_attr(scene, "bearing", -10.0)
                
                highlight_region = getattr(scene, "highlight_region", "none")
                arrow_direction = getattr(scene, "arrow_direction", "none")
                floating_label = getattr(scene, "floating_label", "none")
                
                props = {
                    "visualType": "map_3d",
                    "latitude": lat,
                    "longitude": lon,
                    "zoom": zoom,
                    "pitch": pitch,
                    "bearing": bearing,
                    "highlightRegion": highlight_region,
                    "arrowDirection": arrow_direction,
                    "floatingLabel": floating_label,
                    "pins": pins_data,
                    "vignettes": vignettes_data,
                    "cameraPath": camera_path_data,
                    "audioDurationMs": 10000,
                }
                
                try:
                    remotion_root = Path(self.REMOTION_DIR)
                    self.remotion.render_composition(
                        remotion_path=remotion_root,
                        output_path=clip_path,
                        composition_id="MapRender",
                        props=props
                    )
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                except Exception as remotion_e:
                    Messenger.error(f"   ❌ Remotion MapRender failed: {remotion_e}")
                    Messenger.warning("   ⚠️ Fallback: trying AI image render via Remotion...")
                    visual_type = "ai_image"

            # ── AI Image scene (rendered via Remotion with 3D card effect) ──
            if is_geography_mode and visual_type == "ai_image":
                Messenger.info(f"   🎨 Scene {scene.scene_number}: Generating AI image and rendering via Remotion...")
                
                ai_img_filename = f"scene_{scene.scene_number:02d}_ai.jpg"
                ai_img_dest = remotion_public_images / ai_img_filename
                
                if not ai_img_dest.exists():
                    img_prompt = getattr(scene, "image_prompt", None) or getattr(scene, "narration", "A cinematic geography scene")
                    try:
                        from tools.image_generation.pollinations import PollinationsImageGenerator
                        pollinations = PollinationsImageGenerator(aspect_ratio="9:16")
                        pollinations.generate_image(
                            prompt=img_prompt,
                            output_path=ai_img_dest
                        )
                    except Exception:
                        try:
                            from tools.image_generation.gemini import GeminiImageGenerator
                            gemini_img = GeminiImageGenerator(
                                aspect_ratio="9:16",
                                reference_dir=Path(self.resource_base) / self.REFERENCES_DIR
                            )
                            gemini_img.generate_image(
                                prompt=img_prompt,
                                output_path=ai_img_dest
                            )
                        except Exception as img_e:
                            Messenger.warning(f"   ⚠️ AI image gen failed: {img_e}. Using existing image.")
                            if img_path.exists():
                                import shutil
                                shutil.copy2(img_path, ai_img_dest)
                
                if not ai_img_dest.exists() and img_path.exists():
                    import shutil
                    shutil.copy2(img_path, ai_img_dest)
                
                props = {
                    "visualType": "ai_image",
                    "imageFile": ai_img_filename,
                    "latitude": 0,
                    "longitude": 0,
                    "zoom": 0,
                    "pitch": 0,
                    "bearing": 0,
                    "highlightRegion": "none",
                    "arrowDirection": "none",
                    "floatingLabel": "none",
                    "pins": [],
                    "vignettes": vignettes_data if vignettes_data else [],
                    "audioDurationMs": 8000,
                }
                
                try:
                    remotion_root = Path(self.REMOTION_DIR)
                    self.remotion.render_composition(
                        remotion_path=remotion_root,
                        output_path=clip_path,
                        composition_id="MapRender",
                        props=props
                    )
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                except Exception as remotion_e:
                    Messenger.error(f"   ❌ Remotion AI image render failed: {remotion_e}")
                    Messenger.warning("   ⚠️ Falling back to Ken Burns animation...")

            # ── Stock video search (Pexels / Pixabay) ──
            if visual_type != "ai_image":
                if pexels_tool.fetch_video(query, clip_path):
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True

                if pixabay_tool.fetch_video(query, clip_path):
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                
                Messenger.warning(f"   ⚠️ APIs failed for query '{query}'. Falling back to AI Image.")
            else:
                Messenger.info(f"   🎨 Scene {scene.scene_number}: 'ai_image' type. Skipping stock video search.")

            # ── Fallback: Ken Burns image animation ──
            if not img_path.exists() or img_path.stat().st_size < 1024:
                Messenger.error(f"   ❌ Scene {scene.scene_number} missing image and stock video APIs failed. CRITICAL.")
                return False
                
            Messenger.info(f"   🎬 Generating Ken Burns fallback for Scene {scene.scene_number}...")
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-loop", "1", "-i", str(img_path),
                        "-vf", "zoompan=z='min(zoom+0.0005,1.1)':d=150:s=1080x1920",
                        "-c:v", "libx264", "-t", "6", "-pix_fmt", "yuv420p", "-y", str(clip_path)
                    ],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
            except Exception as ffmpeg_e:
                Messenger.error(f"   ❌ FFmpeg fallback failed: {ffmpeg_e}")
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(process_scene, script.scenes))

        if not all(results):
            Messenger.error("   ❌ One or more video clips failed. Stopping pipeline.")
            return

        idea_obj.state = State.CLIPS_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2b ready: {State.CLIPS_GENERATED} finalized.\n")

    @retry(max_attempts=3)
    def step3_generate_audios(self):
        """
        Generate Audio: Batched AI-Guided Batching (Whisper + Gemini).
        Processes scenes in groups of 10 for maximum stability and alignment precision.
        """
        # Ambos modos (Stickman y Curiosidades) pasan ahora por step2b
        target_state = State.CLIPS_GENERATED
        idea_obj = self.store.get_first_by_state(target_state)
        if not idea_obj:
            Messenger.error(f"No ideas ready for audio generation (target: {target_state}).")
            return

        Messenger.info("\n--- Generating batched audio for the script ---")
        script_data = self.load_script(idea_obj)

        total_scenes = len(script_data.scenes)
        batch_size = 15

        for start_idx in range(0, total_scenes, batch_size):
            try:
                end_idx = min(start_idx + batch_size, total_scenes)
                chunk = script_data.scenes[start_idx:end_idx]
                batch_num = (start_idx // batch_size) + 1

                Messenger.info(f"Processing Batch {batch_num}: Scenes {start_idx + 1} to {end_idx}")

                # 1. Skip if all scenes in batch already exist
                missing_any = False
                for j in range(len(chunk)):
                    scene_num = start_idx + j + 1
                    out_path = self.get_idea_asset_path(
                        idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(scene_num)
                    )
                    if not out_path.exists():
                        missing_any = True
                        break

                if not missing_any:
                    Messenger.info(f"Skipping Batch {batch_num}: All audio files exist.")
                    continue

                # 2. Synthesize chunk audio
                chunk_filename = self.BATCH_AUDIO_PATTERN.format(batch_num)
                chunk_audio_path = self.get_idea_asset_path(
                    idea_obj.id, self.AUDIOS_DIR, chunk_filename
                )

                Messenger.info(f"Synthesizing audio for Batch {batch_num}...")
                chunk_text = "\n\n".join([s.narration for s in chunk])
                
                # BLINDAJE: Si usamos Vertex AI (TTS literal), enviamos SOLO el texto.
                # Si usamos Gemini, enviamos el prompt completo con instrucciones de tono.
                from tools.audio_generation.vertex_ai_tts import VertexAIAudioGenerator
                if isinstance(self.audio_gen, VertexAIAudioGenerator):
                    self.audio_gen.text_to_speech(chunk_text, chunk_audio_path)
                else:
                    formatted_audio = self.prompt_manager.get_audio_prompt(chunk_text, mode=self.mode)
                    self.audio_gen.text_to_speech(formatted_audio, chunk_audio_path)
                
                self.cost_tracker.add_audio_cost(len(chunk_text))

                # 3. Transcribe chunk
                Messenger.info(f"Transcribing Batch {batch_num} for alignment...")
                segments = self.whisper.get_transcription_segments(chunk_audio_path)

                # 4. Align chunk
                Messenger.info(f"Aligning Batch {batch_num} via Gemini...")
                chunk_script_texts = [s.narration for s in chunk]
                prompt = self.prompt_manager.get_alignment_prompt(segments, chunk_script_texts)
                alignment = self.text_gen.generate_text(prompt, AudioAlignment)

                # 5. Validate alignment count
                if len(alignment.alignments) != len(chunk):
                    # Delete corrupted chunk to force retry
                    chunk_audio_path.unlink(missing_ok=True)
                    chunk_audio_path.with_name(chunk_audio_path.name + ".json").unlink(missing_ok=True)
                    error_msg = (
                        f"Alignment mismatch in Batch {batch_num}: "
                        f"Expected {len(chunk)}, got {len(alignment.alignments)}"
                    )
                    raise RuntimeError(error_msg)

                # Get total duration of the chunk
                total_chunk_dur = self.ffmpeg.get_audio_duration(chunk_audio_path)

                # 6. Split and Save (continuous without gaps or overlaps)
                Messenger.info(f"Splitting Batch {batch_num} into {len(chunk)} scene audios...")
                last_end_time = 0.0
                for idx, al in enumerate(alignment.alignments):
                    # al.scene_number is 1-indexed relative to the chunk (1 to 10)
                    absolute_scene_num = start_idx + al.scene_number
                    out_path = self.get_idea_asset_path(
                        idea_obj.id,
                        self.AUDIOS_DIR,
                        self.SCENE_AUDIO_PATTERN.format(absolute_scene_num)
                    )

                    start_time = last_end_time
                    if idx == len(alignment.alignments) - 1:
                        duration = total_chunk_dur - start_time
                    else:
                        end_time = max(start_time + 0.5, min(al.end_time, total_chunk_dur))
                        duration = end_time - start_time
                        last_end_time = end_time
                        
                    if duration < 0.5:
                        chunk_audio_path.unlink(missing_ok=True)
                        chunk_audio_path.with_name(
                            chunk_audio_path.name + ".json"
                        ).unlink(missing_ok=True)
                        raise RuntimeError(
                            f"Invalid duration (Scene {absolute_scene_num}): "
                            f"{duration:.3f}s. Forcing retry."
                        )

                    self.ffmpeg.split_audio(
                        audio_in=chunk_audio_path,
                        audio_out=out_path,
                        start_time=start_time,
                        duration=duration
                    )

                # 7. Cleanup chunk audio
                chunk_audio_path.unlink(missing_ok=True)
            except Exception as e:
                import traceback
                Messenger.error(f"Error in batch {batch_num}: {str(e)}")
                Messenger.error(traceback.format_exc())
                raise e

        # Final Update
        idea_obj.state = State.AUDIO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 3 ready: {State.AUDIO_GENERATED} finalized.\n")

    def step4_generate_videos(self):
        """
        Video Generation: Creates clips for each scene and merges them.
        """
        # 1. Retrieves state
        idea_obj = self.store.get_first_by_state(State.AUDIO_GENERATED)
        if not idea_obj:
            Messenger.error("No audio ready for video generation.")
            return

        Messenger.info("\n--- Generating videos for the script ---")

        # 2. Loads script.json
        script_data = self.load_script(idea_obj)
        
        # 3. Create Master Audio (Source of Truth)
        audio_segments = []
        for i in range(len(script_data.scenes)):
            # Use actual scene_number if available, else i+1
            scene_num = getattr(script_data.scenes[i], 'scene_number', i + 1)
            seg = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(scene_num))
            
            # --- FASE 1: SFX TRANSITION LOGIC ---
            sfx_name = getattr(script_data.scenes[i], 'sfx', 'swoosh')
            if not sfx_name or sfx_name == 'none':
                sfx_name = 'swoosh'
            sfx_name = sfx_name.lower().strip()
            
            sfx_path = Path("flows/image_content_generator/resources/sfx") / f"{sfx_name}.mp3"
            if not sfx_path.exists():
                sfx_path = Path("flows/image_content_generator/resources/sfx") / f"{sfx_name}.wav"
            if not sfx_path.exists():
                sfx_path = Path("flows/image_content_generator/resources/sfx/swoosh.mp3")

            if sfx_path.exists() and seg.exists():
                sfx_seg = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, f"scene_{scene_num:02d}_sfx.wav")
                try:
                    self.ffmpeg.mix_sfx(seg, sfx_path, sfx_seg, volume=0.35)
                    if sfx_seg.exists():
                        seg = sfx_seg  # Use the version with SFX injected
                except Exception as e:
                    Messenger.warning(f"Failed to mix SFX '{sfx_name}' for scene {scene_num}: {e}")

            if seg.exists():
                audio_segments.append(seg)
            else:
                Messenger.warning(f"Missing audio segment for scene {scene_num}: {seg}")
        
        if not audio_segments:
            Messenger.error("No audio segments found. Cannot proceed.")
            return

        master_audio = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_AUDIO)
        
        # Audio concatenation via filter_complex
        cmd_audio = ["ffmpeg", "-y"]
        for s in audio_segments:
            cmd_audio.extend(["-i", str(s)])
        
        if len(audio_segments) > 1:
            filter_complex = "".join([f"[{i}:a]" for i in range(len(audio_segments))]) + f"concat=n={len(audio_segments)}:v=0:a=1[a]"
            cmd_audio.extend(["-filter_complex", filter_complex, "-map", "[a]"])
        else:
            cmd_audio.extend(["-c:a", "copy"])
        
        cmd_audio.append(str(master_audio))
        import subprocess
        subprocess.run(cmd_audio, check=True)

        # 4. Merges assets into scene clips (Visual only)
        scene_videos: List[Path] = []
        
        def process_video_scene(item):
            i, scene = item
            scene_num = getattr(scene, 'scene_number', i + 1)
            
            # Check multiple naming patterns for source (Video clips first, then images)
            possible_sources = [
                self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, self.SCENE_VIDEO_PATTERN.format(scene_num)),
                self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, f"scene_{scene_num:02d}.png"),
                self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, f"scene_{scene_num}.png")
            ]
            
            source_path = None
            for p in possible_sources:
                if p.exists():
                    source_path = p
                    break
            
            if not source_path:
                Messenger.error(f"Missing source (image/clip) for Scene {scene_num}. Skipping.")
                return None
                
            audio_seg = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(scene_num))
            video_path = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(scene_num))

            if not audio_seg.exists():
                Messenger.error(f"Missing audio for Scene {scene_num}. Skipping.")
                return None

            Messenger.info(f"Stitching Scene {scene_num}...")
            if "_frame_" in str(source_path):
                image_sequence_pattern = str(source_path).replace("_frame_01.png", "_frame_%02d.png")
                self.ffmpeg.create_animated_scene_video(image_sequence_pattern, audio_seg, video_path)
            else:
                self.ffmpeg.create_composite_scene_video(source_path, audio_seg, video_path, apply_glitch=(i > 0))
            return video_path

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_video_scene, enumerate(script_data.scenes)))
            
        scene_videos = [r for r in results if r is not None]

        if not scene_videos:
            Messenger.error("No scene videos generated.")
            return

        # 5. Final video concatenation + Master Audio re-sync
        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        temp_video = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, "temp_concat.mp4")
        self.ffmpeg.concat_videos(scene_videos, temp_video)
        
        # Merge concatenated video with the Master Audio
        cmd_merge = [
            "ffmpeg", "-y", "-i", str(temp_video), "-i", str(master_audio),
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest",
            str(raw_video)
        ]
        subprocess.run(cmd_merge, check=True)

        # 6. Updates state.
        idea_obj.state = State.VIDEO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 4 ready: {State.VIDEO_GENERATED} finalized.\n")

    def step5_generate_subtitles(self):
        """
        Generate Subtitles: Adds subtitles to the video.
        1. Retrieves the VIDEO_GENERATED idea.
        2. Prepares directories.
        3. Extracts audio.
        4. Generates srt.
        5. Adds subtitles to final video.
        6. Updates state.
        """
        # 1. Retrieves VIDEO_GENERATED idea.
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED)
        if not idea_obj:
            Messenger.error("No video ready for subtitle generation.")
            return

        Messenger.info("\n--- Generating subtitles for the video ---")

        # 2. Prepares directories.
        raw_video = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO
        )
        audio_wav = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.FINAL_AUDIO
        )
        subs_srt = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.FINAL_SUBS
        )
        subtitled_video = self.get_idea_asset_path(
            idea_obj.id, self.EDITIONS_DIR, self.SUBTITLED_VIDEO
        )

        # 3. Extract Audio
        Messenger.info("Extracting audio for transcription...")
        self.ffmpeg.extract_audio(raw_video, audio_wav)

        # 4. Generate srt with script context for perfect spelling
        Messenger.info("Transcribing audio via Whisper...")
        script_data = self.load_script(idea_obj)
        full_narration = " ".join([s.narration for s in script_data.scenes])
        self.whisper.generate_srt(audio_wav, subs_srt, prompt=full_narration, script_text=full_narration)

        # 5. Add Subtitles
        Messenger.info("Adding subtitles to final video...")
        self.ffmpeg.add_subtitles_to_video(raw_video, subs_srt, subtitled_video)

        # 6. Updates state.
        idea_obj.state = State.VIDEO_SUBTITLED
        self.store.save(idea_obj)
        Messenger.success(f"Step 5 ready: {State.VIDEO_SUBTITLED} finalized.\n")

    def step5_pro_subtitles(self):
        """
        Step 5 (PRO): High-End Subtitles and Multi-layer Composition.
        """
        # 1. Retrieves state
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED)
        if not idea_obj:
            Messenger.error("No video ready for PRO subtitles.")
            return

        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        remotion_overlay = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.REMOTION_VIDEO)
        pro_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.PRO_SUBTITLED_VIDEO)
        audio_wav = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_AUDIO)
        
        # 2. Get timing from Whisper but TEXT from the original script (zero spelling errors)
        Messenger.info(f"Aligning subtitles: using exact script words + Whisper timestamps...")
        script_data = self.load_script(idea_obj)
        full_narration = " ".join([s.narration for s in script_data.scenes])
        
        # Get word-level timestamps from Whisper (used ONLY for timing)
        whisper_words = self.whisper.get_word_tokens(audio_wav, prompt=full_narration)
        
        # Build the exact word list from the original script (perfect spelling guaranteed)
        # Split preserving all words exactly as written
        import re
        # Tokenize script words keeping punctuation attached to words (as Whisper does)
        script_tokens = re.findall(r"\S+", full_narration)
        
        word_data = []
        whisper_count = len(whisper_words)
        script_count = len(script_tokens)
        
        Messenger.info(f"   Whisper detected {whisper_count} word-timestamps | Script has {script_count} words")
        
        for i, w in enumerate(whisper_words):
            if i < script_count:
                # Use the EXACT script word for display text (no spelling errors)
                exact_text = script_tokens[i]
            else:
                # Fallback: use whisper text if script ran out (shouldn't happen)
                exact_text = w.text.strip()
            word_data.append({"text": exact_text, "start": w.start, "end": w.end})
        
        Messenger.success(f"   ✅ Subtitle text anchored to original script: zero spelling errors guaranteed.")
        
        # 3. Render Remotion
        remotion_root = Path(self.REMOTION_DIR)
        remotion_frames_dir = remotion_overlay.parent
        remotion_frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Get top headline from script (StoryIdea field)
        intrigue_text = getattr(script_data, "top_headline", None)
        
        self.remotion.render_subtitles(
            remotion_path=remotion_root,
            output_path=remotion_overlay,
            words=word_data,
            top_headline=intrigue_text
        )

        # 4. Multi-layer Composition with filter_complex
        import subprocess
        remotion_pattern = remotion_overlay / "%04d.png"
        duration = self.ffmpeg.get_video_duration(raw_video)
        
        fc = (
            f"[0:v]noise=alls=5:allf=t+u[v_grain];"
            f"[v_grain]drawbox=y=0:w=iw:h=25:color=black@0.5:t=fill[v_bar_bg];"
            f"[v_bar_bg]drawbox=y=0:w=iw*t/{duration}:h=25:color=#FFFF00@1.0:t=fill[v_composed];"
            f"[v_composed][1:v]overlay=shortest=1[out]"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-framerate", "25",
            "-i", str(remotion_pattern),
            "-filter_complex", fc,
            "-map", "[out]", "-map", "0:a",
            "-c:v", "libx264", "-c:a", "copy", "-pix_fmt", "yuv420p",
            str(pro_video)
        ]
        subprocess.run(cmd, check=True)

        # 5. Updates state
        idea_obj.state = State.VIDEO_PRO_SUBTITLED
        self.store.save(idea_obj)
        Messenger.success(f"Step 5 (PRO) ready: {State.VIDEO_PRO_SUBTITLED} finalized.\n")

    def step6_add_background_music(self):
        """
        Background Music: Adds a random background track to the subtitled video.
        """
        # 1. Retrieves subtitled video (PRO takes priority)
        idea_obj = self.store.get_first_by_state(State.VIDEO_PRO_SUBTITLED)
        is_pro = True
        if not idea_obj:
            idea_obj = self.store.get_first_by_state(State.VIDEO_SUBTITLED)
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
        idea_obj = self.store.get_first_by_state(State.VIDEO_MUSIC_GENERATED)
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
        Generates a short, highly viral description for Facebook/Instagram Reels.
        """
        # Clean title from A/B testing tags like [Hook B] or [Hook A]
        import re
        title = re.sub(r"\s*\[Hook\s+[A-Z]\]", "", title, flags=re.IGNORECASE).strip()

        prompt = f"""
        You are the social media expert for "BlowYourMind", a super viral channel about curious facts, mysteries, and science.
        Write the "Caption" (description) for the following video: "{title}"
        
        MANDATORY Requirements:
        1. BE EXTREMELY SHORT. Maximum 2 engaging lines that invite people to comment.
        2. Tone: Intriguing, dynamic, and mind-blowing (e.g. "Did you know this? Let us know in the comments 👇").
        3. Do not use poetic or philosophical language, use the language of a TikTok/Reels content creator.
        4. Add exactly 10 VIRAL HASHTAGS relevant to the video topic and always include: #Curiosities #MindBlowing #BlowYourMind
        
        Respond ONLY with the description text and hashtags, without any additional text.
        """
        try:
            return self.text_gen.generate(prompt).strip()
        except Exception as e:
            Messenger.warning(f"AI Description generation failed: {e}. Using fallback.")
            return f"🤯 {title}\n\nWhat do you think? Let us know in the comments 👇\n\n#Curiosities #Viral #Foryou #Mysteries #DidYouKnow #BlowYourMind #Interesting"

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
            idea_obj = self.store.get_first_by_state(State.COMPLETED)
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

                # 5. Updates state to UPLOADED.
                idea_obj.state = State.UPLOADED
                self.store.save(idea_obj)
                Messenger.success(f"   Idea {idea_obj.id} uploaded and marked as {State.UPLOADED}.\n")
            except Exception as e:
                Messenger.error(f"   Failed to upload Idea {idea_obj.id}: {str(e)}")
                break

    def generate_sabias_que_content(self, title: str) -> dict:
        """
        Generates the visual curiosity text (for drawing on the image), the post description,
        and a matching dedicated image prompt using Gemini.
        All content is generated exclusively in English for BlowYourMind.
        """
        # Clean title from A/B testing tags like [Hook B] or [Hook A]
        import re
        title = re.sub(r"\s*\[Hook\s+[A-Z]\]", "", title, flags=re.IGNORECASE).strip()

        prompt = f"""
        You are a star creative copywriter for the channel "BlowYourMind" on Facebook.
        We are going to create a "Did you know...?" style image post based on this topic: "{title}"
        
        We need three fields in JSON format (ALL IN ENGLISH):
        1. **card_text**: A mind-bending, high-curiosity teaser/hook about the topic to draw on the image.
           It must be framed as a "Hard Truth" or a "Secret" that triggers ego or curiosity.
           It MUST be in ALL CAPS. Max 15-20 words (1-2 lines).
           It should end with a cliffhanger or teaser (e.g. "...but the secret truth is much darker.", "...and the reason why is terrifying.")
           Examples:
           - "SHARKS WERE HERE BEFORE THE TREES... AND THE SCIENTIFIC REASON WHY IS MINDBLOWING."
           - "AI IS NOW READING HUMAN DREAMS... AND WHAT IT DECODED WILL TERRIFY YOU."
           - "OCTOPUSES HAVE THREE HEARTS AND NINE BRAINS... BUT THERE IS A 10TH SECRET THAT SCIENTISTS HID."
        
        2. **post_description**: A long, highly engaging, and entertaining educational caption to accompany the image.
           It must explain the topic in detail but using simple, clear, and easy-to-understand English (suitable for international, non-native audiences).
           It must NOT be short, generic, or overly brief. It should make the reader go "Wow, that is fascinating!" and understand the science or history behind the topic clearly.
           Length: Around 150-250 words.
           Structure:
           - First line: A stunning, hook-like resolution to the image cliffhanger in simple words.
           - Body: Break it down into 2-3 short, highly engaging paragraphs detailing the exact mystery, how it works scientifically, and 3 mind-blowing facts about it. Use friendly, clear language without overly dense scientific jargon, but with extreme educational detail.
           - Ending: A fun, conversational call-to-action question inviting users to comment, share their thoughts, or answer a paradox (e.g., "If nature is capable of this, what else is waiting to be discovered? Tell us your thoughts below! 👇").
           - Contain exactly 10 high-impact hashtags: #DidYouKnow #Curiosities #MindBlowing #BlowYourMind and 6 others relevant to the topic.
        
        3. **image_prompt**: A highly descriptive and detailed prompt in English to generate a premium hyper-realistic image via Vertex AI Imagen 3.
           It must follow these aesthetic parameters based on the topic:
           - If Animal/Nature: "National Geographic style, extreme close-up (macro), 8k, bokeh background, hyper-detailed fur/scales, natural sunlight, cinematic color grading."
           - If Science/Space: "Interstellar movie aesthetic, volumetric lighting, deep blacks, high contrast, scientific accuracy but epic scale, sharp focus."
           - If Tech/Futuristic: "Cyberpunk minimalism, sleek metallic textures, neon accents (teal/orange), macro lens, shallow depth of field, futuristic realism."

        IMPORTANT: ALL fields MUST be in native English only.

        Mandatory JSON output format:
        {{
          "card_text": "HOOK IN CAPS",
          "post_description": "Detailed deep caption text in simple English",
          "image_prompt": "Prompt for Vertex AI Imagen 3 matching style guidelines"
        }}
        """
        try:
            res_raw = self._text_gen.generate(prompt).strip() if self._text_gen else ""
            if not res_raw:
                from tools.text_generation.gemini import GeminiTextGenerator
                text_gen = GeminiTextGenerator()
                res_raw = text_gen.generate(prompt).strip()
            
            # Clean JSON block if present
            if "```json" in res_raw:
                res_raw = res_raw.split("```json")[1].split("```")[0].strip()
            elif "```" in res_raw:
                res_raw = res_raw.split("```")[1].split("```")[0].strip()
            
            import json
            data = json.loads(res_raw)
            return {
                "card_text": data.get("card_text", "").strip(),
                "post_description": data.get("post_description", "").strip(),
                "image_prompt": data.get("image_prompt", "").strip()
            }
        except Exception as e:
            Messenger.warning(f"Failed to generate custom Did You Know content: {e}. Using fallback.")
            return {
                "card_text": f"{title.upper()} HAS A SECRET... AND THE SCIENTIFIC REASON WILL BLOW YOUR MIND.",
                "post_description": (
                    f"🤯 Did you know the incredible truth behind {title}? It is absolutely mind-blowing!\n\n"
                    f"For a long time, this topic has fascinated people and scientists alike. The reality is that this phenomenon "
                    f"works in ways that challenge what we normally expect. Specifically, recent discoveries reveal three astonishing facts:\n\n"
                    f"1️⃣ It operates under unique principles that create highly unusual patterns.\n"
                    f"2️⃣ The impact it has on its surroundings is far greater than previously thought.\n"
                    f"3️⃣ It holds secrets that could change how we understand the topic in the future.\n\n"
                    f"It is a beautiful and mysterious part of our world. What do you think about this fascinating concept? "
                    f"Does it surprise you? Let us know in the comments below! 👇\n\n"
                    f"#DidYouKnow #Curiosities #MindBlowing #BlowYourMind #ScienceFacts #NatureLovers #Discoveries #Secrets #LearningIsFun #Fascinating"
                ),
                "image_prompt": f"Extreme close-up macro shot representing the mysterious concept of {title}, volumetric lighting, high contrast, cinematic color grading, 8k."
            }

    def compose_did_you_know_card(self, original_img_path: Path, output_path: Path, card_text: str):
        """
        Composes a highly professional, stunning vertical "Did You Know?" card (1080x1350)
        from a raw generated image. All text is in English.
        """
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        
        # 1. Download premium fonts if not already cached
        font_dir = self.resource_base / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)
        
        font_bold_path = font_dir / "Montserrat-Bold.ttf"
        font_medium_path = font_dir / "Montserrat-Medium.ttf"
        
        url_bold = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf"
        url_medium = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Medium.ttf"
        
        def download_font(url: str, dest: Path):
            if not dest.exists():
                import urllib.request
                try:
                    Messenger.info(f"Downloading premium font for layout: {dest.name}...")
                    urllib.request.urlretrieve(url, dest)
                except Exception as e:
                    Messenger.warning(f"Could not download font {dest.name}: {e}")
        
        download_font(url_bold, font_bold_path)
        download_font(url_medium, font_medium_path)
        
        # Fallback to default if download fails
        try:
            font_title = ImageFont.truetype(str(font_bold_path), 64)
            font_body = ImageFont.truetype(str(font_medium_path), 32)
        except Exception:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
            Messenger.warning("Using fallback default fonts for card composition.")
            
        # 2. Dimensions
        canvas_w, canvas_h = 1080, 1350
        
        # Load and scale original image (originally 9:16)
        if not original_img_path.exists():
            raise FileNotFoundError(f"Original image not found: {original_img_path}")
            
        orig_img = Image.open(original_img_path).convert("RGBA")
        
        # 3. Create context-aware blurred background
        # Resize to fill canvas
        bg_img = orig_img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        # Apply strong blur for aesthetic depth
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=40))
        
        # Apply elegant dark color overlay (semi-transparent black)
        overlay = Image.new("RGBA", (canvas_w, canvas_h), (11, 15, 25, 180)) # deep navy dark overlay
        canvas = Image.alpha_composite(bg_img, overlay)
        draw = ImageDraw.Draw(canvas)
        
        # 4. Draw Header "DID YOU KNOW...?"
        title_text = "DID YOU KNOW...?"
        title_bbox = font_title.getbbox(title_text)
        title_w = title_bbox[2] - title_bbox[0]
        title_x = (canvas_w - title_w) // 2
        title_y = 80
        
        # Draw soft drop shadow for title
        draw.text((title_x + 3, title_y + 3), title_text, font=font_title, fill=(0, 0, 0, 120))
        # Draw glowing yellow title
        draw.text((title_x, title_y), title_text, font=font_title, fill=(255, 255, 0, 255))
        
        # Draw elegant golden accent bar under title
        bar_w, bar_h = 180, 5
        bar_x = (canvas_w - bar_w) // 2
        bar_y = title_y + 80
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=(255, 255, 0, 255))
        
        # 5. Place Center Image Card (960x650 px)
        card_w, card_h = 960, 650
        card_x = (canvas_w - card_w) // 2
        card_y = 200
        
        # Crop & scale original image to fit center card exactly (centered crop)
        orig_w, orig_h = orig_img.size
        target_ratio = card_w / card_h
        orig_ratio = orig_w / orig_h
        
        if orig_ratio > target_ratio:
            # Crop width
            new_w = int(orig_h * target_ratio)
            left = (orig_w - new_w) // 2
            cropped = orig_img.crop((left, 0, left + new_w, orig_h))
        else:
            # Crop height
            new_h = int(orig_w / target_ratio)
            top = (orig_h - new_h) // 2
            cropped = orig_img.crop((0, top, orig_w, top + new_h))
            
        center_img = cropped.resize((card_w, card_h), Image.Resampling.LANCZOS)
        
        # Add smooth rounded corners to the center image
        def add_corners(im, rad):
            circle = Image.new('L', (rad * 2, rad * 2), 0)
            draw_circle = ImageDraw.Draw(circle)
            draw_circle.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
            alpha = Image.new('L', im.size, 255)
            w, h = im.size
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
            im.putalpha(alpha)
            return im
            
        center_img = add_corners(center_img, 24)
        
        # Draw rounded backing card for the image
        glow_padding = 4
        draw.rounded_rectangle(
            [card_x - glow_padding, card_y - glow_padding, card_x + card_w + glow_padding, card_y + card_h + glow_padding],
            radius=28,
            fill=(255, 255, 255, 15), # subtle transparent white border
            outline=(255, 255, 255, 30),
            width=2
        )
        
        # Paste the centered image card
        canvas.paste(center_img, (card_x, card_y), center_img)
        
        # 6. Draw Text Card Area at the Bottom (y = 890px to 1270px)
        text_card_y = 890
        text_card_h = 360
        text_card_w = 960
        text_card_x = (canvas_w - text_card_w) // 2
        
        # Semi-transparent dark card behind the text
        draw.rounded_rectangle(
            [text_card_x, text_card_y, text_card_x + text_card_w, text_card_y + text_card_h],
            radius=24,
            fill=(0, 0, 0, 160), # darker background for high legibility
            outline=(255, 255, 255, 20),
            width=1
        )
        
        # Text wrapping
        max_text_width = text_card_w - 80 # margin inside card
        words = card_text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font_body.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_text_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        # Draw wrapped lines
        line_height = 48
        total_text_h = len(lines) * line_height
        start_y = text_card_y + (text_card_h - total_text_h) // 2 # center vertically inside text card
        
        for i, line in enumerate(lines):
            line_bbox = font_body.getbbox(line)
            line_w = line_bbox[2] - line_bbox[0]
            line_x = text_card_x + (text_card_w - line_w) // 2 # center horizontally
            
            fill_color = (255, 255, 255, 255) # white
            if i == 0:
                fill_color = (255, 255, 0, 255) # yellow highlight
                
            draw.text((line_x, start_y + i * line_height), line, font=font_body, fill=fill_color)
            
        # 7. Draw High-Impact CTA Banner at the very bottom (y = 1270 to 1330) to drive caption reading
        cta_y = 1270
        cta_h = 55
        cta_w = 960
        cta_x = (canvas_w - cta_w) // 2
        
        draw.rounded_rectangle(
            [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
            radius=12,
            fill=(255, 255, 0, 15), # subtle yellow tint background
            outline=(255, 255, 0, 180), # glowing golden outline
            width=2
        )
        
        cta_text = "👇 READ THE FULL STORY IN THE CAPTION 👇"
        try:
            font_cta = ImageFont.truetype(str(font_bold_path), 26)
        except Exception:
            font_cta = font_body
            
        cta_bbox = font_cta.getbbox(cta_text)
        cta_text_w = cta_bbox[2] - cta_bbox[0]
        cta_text_h = cta_bbox[3] - cta_bbox[1]
        cta_text_x = cta_x + (cta_w - cta_text_w) // 2
        cta_text_y = cta_y + (cta_h - cta_text_h) // 2 - 2
        
        draw.text((cta_text_x, cta_text_y), cta_text, font=font_cta, fill=(255, 255, 0, 255))
            
        # Save composed canvas
        canvas = canvas.convert("RGB")
        canvas.save(output_path, "JPEG", quality=95)
        Messenger.success(f"🎨 Composed 'Did You Know?' image card with premium CTA at: {output_path}")

    def step8_upload_image_to_facebook(self):
        """
        Upload Image to Facebook: Uploads a single beautifully composed "Did You Know?" image.
        Used for the '30 images weekly' requirement.
        """
        idea_obj = self.store.get_first_by_state(State.IMAGES_GENERATED)
        if not idea_obj:
            Messenger.error("No image found to upload.")
            return

        Messenger.info(f"\n--- Composing and Uploading Image Post: {idea_obj.title} ---")

        # 1. Generate customized content for card and post (including dedicated image prompt!)
        Messenger.info("Generating customized 'Did You Know?' text content and image prompt via Gemini...")
        content_data = self.generate_sabias_que_content(idea_obj.title)
        
        card_text = content_data["card_text"]
        post_description = content_data["post_description"]
        image_prompt = content_data.get("image_prompt", "")
        
        # 2. Path to the dedicated image to use
        img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "sabias_que_source.png")
        
        # 3. Generate the dedicated coherent image if prompt is present
        if image_prompt:
            Messenger.info(f"Generating dedicated coherent image via Vertex AI Imagen 3...")
            Messenger.info(f"   Prompt: {image_prompt}")
            try:
                task = ImageTask(
                    prompt=image_prompt,
                    output_path=img_path
                )
                self.image_gen.generate_images([task])
                self.cost_tracker.add_image_cost(1)
            except Exception as gen_e:
                Messenger.error(f"   ❌ Dedicated image generation failed: {gen_e}. Falling back to default scene_01.png")
                # Fallback to scene_01.png
                img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "scene_01.png")
        else:
            Messenger.warning("No image prompt generated. Falling back to default scene_01.png")
            img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "scene_01.png")

        if not img_path.exists():
            # Second-level fallback to any scene image if scene_01.png is also missing
            fallback_img = None
            for idx in range(1, 10):
                possible_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, f"scene_{idx:02d}.png")
                if possible_path.exists():
                    fallback_img = possible_path
                    break
            
            if fallback_img:
                img_path = fallback_img
                Messenger.warning(f"Using secondary fallback image: {img_path}")
            else:
                Messenger.error(f"Image not found (and all fallbacks failed): {img_path}")
                return
        
        # 4. Path to composed card output
        composed_img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, "sabias_que_composed.jpg")
        
        # 5. Compose card
        Messenger.info("Composing premium 'Did You Know?' card canvas with Pillow...")
        self.compose_did_you_know_card(img_path, composed_img_path, card_text)

        # 6. Append Transparency Footer to Description
        transparency_footer = (
            "\n\n---\n"
            "🤖 **AI-Generated Content**: This infographic and message have been created with Artificial Intelligence for educational and recreational purposes.\n\n"
            "✨ Published by BlowYourMind.\n"
            "#MadeWithAI #DidYouKnow #Curiosities #BlowYourMind #LearningIsFun"
        )
        final_description = post_description + transparency_footer

        # 7. Upload composed photo
        try:
            Messenger.info("Uploading composed card photo to Facebook...")
            photo_id = self.facebook.upload_photo(composed_img_path, caption=final_description)
            if photo_id:
                idea_obj.state = State.UPLOADED
                self.store.save(idea_obj)
                Messenger.success(f"✅ Composed image post successful! ID: {photo_id}")
        except Exception as e:
            Messenger.error(f"❌ Failed to upload image: {e}")
