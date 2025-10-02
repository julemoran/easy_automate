import uuid
from selenium import webdriver

class BrowserManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session_id = str(uuid.uuid4())
        options = webdriver.ChromeOptions()
        # The following arguments are still useful for remote execution
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=options
        )
        self.sessions[session_id] = driver
        return session_id

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def close_session(self, session_id):
        driver = self.sessions.pop(session_id, None)
        if driver:
            driver.quit()

browser_manager = BrowserManager()