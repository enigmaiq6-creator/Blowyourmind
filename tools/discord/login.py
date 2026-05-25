import random
import time
from typing import Any, cast

from pydantic import PrivateAttr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tools.common.base_model import BaseModelTool
from tools.env_settings.settings import ENV_SETTINGS


class DiscordBot(BaseModelTool):
    _driver: WebDriver = PrivateAttr()

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        self._driver = cast(Any, webdriver).Chrome(options=chrome_options)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    def human_like_typing(self, element: WebElement, text: str):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def login(
        self,
        website: str,
        user: str,
        password: str,
        user_name_element: str,
        pass_name_element: str,
    ) -> WebDriver:
        # Open Website and log in
        self.driver.get(website)
        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        time.sleep(3)

        email_input = self.driver.find_element(By.NAME, user_name_element)
        password_input = self.driver.find_element(By.NAME, pass_name_element)
        self.human_like_typing(element=email_input, text=user)
        self.human_like_typing(element=password_input, text=password)
        password_input.send_keys(Keys.RETURN)

        return self.driver

    def get_discord_driver(self) -> WebDriver:
        self.login(
            website="https://discord.com/login",
            user=ENV_SETTINGS.DISCORD_EMAIL,
            password=ENV_SETTINGS.DISCORD_PASSWORD,
            user_name_element="email",
            pass_name_element="password",
        )

        if not self.driver:
            raise RuntimeError("Driver not initialized")

        WebDriverWait(self.driver, 40).until(
            EC.url_to_be("https://discord.com/channels/@me")
        )
        time.sleep(5)

        # Open the chat based on the provided URL
        self.driver.get(ENV_SETTINGS.DISCORD_CHAT_URL)
        time.sleep(5)  # Wait for the page to load

        return self.driver
