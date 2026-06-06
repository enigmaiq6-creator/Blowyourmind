import random
import time
from pathlib import Path
from typing import Any, List, Optional

from google import genai
from google.genai import types

from pathlib import Path
from typing import List
from pydantic import BaseModel

from tools.common.messenger import Messenger
from tools.utils.time import retry


class ImageTask(BaseModel):
    prompt: str
    output_path: Path
    is_video: bool = False


class VertexAIImageGenerator:
    """
    Generator that uses the NEW google-genai SDK to generate 
    "Live Images" (animated 4-second video clips) via generate_videos.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        aspect_ratio: str = "9:16",
        **kwargs: Any
    ) -> None:
        self.project_id = project_id
        self.location = location
        self.aspect_ratio = aspect_ratio
        
        # Initialize the new GenAI Client
        self.client = genai.Client(
            vertexai=True, 
            project=self.project_id, 
            location=self.location
        )

    def generate_image(
        self,
        prompt: str,
        output_path: Path,
    ) -> None:
        """
        Generates a static image using Imagen 3 via Vertex AI.
        Includes robust exponential backoff to handle 429 RESOURCE_EXHAUSTED errors.
        """
        Messenger.info(f"Generating Vertex AI Image: {prompt[:50]}...")
        
        max_attempts = 6
        base_delay = 10.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=self.aspect_ratio,
                    )
                )

                if not response or not response.generated_images:
                    raise RuntimeError("❌ Vertex AI Imagen no devolvió imágenes")

                # Save the image
                with open(output_path, "wb") as f:
                    f.write(response.generated_images[0].image.image_bytes)
                
                Messenger.image(f"Imagen generada con éxito: {output_path}")
                return
            except Exception as e:
                error_str = str(e)
                Messenger.warning(f"⚠️ Attempt {attempt}/{max_attempts} failed: {error_str}")
                
                if attempt == max_attempts:
                    raise e
                
                # Check for rate limits / 429
                is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower()
                sleep_time = (base_delay * (2 ** (attempt - 1))) + random.uniform(1.0, 3.0)
                
                if is_rate_limit:
                    Messenger.warning(f"🛑 Rate limit/Quota exhausted. Sleeping for {sleep_time:.2f}s before retrying...")
                else:
                    Messenger.warning(f"🔄 General exception. Sleeping for {sleep_time:.2f}s before retrying...")
                
                time.sleep(sleep_time)

    @retry(max_attempts=3, delay=10.0)
    def generate_video(
        self,
        prompt: str,
        output_path: Path,
    ) -> None:
        """
        Generates an animated clip using Veo 2 (veo-2.0-generate-001) via Vertex AI.
        """
        Messenger.info(f"Generating Vertex AI Video (Veo 2): {prompt[:50]}...")
        
        # Trigger Asynchronous Generation
        operation = self.client.models.generate_videos(
            model='veo-2.0-generate-001',
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=self.aspect_ratio,
            )
        )

        # Polling for Completion
        while not operation.done:
            Messenger.info("⏳ Waiting for Veo 2 video generation (polling)...")
            time.sleep(15)
            operation = self.client.operations.get(operation)

        if operation.error:
            raise RuntimeError(f"❌ Video generation failed: {operation.error}")

        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError("❌ Vertex AI Veo no devolvió videos")

        # Save the video
        video_metadata = operation.response.generated_videos[0]
        video_obj = video_metadata.video
        
        if video_obj.video_bytes:
            with open(output_path, "wb") as f:
                f.write(video_obj.video_bytes)
        else:
            # Fallback to save method if bytes are not directly available
            video_obj.save(str(output_path))
        
        Messenger.success(f"Video animado generado con éxito: {output_path}")

    def generate_images(self, tasks: List[ImageTask]) -> None:
        """
        Batch processing for Vertex AI Images using ThreadPoolExecutor.
        """
        total = len(tasks)
        Messenger.info(f"Vertex AI Image Generation Batch: {total} images (Sequential with max_workers=1 to prevent rate limits)")

        def process_task(item):
            i, task = item
            out_path = task.output_path
            
            if out_path.exists():
                Messenger.info(f"Skipping {out_path.name}: File already exists.")
                return True

            Messenger.info(f"Processing Scene {i}/{total}: {out_path.name}")
            try:
                if task.is_video:
                    self.generate_video(
                        prompt=task.prompt,
                        output_path=out_path
                    )
                else:
                    self.generate_image(
                        prompt=task.prompt,
                        output_path=out_path
                    )
                # Add a brief delay between sequential requests to prevent triggering rate limits
                time.sleep(2.0)
                return True
            except Exception as e:
                Messenger.error(f"Error in scene {i}: {str(e)}")
                # Return False but don't re-raise — let the batch decide
                return False

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            results = list(executor.map(process_task, enumerate(tasks, start=1)))

        successful = sum(results)
        failed = total - successful
        Messenger.step_success(f"Batch complete: {successful}/{total} scenes processed successfully.")

        # Only stop the pipeline if MORE than half the images failed.
        # A single failed scene (e.g. due to content policy) should not kill the whole video.
        if successful == 0:
            raise RuntimeError(f"❌ ALL {total} images failed to generate. Stopping pipeline.")
        elif failed > total // 2:
            raise RuntimeError(f"❌ Too many failures ({failed}/{total}). Stopping pipeline.")
        elif failed > 0:
            Messenger.warning(f"⚠️ {failed} scene(s) failed but pipeline will continue with the {successful} successful images.")
