from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import time

import secrets
import constants

from telethon import TelegramClient


def get_source_html(url):
    # Signing in in Telegram
    client = TelegramClient('anon', secrets.APP_API_ID, secrets.API_HASH)

    # Setting option for WebDriver
    chromeoptions = Options()

    # headless = False - to open browser (for debugging)
    # headless = True - not to open browser
    chromeoptions.headless = True

    # Create driver
    driver = webdriver.Chrome(
        executable_path=constants.CHROMEDRIVER_PATH, options=chromeoptions
    )
    driver.maximize_window()

    try:
        iterator = 1
        while True:
            driver.get(url=constants.URL)
            time.sleep(60)

            print(f"Attempt №{iterator}")

            # Managing cookies
            if iterator == 1:
                driver.find_element(by=By.CLASS_NAME, value=constants.COOKIE_BUTTON_CLASS).click()

            # Clicking "READ MORE" button
            driver.find_element(by=By.XPATH, value=constants.READMORE_BUTTON).click()

            # Checking if it is still unavailable
            driver.find_element(by=By.XPATH, value=constants.ROOM_EURO_XPATH)
            driver.find_element(by=By.XPATH, value=constants.ROOM_CZK_XPATH)

            # Reporting to Telegram
            async def sending_messages():
                await client.send_message(constants.TELEGRAM_USERNAME, f"Attempt №{iterator}. Nothing has been found")
            with client:
                if iterator % 60.0 == 0:
                    client.loop.run_until_complete(sending_messages())

            # Iterating in order to avoid cookies error and show number of attempts
            iterator += 1

    # Available Room Notification
    except NoSuchElementException as ex:
        print(ex)

        # Reporting to Telegram
        async def sending_availability():
            await client.send_message(constants.TELEGRAM_USERNAME, "Apartments have been found!")
            await client.send_message(constants.TELEGRAM_USERNAME, constants.URL)
        with client:
            client.loop.run_until_complete(sending_availability())

    # Handling other errors
    except Exception as ex:
        print(ex)

        async def sending_errors():
            await client.send_message(constants.TELEGRAM_USERNAME, "Something went wrong.")
            await client.send_message(constants.TELEGRAM_USERNAME, str(ex))
        with client:
            client.loop.run_until_complete(sending_errors())

    finally:
        async def sending_termination():
            await client.send_message(constants.TELEGRAM_USERNAME, "The script has been terminated.")
        with client:
            client.loop.run_until_complete(sending_termination())
        driver.close()
        driver.quit()


def main():
    get_source_html(url=constants.URL)


if __name__ == '__main__':
    main()
