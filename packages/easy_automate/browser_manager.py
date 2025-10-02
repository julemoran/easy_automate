import os
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

class BrowserManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, timeout=None):
        session_id = str(uuid.uuid4())
        options = webdriver.ChromeOptions()

        selenium_mode = os.environ.get('SELENIUM_MODE', 'remote')

        if selenium_mode == 'local':
            # When running locally, we can choose to see the browser
            from webdriver_manager.chrome import ChromeDriverManager
            interactive_mode = os.environ.get('INTERACTIVE_MODE', 'False').lower() in ('true', '1', 't')
            if not interactive_mode:
                options.add_argument('--headless=new')

            # Common options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        else:
            # Remote execution for Docker setup
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            selenium_hub_url = os.environ.get('SELENIUM_HUB_URL', 'http://selenium:4444/wd/hub')
            driver = webdriver.Remote(
                command_executor=selenium_hub_url,
                options=options
            )

        # Set the command executor timeout for both local and remote sessions.
        # A value of None should make it wait indefinitely.
        if timeout is not None:
            driver.command_executor.set_timeout(timeout)

        self.sessions[session_id] = driver
        return session_id

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def close_session(self, session_id):
        driver = self.sessions.pop(session_id, None)
        if driver:
            driver.quit()

browser_manager = BrowserManager()