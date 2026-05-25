import uuid
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from tools.chrome.driver import find_element, upload_file
from tools.common.messenger import Messenger
from tools.midjourney.base_bot import (
    INPUT_TEXT_MESSAGE_SELECTOR,
    MJ_IMAGINE_COMMAND,
    MediaType,
    MidjourneyBot,
)

INPUT_FILE_SELECTOR = "input.file-input"
MJ_VIDEO_SUFFIX_PARAM = " --ar 9:16 --video"


class MidjourneyVideoGenerator(MidjourneyBot):
    """
    Bot specifically configured to generate video files via Midjourney start frames.
    """
    style_param: str

    def __init__(self, style_param: str = ""):
        """
        Initializes the MidjourneyImageBot.
        """
        super().__init__(style_param=f" {style_param}" if style_param else "")

    def send_image_to_discord(self, driver: WebDriver, image_path: Path, key: str):
        """
        Uploads an image to Discord and associates it with a key.

        Steps:
        1. Locates the Discord text input and types the key.
        2. Uploads the image file.
        3. Waits for the image upload element to appear.
        4. Presses ENTER to submit the message.
        """
        # Step 1: Locates the Discord text input and types the key.
        message_input = find_element(
            driver=driver,
            selector=(By.CSS_SELECTOR, INPUT_TEXT_MESSAGE_SELECTOR),
        )
        message_input.send_keys(key)

        # Step 2: Uploads the image file.
        upload_file(
            driver=driver,
            file_path=image_path,
            selector=(By.CSS_SELECTOR, INPUT_FILE_SELECTOR),
        )

        # Step 3: Waits for confirmation of the uploaded image preview in the UI based on key.
        find_element(
            driver=driver,
            selector=(By.XPATH, f"//span[text()='{key}']"),
        )

        # Step 4: Presses ENTER to submit the message.
        message_input.send_keys(Keys.RETURN)

    def send_start_frame(self, start_frame: Path) -> str:
        """
        Sends the start frame image to Discord to generate a useable URL.

        Steps:
        1. Generates a unique key for the message content and uploads the image to Discord.
        2. Polls Discord messages using the `wait_for_midjourney_result` method.
        3. Returns the Discord URL of the uploaded start frame image.

        Args:
            start_frame (Path): The local path to the start frame image.

        Returns:
            str: The URL of the uploaded start frame image.
        """
        # Step 1: Generate key and upload image
        key = str(uuid.uuid4())
        self.send_image_to_discord(
            driver=self.driver,
            image_path=start_frame,
            key=key,
        )

        # Step 2: Poll Discord messages
        mj_data = self.wait_for_midjourney_result(
            content_id=key,
        )

        # Step 3: Extract URL and return
        return mj_data.image_url

    def generate_video(self, start_frame: Path, prompt: str, output_path: Path):
        """
        Generates a video via Midjourney using a start frame image and a text prompt.

        Steps:
        1. Uploads the start frame image to Discord to obtain a useable URL.
        2. Formats and sends the '/imagine' command with the image URL and video suffix.
        3. Wait for the finished Midjourney result using the `wait_for_midjourney_result` method.
        4. Processes and downloads the resulting generated video.

        Args:
            start_frame (Path): The local path to the start frame image.
            prompt (str): The visual description for the video.
            output_path (Path): The local path where the final video will be saved.
        """
        Messenger.step_success(f"Generating Video: {prompt}")

        # Step 1: Send the start frame to generate url
        start_frame_url = self.send_start_frame(start_frame=start_frame)

        # Step 2: Send the /imagine command
        prompt_command = (
            f"{MJ_IMAGINE_COMMAND}{start_frame_url} {prompt}{MJ_VIDEO_SUFFIX_PARAM}"
        )
        self.send_message(text=prompt_command)

        # Step 3: Wait for the finished Midjourney result
        mj_data = self.wait_for_midjourney_result(
            content_id=prompt,
        )

        # Step 4: Process the found video
        Messenger.success(f"Found video URL: {mj_data.filename}")
        self.download_midjourney_media(
            mj_filename=mj_data.filename,
            output_path=output_path,
            media_type=MediaType.VIDEO,
            index=0,
        )


# MidjourneyVideoGenerator().generate_video(
#     start_frame="temp/start_image.webp",
#     prompt="a dog with a red hat",
#     output_path=Path("temp/temp.png"),
# )
