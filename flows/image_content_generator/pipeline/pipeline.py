
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
    resource_base: Path
    orientation: VideoOrientation
    mode: str = "standard"

    @property
    def _category(self) -> str | None:
        _map = {"geography": "geography", "stories": "stories", "seven_levels": "seven_levels", "finance": "finance", "what_if": "what_if"}
        return _map.get(self.mode)

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
        category = getattr(idea_obj, "category", "")
        if category == "geography":
            from flows.image_content_generator.pipeline.prompt_shorts.geography.models import GeographyHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, GeographyHandler)
        if category == "seven_levels":
            from flows.image_content_generator.pipeline.prompt_shorts.seven_levels.models import SevenLevelsHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, SevenLevelsHandler)
        if category == "stories":
            from flows.image_content_generator.pipeline.prompt_shorts.stories.models import StoryHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, StoryHandler)
        if category == "finance":
            from flows.image_content_generator.pipeline.prompt_shorts.finance.models import FinanceHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, FinanceHandler)
        if category == "what_if":
            from flows.image_content_generator.pipeline.prompt_shorts.what_if.models import WhatIfHandler
            return self.load_json(idea_obj.id, self.SCRIPT_JSON, WhatIfHandler)
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
        Generate Images: Batch Image Generation (Gemini).
        Generates 3 frames per scene for Flipbook animation.
        """
        idea_obj = self.store.get_first_by_state(State.SCRIPT_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.warning("Step 2 skipped: No idea in SCRIPT_GENERATED state.")
            return

        Messenger.info(f"Step 2 started: Generating Animated Frames for '{idea_obj.title}'")
        Messenger.info(f"   Loading script for Idea {idea_obj.id}...")
        script = self.load_script(idea_obj)
        Messenger.info(f"   Script loaded. Scenes: {len(script.scenes)}")

        from tools.image_generation.gemini import GeminiImageGenerator
        import os as os_mod
        fallback_gen = None

        def generate_one(scene):
            nonlocal fallback_gen
            action_prompt = getattr(scene, "image_prompt", None) or getattr(scene, "narration", f"A cinematic scene about {idea_obj.title}")
            out_name = f"scene_{scene.scene_number:02d}.png"
            out_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, out_name)
            if out_path.exists():
                return
            try:
                self.image_gen.generate_image(
                    prompt=action_prompt,
                    output_path=out_path
                )
            except Exception as e:
                Messenger.warning(f"   ⚠️ Primary image gen failed for scene {scene.scene_number}: {e}")
                if not fallback_gen:
                    ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
                    fallback_gen = GeminiImageGenerator(
                        aspect_ratio=ar_value,
                        reference_dir=self.resource_base / self.REFERENCES_DIR,
                    )
                    Messenger.info("   🔄 Falling back to Gemini image generator...")
                fallback_gen.generate_image(
                    prompt=action_prompt,
                    output_path=out_path
                )
            try:
                from PIL import Image
                img = Image.open(out_path)
                w, h = img.size
                target_short = 1080 if h >= w else 1920
                target_long = 1920 if h >= w else 1080
                if w < target_short or h < target_long:
                    Messenger.info(f"   Upscaling {out_name} from {w}x{h} to target...")
                    img = img.resize((max(w, target_short), max(h, target_long)), Image.LANCZOS)
                    img.save(out_path, quality=95)
            except Exception:
                pass

        # Use 1 worker (sequential) to avoid rate limit hammering on any image gen backend
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(generate_one, scene) for scene in script.scenes]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    Messenger.error(f"   ❌ Image generation failed: {e}")
                    raise

        self.cost_tracker.add_image_cost(len(script.scenes))

        # Update State
        idea_obj.state = State.IMAGES_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2 ready: {State.IMAGES_GENERATED} finalized.\n")

    def _generate_narration_cues(self, idea_id: int, scene) -> list:
        """
        Generates narration cues by matching scene visual elements (floating_label,
        map_pins, vignettes) against Whisper word-level timestamps.
        Returns a list of NarrationCue dicts for Remotion.
        """
        from flows.image_content_generator.pipeline.schemas import NarrationCue
        import json

        cues = []
        scene_num = scene.scene_number

        # Load Whisper transcription for this scene's audio
        audio_seg = self.get_idea_asset_path(
            idea_id, self.AUDIOS_DIR,
            self.SCENE_AUDIO_PATTERN.format(scene_num)
        )
        whisper_json = audio_seg.with_name(audio_seg.name + ".json")
        if not whisper_json.exists():
            return cues

        try:
            with open(whisper_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return cues

        word_timestamps = []
        for seg in data.get("transcription", []):
            for token in seg.get("tokens", []):
                word_timestamps.append({
                    "word": token.get("text", "").strip().lower(),
                    "start_ms": token.get("offsets", {}).get("from", 0),
                    "end_ms": token.get("offsets", {}).get("to", 0),
                })

        # Match floating_label keywords to words in narration
        floating_label = getattr(scene, "floating_label", "") or ""
        if floating_label and floating_label != "none":
            label_words = set(w.lower() for w in floating_label.replace(",", "").split())
            for wt in word_timestamps:
                if wt["word"] in label_words:
                    cues.append(NarrationCue(
                        word=wt["word"],
                        start_ms=wt["start_ms"],
                        end_ms=wt["end_ms"],
                        event_type="label_flash",
                        target=floating_label,
                    ).model_dump())
                    break

        # Match pin labels
        map_pins = getattr(scene, "map_pins", []) or []
        for pin in map_pins:
            pin_label = getattr(pin, "label", "") or ""
            if pin_label:
                pin_words = pin_label.lower().split()
                for wt in word_timestamps:
                    if any(pw == wt["word"] for pw in pin_words):
                        cues.append(NarrationCue(
                            word=wt["word"],
                            start_ms=wt["start_ms"],
                            end_ms=wt["end_ms"],
                            event_type="pin_drop",
                            target=pin_label,
                        ).model_dump())
                        break

        return cues

    def _build_scene_props(self, idea_obj, scene, audio_duration_ms, remotion_public_images):
        """Build MapRender props dict for a single scene (map_3d or ai_image)."""
        is_geography_mode = getattr(idea_obj, "category", "") == "geography"

        def _get_camera_attr(s, attr, default):
            flat_val = getattr(s, f"camera_{attr}", None)
            if flat_val and flat_val != 0.0:
                return flat_val
            camera = getattr(s, "camera", None)
            if camera:
                return getattr(camera, attr, default)
            return default

        lat = _get_camera_attr(scene, "latitude", 4.570868)
        lon = _get_camera_attr(scene, "longitude", -74.297333)
        zoom = _get_camera_attr(scene, "zoom", 5.2)
        pitch = _get_camera_attr(scene, "pitch", 45.0)
        bearing = _get_camera_attr(scene, "bearing", -10.0)

        visual_type = getattr(scene, "visual_type", "map_3d")

        # Build pins/vignettes/camera_path
        pins_data = []
        for p in getattr(scene, "map_pins", []):
            pins_data.append({
                "latitude": p.latitude if hasattr(p, "latitude") else 0,
                "longitude": p.longitude if hasattr(p, "longitude") else 0,
                "label": p.label if hasattr(p, "label") else "",
                "value": p.value if hasattr(p, "value") else "",
            })
        vignettes_data = []
        for v in getattr(scene, "vignettes", []):
            vignettes_data.append({
                "icon": v.icon if hasattr(v, "icon") else "📊",
                "title": v.title if hasattr(v, "title") else "",
                "value": v.value if hasattr(v, "value") else "",
            })
        camera_path_data = []
        for wp in getattr(scene, "camera_path", []):
            camera_path_data.append({
                "latitude": wp.latitude if hasattr(wp, "latitude") else 0,
                "longitude": wp.longitude if hasattr(wp, "longitude") else 0,
                "zoom": wp.zoom if hasattr(wp, "zoom") else 5,
                "pitch": wp.pitch if hasattr(wp, "pitch") else 40,
                "bearing": wp.bearing if hasattr(wp, "bearing") else 0,
            })
        hex_icons_data = []
        for hx in getattr(scene, "hex_icons", []):
            hex_icons_data.append({
                "latitude": hx.latitude if hasattr(hx, "latitude") else 0,
                "longitude": hx.longitude if hasattr(hx, "longitude") else 0,
                "icon": hx.icon if hasattr(hx, "icon") else "📍",
                "label": hx.label if hasattr(hx, "label") else "",
                "value": hx.value if hasattr(hx, "value") else "",
                "color": hx.color if hasattr(hx, "color") else "#FF0078",
            })
        routes_data = []
        for rt in getattr(scene, "routes", []):
            wps = []
            for wp in getattr(rt, "waypoints", []):
                wps.append({
                    "latitude": wp.latitude if hasattr(wp, "latitude") else 0,
                    "longitude": wp.longitude if hasattr(wp, "longitude") else 0,
                    "zoom": wp.zoom if hasattr(wp, "zoom") else 5,
                    "pitch": wp.pitch if hasattr(wp, "pitch") else 40,
                    "bearing": wp.bearing if hasattr(wp, "bearing") else 0,
                })
            routes_data.append({
                "waypoints": wps,
                "color": rt.color if hasattr(rt, "color") else "#FF0078",
                "label": rt.label if hasattr(rt, "label") else "",
                "dot_labels": list(getattr(rt, "dot_labels", [])),
            })
        regions_data = []
        for rg in getattr(scene, "regions", []):
            regions_data.append({
                "name": rg.name if hasattr(rg, "name") else "",
                "center_latitude": rg.center_latitude if hasattr(rg, "center_latitude") else 0,
                "center_longitude": rg.center_longitude if hasattr(rg, "center_longitude") else 0,
                "color": rg.color if hasattr(rg, "color") else "#FF0078",
                "label": rg.label if hasattr(rg, "label") else "",
                "radius_km": rg.radius_km if hasattr(rg, "radius_km") else 200,
            })

        narration_cues = self._generate_narration_cues(idea_obj.id, scene)

        subtitle_words = []
        try:
            narration_text = getattr(scene, "narration", "") or ""
            raw_words = narration_text.split()
            if raw_words and audio_duration_ms > 0:
                word_duration = audio_duration_ms / len(raw_words)
                for i, w in enumerate(raw_words):
                    start_ms = i * word_duration
                    end_ms = (i + 1) * word_duration
                    _w_json = Path(self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(scene.scene_number))).with_name(f"scene_{scene.scene_number}.wav.json")
                    if _w_json.exists():
                        import json as _json
                        with open(_w_json, 'r', encoding='utf-8') as _f:
                            _data = _json.load(_f)
                        _seg_ms = 0
                        _ti = 0
                        for _seg in _data.get("transcription", []):
                            for _tok in _seg.get("tokens", []):
                                _txt = _tok.get("text", "").strip()
                                if _txt and _ti < len(raw_words):
                                    subtitle_words.append({
                                        "word": raw_words[_ti],
                                        "startMs": _tok.get("offsets", {}).get("from", _seg_ms),
                                        "endMs": _tok.get("offsets", {}).get("to", _seg_ms + 200),
                                    })
                                    _ti += 1
                                _seg_ms = _seg.get("offsets", {}).get("to_ms", _seg_ms)
                            _seg_ms = _seg.get("offsets", {}).get("to_ms", _seg_ms)
                        break
                    else:
                        subtitle_words.append({
                            "word": w,
                            "startMs": round(start_ms),
                            "endMs": round(end_ms),
                        })
        except Exception:
            pass

        highlight_region = getattr(scene, "highlight_region", "none")
        floating_label = getattr(scene, "floating_label", "none")
        arrow_direction = getattr(scene, "arrow_direction", "none")

        if visual_type == "ai_image":
            # CRITICAL FIX: Include idea_obj.id in the filename so Hook A and Hook B
            # (two ideas generated in the same run) never share the same temp image file.
            # Previously, scene_01_ai.jpg was overwritten/reused across ideas, causing
            # all videos to have identical images.
            ai_img_filename = f"idea_{idea_obj.id:06d}_scene_{scene.scene_number:02d}_ai.jpg"
            ai_img_dest = remotion_public_images / ai_img_filename
            # Always use the image already generated by Vertex AI in Step 2.
            # Do NOT call Gemini here — that caused generic/repeated images.
            img_path = self.get_idea_asset_path(idea_obj.id, self.IMAGES_DIR, f"scene_{scene.scene_number:02d}.png")
            if not ai_img_dest.exists():
                if img_path.exists():
                    import shutil
                    shutil.copy2(img_path, ai_img_dest)
                    Messenger.info(f"   ✅ Copied Vertex AI image for idea {idea_obj.id} scene {scene.scene_number}: {ai_img_filename}")
                else:
                    Messenger.warning(f"   ⚠️ No pre-generated image found for idea {idea_obj.id} scene {scene.scene_number}. Remotion will use placeholder.")
            return {
                "visualType": "ai_image",
                "imageFile": ai_img_filename,
                "latitude": 0, "longitude": 0, "zoom": 0, "pitch": 0, "bearing": 0,
                "highlightRegion": "none", "arrowDirection": "none", "floatingLabel": "none",
                "pins": [], "vignettes": vignettes_data, "cameraPath": [],
                "audioDurationMs": audio_duration_ms,
                "narrationCues": narration_cues, "subtitleWords": subtitle_words,
                "hexIcons": [], "routes": [], "regions": [],
                "mapStyle": getattr(scene, "map_style", "satellite"), "scanEffect": False, "lowerThirdData": [],
            }

        geopolitical_data = {}
        try:
            narration_text = getattr(scene, "narration", "") or ""
            if narration_text:
                from flows.image_content_generator.pipeline.geopolitical_analyzer import analyze_narration
                geopolitical_data = analyze_narration(narration_text)
        except Exception:
            pass

        scene_overlay = {}
        try:
            import json as _json
            _raw_path = self.get_idea_path(idea_obj.id) / self.SCRIPT_JSON
            if _raw_path.exists():
                _raw = _json.loads(_raw_path.read_text(encoding='utf-8'))
                _scn_num = getattr(scene, 'scene_number', 0)
                for _rs in _raw.get('scenes', []):
                    if _rs.get('scene_number') == _scn_num:
                        scene_overlay = _rs.get('sceneOverlay', {})
                        break
        except Exception:
            pass

        return {
            "visualType": "map_3d",
            "imageFile": "",
            "latitude": lat, "longitude": lon, "zoom": zoom, "pitch": pitch, "bearing": bearing,
            "highlightRegion": highlight_region,
            "arrowDirection": arrow_direction,
            "floatingLabel": floating_label,
            "pins": pins_data, "vignettes": vignettes_data, "cameraPath": camera_path_data,
            "audioDurationMs": audio_duration_ms,
            "narrationCues": narration_cues, "subtitleWords": subtitle_words,
            "hexIcons": hex_icons_data, "routes": routes_data, "regions": regions_data,
            "mapStyle": getattr(scene, "map_style", "satellite"), "scanEffect": True,
            "lowerThirdData": [
                {"icon": "🌍", "label": "REGION", "value": highlight_region if highlight_region != "none" else "EARTH"},
                {"icon": "📐", "label": "AREA", "value": f"{zoom:.1f}° zoom"},
                {"icon": "📍", "label": "COORDINATES", "value": f"{lat:.1f}°, {lon:.1f}°"},
            ],
            "geopolitical": geopolitical_data,
            "sceneOverlay": scene_overlay,
        }

    def step2b_generate_video_clips(self):
        """
        Step 2b: Render video clips using enhanced Remotion MapRender (3D satellite maps)
        with GeoJSON country borders, neon glow, AI image scenes, and tile fallback.
        Falls back to Pexels/Pixabay stock video or Ken Burns image animation.
        Runs AFTER audio generation so we know exact scene durations.
        """
        idea_obj = self.store.get_first_by_state(State.AUDIO_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.warning("Step 2b skipped: No idea in AUDIO_GENERATED state.")
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

        def get_scene_audio_duration(scene):
            audio_seg = self.get_idea_asset_path(
                idea_obj.id, self.AUDIOS_DIR,
                self.SCENE_AUDIO_PATTERN.format(scene.scene_number)
            )
            if audio_seg.exists():
                dur = self.ffmpeg.get_audio_duration(audio_seg)
                if dur > 0:
                    return int(dur * 1000)
            return 10000

        def process_fallback_scene(scene):
            """Handle non-MapRender scene types (data_viz, split_map, hex_grid, stock_video, Ken Burns)."""
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
            audio_duration_ms = get_scene_audio_duration(scene)

            # ── Data Visualization scene ──
            if is_geography_mode and visual_type in ("data_viz", "data_visualization"):
                Messenger.info(f"   📊 Scene {scene.scene_number}: Rendering data visualization via Remotion...")
                floating_label = getattr(scene, "floating_label", "none")
                highlight_region = getattr(scene, "highlight_region", "none")
                map_pins = getattr(scene, "map_pins", [])
                vignettes = getattr(scene, "vignettes", [])

                data_points = []
                for pin in map_pins:
                    data_points.append({
                        "label": getattr(pin, "label", ""),
                        "value": float(getattr(pin, "value", "0").replace(",", "").replace("%", "")) / 100 if getattr(pin, "value", "") else 50,
                    })
                if not data_points:
                    for v in vignettes:
                        val_str = getattr(v, "value", "0").replace(",", "").replace("%", "")
                        try:
                            val = float(val_str) / 100
                        except ValueError:
                            val = 50
                        data_points.append({"label": getattr(v, "title", ""), "value": val})

                props = {
                    "chartType": "bar",
                    "title": highlight_region if highlight_region != "none" else "",
                    "mainValue": floating_label if floating_label != "none" else "",
                    "mainLabel": "",
                    "dataPoints": data_points or [{"label": "DATA A", "value": 75}, {"label": "DATA B", "value": 50}, {"label": "DATA C", "value": 90}],
                    "subtitle": "",
                    "audioDurationMs": audio_duration_ms,
                }
                try:
                    self.remotion.render_composition(remotion_path=Path(self.REMOTION_DIR), output_path=clip_path, composition_id="DataVisualization", props=props)
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                except Exception as e:
                    Messenger.error(f"   ❌ DataViz failed: {e}. Falling back to map_3d...")

            # ── Split Map scene ──
            if is_geography_mode and visual_type == "split_map":
                Messenger.info(f"   🗺️ Scene {scene.scene_number}: Rendering split map via Remotion...")
                pins_data = []
                for p in getattr(scene, "map_pins", []):
                    pins_data.append({
                        "latitude": p.latitude if hasattr(p, "latitude") else 0,
                        "longitude": p.longitude if hasattr(p, "longitude") else 0,
                        "label": p.label if hasattr(p, "label") else "",
                        "value": p.value if hasattr(p, "value") else "",
                    })
                left_cam = {"latitude": _get_camera_attr(scene, "latitude", 4.570868), "longitude": _get_camera_attr(scene, "longitude", -74.297333), "zoom": _get_camera_attr(scene, "zoom", 5.2), "label": getattr(scene, "highlight_region", "LOCATION A")}
                right_cam = {"latitude": _get_camera_attr(scene, "latitude", 40.7128) + 5, "longitude": _get_camera_attr(scene, "longitude", -74.006) + 10, "zoom": _get_camera_attr(scene, "zoom", 5.2), "label": getattr(scene, "floating_label", "LOCATION B")}
                if pins_data and len(pins_data) >= 2:
                    right_cam["latitude"] = pins_data[1]["latitude"]
                    right_cam["longitude"] = pins_data[1]["longitude"]
                    right_cam["label"] = pins_data[1]["label"]

                props = {"leftCamera": left_cam, "rightCamera": right_cam, "leftTitle": "THEN", "rightTitle": "NOW", "comparisonLabel": getattr(scene, "floating_label", ""), "audioDurationMs": audio_duration_ms}
                try:
                    self.remotion.render_composition(remotion_path=Path(self.REMOTION_DIR), output_path=clip_path, composition_id="SplitMap", props=props)
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                except Exception as e:
                    Messenger.error(f"   ❌ SplitMap failed: {e}. Falling back to map_3d...")

            # ── Hex Data Grid scene ──
            if is_geography_mode and visual_type == "hex_grid":
                Messenger.info(f"   🔲 Scene {scene.scene_number}: Rendering hex data grid via Remotion...")
                hex_grid_raw = getattr(scene, "hex_grid", None)
                hex_grid_title = ""
                hex_grid_items = []
                if hex_grid_raw:
                    hex_grid_title = getattr(hex_grid_raw, "title", "")
                    for item in getattr(hex_grid_raw, "items", []):
                        hex_grid_items.append({"icon": item.icon if hasattr(item, "icon") else "📊", "label": item.label if hasattr(item, "label") else "", "value": item.value if hasattr(item, "value") else "", "color": item.color if hasattr(item, "color") else "#FF0078"})
                props = {"title": hex_grid_title, "items": hex_grid_items, "audioDurationMs": audio_duration_ms}
                try:
                    self.remotion.render_composition(remotion_path=Path(self.REMOTION_DIR), output_path=clip_path, composition_id="HexDataGrid", props=props)
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                except Exception as e:
                    Messenger.error(f"   ❌ HexDataGrid failed: {e}. Falling back to map_3d...")
                    visual_type = "map_3d"

            # ── Final fallbacks: stock video or Ken Burns ──
            if visual_type not in ("map_3d", "ai_image"):
                if pexels_tool.fetch_video(query, clip_path):
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                if pixabay_tool.fetch_video(query, clip_path):
                    if clip_path.exists() and clip_path.stat().st_size > 1024:
                        return True
                Messenger.warning(f"   ⚠️ APIs failed for '{query}'. Falling back to Ken Burns.")

                if not img_path.exists() or img_path.stat().st_size < 1024:
                    Messenger.error(f"   ❌ Scene {scene.scene_number} missing image. CRITICAL.")
                    return False
                Messenger.info(f"   🎬 Ken Burns fallback for Scene {scene.scene_number}...")
                dur_secs = audio_duration_ms / 1000.0
                zoompan_frames = int(audio_duration_ms / 1000 * 25)
                try:
                    subprocess.run(["ffmpeg", "-loop", "1", "-i", str(img_path), "-vf", f"zoompan=z='min(zoom+0.0005,1.1)':d={zoompan_frames}:s=1080x1920", "-c:v", "libx264", "-crf", "18", "-t", str(dur_secs), "-pix_fmt", "yuv420p", "-y", str(clip_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception as ffmpeg_e:
                    Messenger.error(f"   ❌ FFmpeg fallback failed: {ffmpeg_e}")
                    return False
            return False

        is_geography_mode = getattr(idea_obj, "category", "") == "geography"
        all_map_render = all(
            getattr(s, "visual_type", "stock_video") in ("map_3d", "ai_image")
            for s in script.scenes
        )

        def render_map_scene(scene):
            """Render a single map_3d/ai_image scene via Remotion MapRender."""
            clip_filename = self.SCENE_VIDEO_PATTERN.format(scene.scene_number)
            clip_path = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, clip_filename)
            if clip_path.exists() and clip_path.stat().st_size > 10240:
                return True
            ad_ms = get_scene_audio_duration(scene)
            props = self._build_scene_props(idea_obj, scene, ad_ms, remotion_public_images)
            try:
                self.remotion.render_composition(
                    remotion_path=Path(self.REMOTION_DIR),
                    output_path=clip_path,
                    composition_id="MapRender",
                    props=props
                )
                return clip_path.exists() and clip_path.stat().st_size > 1024
            except Exception as e:
                Messenger.error(f"   ❌ MapRender failed for scene {scene.scene_number}: {e}")
                return False

        if is_geography_mode and all_map_render:
            Messenger.info(f"   🚀 Rendering all {len(script.scenes)} scenes in ONE Remotion call (MultiSceneVideo)...")
            scene_props_list = []
            for scene in script.scenes:
                ad_ms = get_scene_audio_duration(scene)
                scene_props_list.append(self._build_scene_props(idea_obj, scene, ad_ms, remotion_public_images))

            single_video = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, "temp_multi_scene.mp4")
            if single_video.exists():
                single_video.unlink()

            self.remotion.render_composition(
                remotion_path=Path(self.REMOTION_DIR),
                output_path=single_video,
                composition_id="MultiSceneVideo",
                props={"scenes": scene_props_list, "transitionFrames": 12}
            )

            if not single_video.exists() or single_video.stat().st_size < 1024:
                Messenger.error("   ❌ MultiSceneVideo render failed. Falling back to per-scene rendering.")
                all_map_render = False
            else:
                total_dur = self.ffmpeg.get_video_duration(single_video)
                Messenger.success(f"   ✅ MultiSceneVideo rendered: {single_video.stat().st_size / 1e6:.1f} MB, {total_dur:.1f}s")
                cum_secs = 0.0
                for scene in script.scenes:
                    ad_ms = get_scene_audio_duration(scene)
                    dur_secs = ad_ms / 1000.0
                    clip_filename = self.SCENE_VIDEO_PATTERN.format(scene.scene_number)
                    clip_path = self.get_idea_asset_path(idea_obj.id, self.CLIPS_DIR, clip_filename)
                    cmd = [
                        "ffmpeg", "-y",
                        "-ss", f"{cum_secs:.3f}",
                        "-i", str(single_video),
                        "-t", f"{dur_secs:.3f}",
                        "-c", "copy",
                        "-avoid_negative_ts", "make_zero",
                        str(clip_path)
                    ]
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    cum_secs += dur_secs
                    Messenger.info(f"   ✂️ Scene {scene.scene_number}: clipped {dur_secs:.1f}s → {clip_path.name}")
                Messenger.success("   ✅ All clips extracted from MultiSceneVideo.")
        else:
            Messenger.info(f"   🗺️ {len(script.scenes)} escenas, renderizando individualmente.")
            all_map_render = False

        if not all_map_render:
            results = []
            for scene in script.scenes:
                vt = getattr(scene, "visual_type", "stock_video")
                if vt == "hex_grid":
                    Messenger.info(f"   🗺️ Scene {scene.scene_number}: hex_grid -> map_3d (hex_grid no produce video con mapa)")
                    vt = "map_3d"
                if vt in ("map_3d", "ai_image"):
                    results.append(render_map_scene(scene))
                else:
                    results.append(process_fallback_scene(scene))
            if not all(results):
                Messenger.error("   ❌ One or more video clips failed. Stopping pipeline.")
                return

        idea_obj.state = State.CLIPS_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2b ready: {State.CLIPS_GENERATED} finalized.\n")

    def _resegment_by_audio_pauses(self, idea_id: int, script):
        """
        Re-segments scenes based on natural pauses detected in the master audio.
        Uses Whisper to find gaps >= 0.6s and splits scenes at those boundaries.
        """
        import json, shutil

        master_audio = self.get_idea_asset_path(idea_id, self.EDITIONS_DIR, "master_narration.wav")
        if not master_audio.exists():
            Messenger.warning("No master audio found for pause-based segmentation.")
            return script

        try:
            segments = self.whisper.get_transcription_segments(master_audio)
        except Exception as e:
            Messenger.warning(f"Whisper failed for pause detection: {e}")
            return script

        if len(segments) <= 1:
            return script

        # Detect gaps between segments
        gap_threshold = 0.6
        boundaries = [0]
        for i in range(1, len(segments)):
            gap = segments[i].start - segments[i-1].end
            if gap >= gap_threshold:
                boundaries.append(i)

        if len(boundaries) <= 1:
            return script

        # Group segments into scenes based on boundaries
        new_scenes = []
        for b_idx in range(len(boundaries)):
            start = boundaries[b_idx]
            end = boundaries[b_idx + 1] if b_idx + 1 < len(boundaries) else len(segments)
            chunk_segs = segments[start:end]

            combined_text = " ".join(s.text.strip() for s in chunk_segs)
            if not combined_text:
                continue

            # Find the closest original scene to inherit visual type/props
            orig_scene_idx = min(b_idx, len(script.scenes) - 1)
            orig_scene = script.scenes[orig_scene_idx]

            new_scene = orig_scene.__class__(
                scene_number=b_idx + 1,
                visual_type=getattr(orig_scene, "visual_type", "map_3d"),
                narration=combined_text,
                image_prompt=getattr(orig_scene, "image_prompt", None),
                pexels_query=getattr(orig_scene, "pexels_query", ""),
                camera=getattr(orig_scene, "camera", None),
                camera_path=getattr(orig_scene, "camera_path", []),
                highlight_region=getattr(orig_scene, "highlight_region", "none"),
                arrow_direction=getattr(orig_scene, "arrow_direction", "none"),
                floating_label=getattr(orig_scene, "floating_label", "none"),
                map_pins=getattr(orig_scene, "map_pins", []),
                vignettes=getattr(orig_scene, "vignettes", []),
                sfx=getattr(orig_scene, "sfx", "none"),
            )
            new_scenes.append(new_scene)

        if len(new_scenes) >= 2:
            Messenger.info(f"   Audio-driven resegmentation: {len(script.scenes)} -> {len(new_scenes)} scenes")
            script.scenes = new_scenes
            self.save_json(idea_id, self.SCRIPT_JSON, script)

        return script

    @retry(max_attempts=3)
    def step3_generate_audios(self):
        """
        Generate Audio: Batched AI-Guided Batching (Whisper + Gemini).
        Processes scenes in groups of 10 for maximum stability and alignment precision.
        Runs BEFORE step2b so video clips can use real audio duration.
        After generating audios, optionally re-segments scenes based on natural pauses.
        """
        idea_obj = self.store.get_first_by_state(State.IMAGES_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.error(f"No ideas ready for audio generation (target: State.IMAGES_GENERATED).")
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

        # Re-segment scenes based on natural audio pauses (for better visual sync)
        try:
            script_data = self.load_script(idea_obj)
            self._resegment_by_audio_pauses(idea_obj.id, script_data)
        except Exception as e:
            Messenger.warning(f"Audio resegmentation skipped: {e}")

    def step4_generate_videos(self):
        """
        Video Generation: Creates clips for each scene and merges them.
        Now with crossfade transitions between scenes.
        """
        # 1. Retrieves state
        idea_obj = self.store.get_first_by_state(State.CLIPS_GENERATED, category=self._category)
        if not idea_obj:
            Messenger.error("No clips ready for video generation.")
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

        # 5. Final video concatenation with crossfade transitions + Master Audio re-sync
        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        temp_video = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, "temp_concat.mp4")
        if len(scene_videos) > 1:
            self.ffmpeg.concat_with_crossfade(scene_videos, temp_video, transition_duration=0.4)
        else:
            self.ffmpeg.concat_videos(scene_videos, temp_video)
        
        # Merge concatenated video with the Master Audio
        # Pad the video if shorter than audio so no sentence gets cut off
        video_dur = self.ffmpeg.get_video_duration(temp_video)
        audio_dur = self.ffmpeg.get_audio_duration(master_audio)
        if video_dur > 0 and audio_dur > video_dur:
            pad_dur = audio_dur - video_dur
            Messenger.info(f"   ⏱️  Padding video by {pad_dur:.2f}s to match audio duration (crossfade compensation)...")
            padded_video = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, "temp_padded.mp4")
            cmd_pad = [
                "ffmpeg", "-y", "-i", str(temp_video),
                "-vf", f"tpad=stop_mode=clone:stop_duration={pad_dur}",
                "-c:a", "copy", "-shortest",
                str(padded_video)
            ]
            subprocess.run(cmd_pad, check=True)
            merge_input = padded_video
        else:
            merge_input = temp_video

        cmd_merge = [
            "ffmpeg", "-y", "-i", str(merge_input), "-i", str(master_audio),
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
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED, category=self._category)
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
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED, category=self._category)
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
        
        # Get top headline from idea.json (raw dict to avoid model dependency)
        import json as json_lib
        try:
            idea_json_path = self.get_idea_path(idea_obj.id) / self.IDEA_JSON
            with open(idea_json_path, encoding="utf-8") as f:
                idea_dict = json_lib.load(f)
            intrigue_text = idea_dict.get("intrigue_header", None)
        except Exception:
            intrigue_text = None

        # Build level markers for seven_levels mode
        level_markers = []
        if self.mode == "seven_levels":
            try:
                total_duration = self.ffmpeg.get_audio_duration(audio_wav) * 1000
                from flows.image_content_generator.pipeline.prompt_shorts.seven_levels.models import SevenLevelsHandler
                seven_script = self.load_json(idea_obj.id, self.SCRIPT_JSON, SevenLevelsHandler)
                scene_count = len(seven_script.scenes) or 1
                for i, sc in enumerate(seven_script.scenes):
                    if hasattr(sc, "nivel") and sc.nivel > 0:
                        start_ms = (i / scene_count) * total_duration
                        end_ms = ((i + 1) / scene_count) * total_duration
                        level_markers.append({
                            "nivel": sc.nivel,
                            "titulo": getattr(sc, "level_title", f"Level {sc.nivel}"),
                            "impacto": getattr(sc, "impact", "Medium"),
                            "startTime": int(start_ms),
                            "endTime": int(end_ms),
                        })
                Messenger.success(f"   ✅ Built {len(level_markers)} level markers for 7 Levels mode.")
            except Exception as e:
                Messenger.warning(f"   ⚠️ Failed to build level markers: {e}")

        self.remotion.render_subtitles(
            remotion_path=remotion_root,
            output_path=remotion_overlay,
            words=word_data,
            top_headline=intrigue_text,
            level_markers=level_markers if level_markers else None
        )

        # 4. Composite remotion_overlay (green screen) + grain + progress bar
        import subprocess
        duration = self.ffmpeg.get_video_duration(raw_video)
        
        fc = (
            f"[0:v]noise=alls=3:allf=t+u[v_grain];"
            f"[v_grain]drawbox=y=0:w=iw:h=3:color=black@0.6:t=fill[v_bar_bg];"
            f"[v_bar_bg]drawbox=y=0:w=iw*t/{duration}:h=3:color=#FFEA00@1.0:t=fill[v_base];"
            f"[1:v]colorkey=0x00FF00:0.15:0.08[ck];"
            f"[v_base][ck]overlay[v_out]"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(remotion_overlay),
            "-filter_complex", fc,
            "-map", "[v_out]", "-map", "0:a",
            "-c:v", "libx264", "-crf", "18", "-c:a", "copy", "-pix_fmt", "yuv420p",
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

        # 5. Mix SFX if available
        sfx_dir = self.resource_base / self.SFX_DIR
        if sfx_dir.exists():
            from tools.audio_generation.audio_tool import AudioTool
            sfx_tool = AudioTool(bg_music_dir=sfx_dir)
            sfx_file = sfx_tool.get_random_audio()
            if sfx_file:
                sfx_mixed = self.get_idea_asset_path(
                    idea_obj.id, self.EDITIONS_DIR, "temp_sfx_mixed.mp4"
                )
                self.ffmpeg.mix_sfx(
                    final_with_music, sfx_file, sfx_mixed, volume=0.35
                )
                import shutil
                shutil.move(str(sfx_mixed), str(final_with_music))

        # 6. Updates state.
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


