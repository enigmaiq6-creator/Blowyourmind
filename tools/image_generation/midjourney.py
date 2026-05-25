from collections import deque
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import BaseModel

from tools.common.messenger import Messenger
from tools.midjourney.base_bot import MJ_IMAGINE_COMMAND, MediaType, MidjourneyBot


class ImageTask(BaseModel):
    """
    Represents a single image generation task for batch processing.
    """
    prompt: str
    output_path: Path
    is_video: bool = False


class ActiveJob(BaseModel):
    """
    Wraps a task with its start time to handle timeouts.
    """
    task: ImageTask
    start_time: datetime

    @property
    def duration(self) -> float:
        """Returns elapsed time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


class MidjourneyImageGenerator(MidjourneyBot):
    """
    Bot specifically configured to generate standalone images via Midjourney.
    """
    style_param: str
    BATCH_SIZE: int = 7
    TASK_TIMEOUT_SECONDS: int = 300

    def __init__(self, style_param: str = ""):
        """
        Initializes the MidjourneyImageBot.
        """
        super().__init__(style_param=f" {style_param}" if style_param else "")

    def _format_prompt(self, prompt: str) -> str:
        return f"{MJ_IMAGINE_COMMAND}{prompt}{self.style_param}"

    def generate_image(self, prompt: str, output_path: Path):
        """
        Main entry point for generating a single image via Midjourney.

        Steps:
        1. Format and send the '/imagine' command with the required suffix.
        2. Wait for the finished Midjourney result using the `wait_for_midjourney_result` method.
        3. Process and download the resulting image.
        """
        Messenger.step_success(f"Generating Image: {prompt}")

        # Step 1: Send the /imagine command
        prompt_command = self._format_prompt(prompt)
        self.send_message(text=prompt_command)

        # Step 2: Wait for the finished Midjourney result
        mj_data = self.wait_for_midjourney_result(
            content_id=prompt,
        )

        # Step 3: Process the found image
        Messenger.success(f"Found image in Discord: {mj_data.filename}")
        self.download_midjourney_media(
            mj_filename=mj_data.filename,
            output_path=output_path,
            media_type=MediaType.IMAGE,
            index=0,
        )

    def generate_images(self, tasks: List[ImageTask]):
        """
        Generates images using a centralized, single-threaded sliding-window pool.
        """
        Messenger.info(f"Batch Processing: {len(tasks)} images (Window: {self.BATCH_SIZE})")

        pending = deque(tasks)
        active: List[ActiveJob] = []
        completed_count = 0

        while active or pending:
            # 1. Fill the window
            while len(active) < self.BATCH_SIZE and pending:
                task = pending.popleft()
                Messenger.info(f"Triggering (Pending: {len(pending)}): {task.prompt}")
                self.send_message(text=self._format_prompt(task.prompt))
                active.append(ActiveJob(task=task, start_time=datetime.now()))

            # 2. Poll and Monitor
            still_active: List[ActiveJob] = []
            for job in active:
                # Check for individual timeout
                if job.duration > self.TASK_TIMEOUT_SECONDS:
                    Messenger.warning(f"Timed out after {job.duration:.0f}s: {job.task.prompt}")
                    continue

                # Check status via UI
                mj_data = self.search_midjourney_in_ui(job.task.prompt)
                if not mj_data:
                    still_active.append(job)
                    continue

                Messenger.success(f"Completed: {job.task.prompt}")
                self.download_midjourney_media(
                    mj_filename=mj_data.filename,
                    output_path=job.task.output_path,
                    media_type=MediaType.IMAGE
                )
                completed_count += 1

            active = still_active

        # 3. Final Validation
        Messenger.step_success(f"Process ended. Success: {completed_count}/{len(tasks)}")
        if completed_count < len(tasks):
            raise RuntimeError(f"Generation incomplete: {len(tasks) - completed_count} failed.")


# MidjourneyImageGenerator().generate_image(
#     prompt="a dog with a red hat",
#     output_path=Path("temp/temp.png"),
# )
