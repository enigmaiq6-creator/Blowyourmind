import os
import time
from pathlib import Path
from typing import Any, Callable, cast

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tools.utils.time import sleep_decorator

# TODO: solve casts


def web_selector(method: Callable[[WebDriver], Any], driver: WebDriver) -> Any:
    try:
        return cast(Any, WebDriverWait(driver, 60)).until(method=method)
    except Exception as e:
        raise ValueError("Selector method not found ", e)


@sleep_decorator(4, 8)
def click_element(
    driver: WebDriver,
    selector: tuple[str, str],
    with_script: bool,
) -> None:
    """
    Clicks the on element on the page.
    """
    try:
        element = cast(
            WebElement,
            web_selector(method=EC.element_to_be_clickable(selector), driver=driver)
        )

        ActionChains(driver).move_to_element(element).perform()

        # Click the button
        if with_script:
            cast(Any, driver).execute_script("arguments[0].click();", element)
        else:
            element.click()

    except ElementClickInterceptedException:
        print("Retrying, due Error: ElementClickInterceptedException")
        time.sleep(5)
        click_element(driver=driver, selector=selector, with_script=with_script)

    except Exception as e:
        raise RuntimeError("Cannot click on element ", e)


def send_keys(driver: WebDriver, element: WebElement, custom_text: str) -> None:
    """
    Sends keys to an element using ActionChains.
    """
    # Use ActionChains for typing with pauses between each keystroke
    actions = ActionChains(driver)
    actions.click(element)
    actions.send_keys(custom_text)
    actions.perform()


@sleep_decorator(1, 2)
def find_element(driver: WebDriver, selector: tuple[str, str]) -> WebElement:
    """
    Finds an element
    """
    try:
        element = cast(WebElement, web_selector(
            method=EC.presence_of_element_located(selector),
            driver=driver,
        ))

        return element
    except Exception as e:
        raise RuntimeError("Cannot found element ", e)


@sleep_decorator(3, 5)
def upload_file(driver: WebDriver, file_path: Path, selector: tuple[str, str]) -> None:
    """
    Uploads a file to the specified element.
    """
    try:
        abs_file_path = os.path.abspath(file_path)

        # Wait for the upload input field to be present
        upload_input = cast(WebElement, web_selector(
            method=EC.presence_of_element_located(selector),
            driver=driver,
        ))

        # Clear the upload input field before sending the file path
        cast(Any, driver).execute_script("arguments[0].value = '';", upload_input)
        time.sleep(1)

        # Send the file path to the upload input element
        upload_input.send_keys(abs_file_path)

    except Exception as e:
        raise RuntimeError("Cannot fill field ", e)
