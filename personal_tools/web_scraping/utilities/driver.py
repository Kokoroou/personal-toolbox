"""
Utility functions for working with selenium driver
"""
import os
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def create_driver(
        headless: bool = True,
        detach: bool = False
) -> webdriver:
    """
    Initialize chrome driver with profile
    :param headless: Whether to run the chrome driver in headless mode.
        If True, the chrome driver will not be visible.
    :param detach: Whether to detach the chrome driver from the terminal.
        If True, the chrome driver will not be closed when the terminal is closed.
    :return: A Chrome driver
    """
    window_size = "1000,2000"
    prefs = {"profile.default_content_setting_values.notifications": 2}

    chrome_options = Options()

    chrome_options.add_argument('disable-infobars')

    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-blink-features=AutomationControllered")
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--disable-feature=IsolateOrigins,site-per-process")
    if os.name == 'nt':
        chrome_options.add_argument('--disable-gpu')  # Windows workaround
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-web-security")
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-certificate-error-spki-list")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")  # open Browser in maximized mode
    chrome_options.add_argument(f"--window-size={window_size}")
    chrome_options.add_argument("--verbose")

    chrome_options.add_experimental_option("detach", detach)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def find_elements_by_text(driver: webdriver, text: str) -> List[WebElement]:
    """
    Find elements by text
    :param driver: The driver to use
    :param text: The text to search for
    :return: A list of elements that match the search text
    """
    return driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")


def find_elements_by_attribute(driver: webdriver, attribute: str, value: str) -> List[WebElement]:
    """
    Find elements by attribute
    :param driver: The driver to use
    :param attribute: The attribute to search for
    :param value: The value of the attribute to search for
    :return: A list of elements that match the search attribute and value
    """
    return driver.find_elements(By.XPATH, f"//*[@{attribute}='{value}']")
