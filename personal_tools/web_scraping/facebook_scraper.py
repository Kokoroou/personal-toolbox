"""
Facebook Scraper
"""

import argparse
import os
import traceback
from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from selenium.webdriver.common.by import By

from personal_tools.web_scraping.utilities.driver import create_driver
from personal_tools.web_scraping.utilities.encoding import get_2fa_code


def get_args():
    """Get parsed arguments from command line."""
    parser = argparse.ArgumentParser(description='Facebook Scraper')

    # Environment variables
    parser.add_argument('--env', type=str, default='./.env', help='Path to .env file.')

    # Scraper configuration
    parser.add_argument('--source', type=str, help='Source of the data', required=True,
                        choices=['group', 'page', 'profile', 'all'])
    parser.add_argument('--max', type=int, help='Maximum number of posts to scrape', default=100)
    parser.add_argument('--output', type=str, help='Output folder', default='./data')
    parser.add_argument('--media', type=str, help='Media type to scrape', default='all',
                        nargs='+', choices=['all', 'photo', 'video', 'link', 'text'])

    # Details
    parser.add_argument('--id', type=str,
                        help='ID of the group, page or profile if source is not "all"',
                        required=("--source" in ["group", "page", "profile"]))

    return parser.parse_args()


class FacebookScraper:
    """
    Facebook Scraper
    """

    def __init__(self, username: str, password: str, key_2fa: str):
        self.output_folder = None
        self.web_driver = create_driver(headless=False, detach=False)

        self.login(username, password, key_2fa)

    def login(self, username: str, password: str, key_2fa: str):
        """
        Login to Facebook
        """
        print("\nLogin...")

        # Open Facebook login page
        sleep(1)
        self.web_driver.get("https://mbasic.facebook.com/login")

        # Input username
        sleep(1)  # Wait for page load
        user_name_element = self.web_driver.find_elements(By.CSS_SELECTOR, "#m_login_email")
        user_name_element[0].send_keys(username)

        # Input password
        sleep(1)  # Wait for robot check
        password_element = self.web_driver.find_elements(
            By.CSS_SELECTOR, "#login_form > ul > li:nth-child(2) > section > input"
        )
        password_element[0].send_keys(password)

        # Click submit button
        sleep(1)  # Wait for robot check
        btn_submit = self.web_driver.find_elements(
            By.CSS_SELECTOR, "#login_form > ul > li:nth-child(3) > input"
        )
        btn_submit[0].click()

        # Input 2fa code
        code_2fa = get_2fa_code(key_2fa)
        sleep(1)  # Wait for robot check
        code_2fa_element = self.web_driver.find_elements(By.CSS_SELECTOR, "#approvals_code")
        code_2fa_element[0].send_keys(code_2fa)

        # Click submit button
        sleep(1)  # Wait for robot check
        btn_submit = self.web_driver.find_elements(
            By.CSS_SELECTOR, "#checkpointSubmitButton-actual-button"
        )
        btn_submit[0].click()

        # Do not save login info
        sleep(1)  # Wait for new page load
        btn_do_not_save_login_info = self.web_driver.find_elements(
            By.XPATH, '//*[starts-with(@id, "u_0_")]/section/section[2]/div[2]/div/div[2]/label'
        )
        if len(btn_do_not_save_login_info) > 0:
            btn_do_not_save_login_info[0].click()
        btn_continue = self.web_driver.find_elements(
            By.XPATH, '//*[@id="checkpointSubmitButton-actual-button"]'
        )
        if len(btn_continue) > 0:
            btn_continue[0].click()

        # # Skip save login info
        # sleep(1)  # Wait for new page load
        # btn_skip_save_login_info = self.web_driver.find_elements(
        #     By.XPATH, '//*[@id="root"]/table/tbody/tr/td/div/div[3]/a'
        # )
        # if len(btn_skip_save_login_info) > 0:
        #     btn_skip_save_login_info[0].click()

        print("Login success")

    def logout(self):
        """
        Logout Facebook
        """
        print("\nLogout...")
        btn_logout = self.web_driver.find_elements(By.XPATH, '//*[@id="mbasic_logout_button"]')
        if len(btn_logout) > 0:
            sleep(1)  # Wait for new page load
            btn_logout[0].click()

            btn_logout_confirm = self.web_driver.find_elements(
                By.XPATH, '//*[@id="root"]/table/tbody/tr/td/div/form[2]'
            )
            if len(btn_logout_confirm) > 0:
                sleep(1)  # Wait for new page load
                btn_logout_confirm[0].click()
                print("\nLogout success")
            else:
                print("No logout confirm button")
        else:
            print("No logout button")
            print("\nLogout fail")

    def is_login(self):
        """
        Check if the user is logged in
        """
        try:
            sleep(1)
            self.web_driver.get("https://mbasic.facebook.com/")
            element_live = self.web_driver.find_elements(By.NAME, "view_post")
            return bool(len(element_live) > 0)
        except Exception as exception:
            print("View Facebook post error")
            print(exception)
            print(traceback.format_exc())
            return False

    def set_storage(self, output_folder: str):
        """
        Set storage for scraped data
        """
        self.output_folder = output_folder
        Path(output_folder).mkdir(parents=True, exist_ok=True)

    def scrape_group(self, group_id: str, max_posts: int, media_types: list):
        """
        Scrape posts from a group
        """
        print(f"\nScrape group {group_id}...")

        # Open group site
        self.web_driver.get(f"https://mbasic.facebook.com/groups/{group_id}")

        # Scrape posts
        self.scrape_posts(max_posts, media_types)

    def scrape_page(self, page_id: str, max_posts: int, media_types: list):
        """
        Scrape posts from a page
        """
        print(f"\nScrape page {page_id}...")

        # Open page site
        self.web_driver.get(f"https://mbasic.facebook.com/{page_id}")

        # Scrape posts
        self.scrape_posts(max_posts, media_types)

    def scrape_profile(self, profile_id: str, max_posts: int, media_types: list):
        """
        Scrape posts from a profile
        """
        print(f"\nScrape profile {profile_id}...")

        # Open profile site
        self.web_driver.get(f"https://mbasic.facebook.com/{profile_id}")

        # Scrape posts
        self.scrape_posts(max_posts, media_types)

    def scrape_posts(self, max_posts: int, media_types: list):
        """Scrape posts from the current page"""


if __name__ == "__main__":
    args = get_args()
    load_dotenv(dotenv_path=args.env)
    assert Path(args.env).exists(), f'File {args.env} does not exist.'

    FB_USERNAME = os.getenv("FB_USERNAME")
    FB_PASSWORD = os.getenv("FB_PASSWORD")
    FB_KEY_2FA = os.getenv("FB_KEY_2FA")

    # Initialize Facebook Scraper
    scraper = FacebookScraper(FB_USERNAME, FB_PASSWORD, FB_KEY_2FA)

    # Set storage
    scraper.set_storage(args.output)

    # Scrape data
    if args.source == "all":
        scraper.scrape_group(args.id, args.max, args.media)
        scraper.scrape_page(args.id, args.max, args.media)
        scraper.scrape_profile(args.id, args.max, args.media)

    elif args.source == "group":
        scraper.scrape_group(args.id, args.max, args.media)

    elif args.source == "page":
        scraper.scrape_page(args.id, args.max, args.media)

    elif args.source == "profile":
        scraper.scrape_profile(args.id, args.max, args.media)

    # Logout
    scraper.logout()
