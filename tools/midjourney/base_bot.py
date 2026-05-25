import re
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, cast

import pytz
import requests
from pydantic import BaseModel, PrivateAttr
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from tools.chrome.driver import find_element
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger
from tools.discord.login import DiscordBot
from tools.env_settings.settings import ENV_SETTINGS
from tools.utils.time import retry, sleep_decorator

MAX_GRACE_PERIOD = timedelta(minutes=5)
INPUT_TEXT_MESSAGE_SELECTOR = 'div[role="textbox"][contenteditable="true"][data-slate-editor="true"]'  # noqa: E501
MJ_IMAGINE_COMMAND = "/imagine "
UUID_PATTERN = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
MESSAGES_ENDPOINT_URL = ENV_SETTINGS.DISCORD_MESSAGES_ENDPOINT
MESSAGE_LIST_ITEM_SELECTOR = '[class^="messageListItem"]'
ORIGINAL_LINK_SELECTOR = 'a[class*="originalLink"]'
PERCENTAGE_PATTERN = r"\(\d+%\)"


class MidjourneyForbiddenError(Exception):
    """Exception raised when Midjourney returns a 403 Forbidden error."""
    pass


class MidjourneyData(BaseModel):
    image_url: str
    image_proxy_url: str
    filename: str


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class GenerationMode(str, Enum):
    FAST = "(fast)"
    TURBO = "(turbo)"
    RELAXED = "(relaxed)"


class MidjourneyBot(BaseModelTool):
    """
    A bot to automate image generation via Midjourney on Discord.
    """
    _driver: WebDriver = PrivateAttr()

    @property
    def driver(self) -> WebDriver:
        return self._driver

    def __init__(self, **kwargs: Any):
        """
        Initializes the MidjourneyBot by establishing a Discord session.

        Steps:
        1. Retrieve an authenticated Selenium WebDriver via the Discord tool.
        2. Initialize the parent BaseModelTool with the driver.
        """
        super().__init__(**kwargs)
        # Step 1: Get an authenticated driver from the Discord tool
        self._driver = DiscordBot().get_discord_driver()

    def _is_generation_finished(self, text: str) -> bool:
        """
        Verifies if a Midjourney generation has finished based on message text.

        The final state is reached when:
        1. No percentage pattern (e.g. '(79%)') is present.
        2. One of the generation mode keywords (e.g. '(fast)', '(relaxed)') is present.
        """
        has_percentage = re.search(PERCENTAGE_PATTERN, text)
        has_mode = any(mode.value in text for mode in GenerationMode)
        return not has_percentage and has_mode

    @sleep_decorator(3, 5)
    def get_midjourney_message(
        self,
        content_message_id: str,
        send_time: datetime,
    ) -> Optional[MidjourneyData]:
        """
        Searches through Discord messages to find the generated image post.

        Steps:
        1. Fetches the last 50 messages from Discord.
        2. Iterates through the provided list of messages.
        3. Checks if the content_message_id text is present in the message content.
        4. Verifies the message type is 0 (standard message) and newer than 'send_time'.
        5. Returns the MidjourneyData object if a match is found.
        """
        # Step 1: Fetches the last 50 messages from Discord.
        params = {"limit": 50}
        headers = {
            "Authorization": ENV_SETTINGS.DISCORD_TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(
            url=MESSAGES_ENDPOINT_URL, params=params, headers=headers
        )
        if response.status_code != 200:
            raise Exception("Last message from Discord not found")

        # Step 2: Iterates through the provided list of messages.
        messages_data = response.json()
        for message_data in messages_data:
            # Step 3: Checks if the content_message_id text is present, message type is 0,
            # and newer than 'send_time'.
            if (
                content_message_id in message_data["content"]
                and message_data["type"] == 0
                and send_time <= datetime.fromisoformat(message_data["timestamp"])
                and self._is_generation_finished(message_data["content"])
            ):
                image_url = message_data["attachments"][0]["url"]
                image_proxy_url = message_data["attachments"][0]["proxy_url"]
                filename = message_data["attachments"][0]["filename"]

                # Step 4: Returns the MidjourneyData object if a match is found.
                return MidjourneyData(
                    image_url=image_url,
                    image_proxy_url=image_proxy_url,
                    filename=filename,
                )

        return None

    @retry(max_attempts=3, delay=5, exceptions=(MidjourneyForbiddenError,))
    def download_midjourney_media(
        self,
        mj_filename: str,
        output_path: Path,
        media_type: MediaType,
        index: int = 0
    ):
        """
        Downloads a Midjourney media file (image or video) from the CDN and saves it.

        Steps:
        1. Search for the UUID pattern in the filename.
        2. Prepare the subdirectory structure.
        3. Determine the direct CDN URL based on media_type.
        4. Extract real browser identity from Selenium.
        5. Save the media file locally.
        """
        # Step 1: Search for the UUID pattern in the filename
        match = re.search(UUID_PATTERN, mj_filename)
        uuid_filename = match.group(0) if match else None
        assert uuid_filename

        # Step 2: Prepare the subdirectory structure
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 3: Download the media
        if media_type == MediaType.VIDEO:
            media_url = f"https://cdn.midjourney.com/video/{uuid_filename}/{index}.mp4"
            Messenger.info(f"Downloading Midjourney video to: {output_path}")
        else:
            media_url = f"https://cdn.midjourney.com/{uuid_filename}/0_{index}.jpeg"
            Messenger.info(f"Downloading Midjourney image to: {output_path}")

        Messenger.info(f"Source URL: {media_url}")

        # Step 4: Extract real browser identity from Selenium
        user_agent = cast(str, cast(Any, self.driver).execute_script("return navigator.userAgent"))
        selenium_cookies = cast(List[dict[str, Any]], cast(Any, self.driver).get_cookies())
        cookies = {cast(str, c["name"]): c["value"] for c in selenium_cookies}
        headers = {
            "User-Agent": user_agent,
            "Referer": "https://www.midjourney.com/",
        }
        response = requests.get(media_url, headers=headers, cookies=cookies)

        # Step 5: Save the media file
        if response.ok:
            with open(output_path, "wb") as file:
                file.write(response.content)
        else:
            if response.status_code == 403:
                Messenger.warning(
                    f"403 Forbidden error detected for {media_type.value}.\n"
                    f"Source URL: {media_url}. Retrying..."
                )
                raise MidjourneyForbiddenError(f"403 Forbidden: {media_type.value}")

            Messenger.error(
                f"Failed to download {media_type.value} from Midjourney.\n"
                f"Status Code: {response.status_code}\n"
                f"Source URL: {media_url}"
            )
            raise Exception(f"Download failed ({response.status_code}): {media_type.value}")

    @sleep_decorator(1, 2)
    def send_message(self, text: str):
        """
        Sends a message to the Discord chat using Selenium WebDriver.
        """
        # Step 1: Locates the Discord text input element.
        message_input = find_element(
            driver=self.driver,
            selector=(By.CSS_SELECTOR, INPUT_TEXT_MESSAGE_SELECTOR),
        )

        # Step 2: Special logic for the slash command to trigger Midjourney's prompt UI
        if MJ_IMAGINE_COMMAND in text:
            message_input.send_keys(MJ_IMAGINE_COMMAND)
            text = text.replace(MJ_IMAGINE_COMMAND, "")
            time.sleep(1)

        # Step 3: Types the remaining prompt text.
        message_input.send_keys(text)
        time.sleep(0.5)

        # Step 4: Presses ENTER to submit the message.
        message_input.send_keys(Keys.RETURN)

    @sleep_decorator(3, 5)
    def search_midjourney_in_ui(self, content_id: str) -> Optional[MidjourneyData]:
        """
        Fallback: Searches for the Midjourney result directly in the Discord UI.
        Useful for ephemeral messages or when the API history is delayed.
        """
        try:
            # Find all message items
            # The class names are dynamic but usually start with these prefixes
            messages = self.driver.find_elements(By.CSS_SELECTOR, MESSAGE_LIST_ITEM_SELECTOR)

            # Iterate backwards (latest first)
            for msg in reversed(messages):
                msg_text = msg.text
                is_finished = self._is_generation_finished(msg_text)
                if not (content_id in msg_text and is_finished):
                    continue

                # Found the message container, now look for the original link
                link_elements = msg.find_elements(By.CSS_SELECTOR, ORIGINAL_LINK_SELECTOR)
                if not link_elements:
                    continue

                url = cast(str | None, cast(Any, link_elements[0]).get_attribute("href"))
                if url is None:
                    continue

                # Use UUID_PATTERN to extract the matching part from the URL
                match = re.search(UUID_PATTERN, url)
                if not match:
                    continue

                # Use the UUID as the filename
                filename = match.group(0)

                return MidjourneyData(
                    image_url=url, image_proxy_url=url, filename=filename
                )
        except (StaleElementReferenceException, NoSuchElementException):
            # If the UI updates while we are searching, we just skip this poll
            # and try again in the next iteration of the wait loop.
            Messenger.warning("UI updated during search. Retrying in next poll...")
            return None

        return None

    def wait_for_midjourney_result(self, content_id: str) -> MidjourneyData:
        """
        Polls Discord for a Midjourney result matching the content_id.
        Prioritizes UI search, then falls back to API polling in a loop.

        Steps:
        1. Execute a polling loop until `MAX_GRACE_PERIOD`.
        2. In each iteration, try to find a finished result in the Discord UI.
        3. If not found in UI, try to find a finished result via the Discord API.
        4. If a results is found by either method, return it.
        5. If `MAX_GRACE_PERIOD` is exceeded, raise a RuntimeError.
        """
        send_time = datetime.now(pytz.utc)

        while datetime.now(pytz.utc) - send_time < MAX_GRACE_PERIOD:
            # Step 1: Prioritize searching the Discord UI
            mj_data = self.search_midjourney_in_ui(content_id=content_id)
            if mj_data:
                return mj_data

            # Step 2: Fall back to standard API polling
            try:
                mj_data = self.get_midjourney_message(
                    content_message_id=content_id,
                    send_time=send_time,
                )
                if mj_data:
                    return mj_data
            except Exception as e:
                # API polling might fail temporarily; log and continue
                Messenger.warning(f"API polling encountered an error: {e}")

        # If we exit the loop, the generation timed out
        error_msg = (
            f"Midjourney failed to generate content for '{content_id}' "
            f"within {MAX_GRACE_PERIOD}"
        )
        raise RuntimeError(error_msg)
