import unittest
import os
from src.browser_manager import browser_manager
from flask import Flask, send_from_directory
import threading

TEST_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'test_pages')

def run_test_server():
    app = Flask(__name__)

    @app.route('/<path:filename>')
    def serve_file(filename):
        return send_from_directory(TEST_STATIC_DIR, filename)

    app.run(port=5001, debug=False, use_reloader=False)

server_thread = None

class BrowserManagerTestCase(unittest.TestCase):
    def test_get_current_page_logic(self):
        from src.browser_actions import BrowserActions
        actions = BrowserActions(self.driver)
        # Define test pages and selectors
        test_pages = [
            {
                'id': 'dummy1',
                'application_id': 'test_app',
                'identifying_selectors': [
                    {'alias': 'page-identifier-1', 'xpath': "//*[@id='page-identifier-1']", 'visible': True},
                    {'alias': 'page-identifier-2', 'xpath': "//*[@id='page-identifier-2']", 'visible': False}
                ]
            },
            {
                'id': 'dummy2',
                'application_id': 'test_app',
                'identifying_selectors': [
                    {'alias': 'page-identifier-2', 'xpath': "//*[@id='page-identifier-2']", 'visible': True},
                    {'alias': 'page-identifier-1', 'xpath': "//*[@id='page-identifier-1']", 'visible': False},
                    {'alias': 'page-identifier-3', 'xpath': "//*[@id='page-identifier-3']"}  # visible missing
                ]
            },
            {
                'id': 'dummy3',
                'application_id': 'test_app',
                'identifying_selectors': [
                    {'alias': 'page-identifier-3', 'xpath': "//*[@id='page-identifier-3']", 'visible': True},
                    {'alias': 'page-identifier-1', 'xpath': "//*[@id='page-identifier-1']", 'visible': False},
                    {'alias': 'page-identifier-2', 'xpath': "//*[@id='page-identifier-2']", 'visible': False}
                ]
            }
        ]
        applications_pages = {'test_app': {
            'dummy1': test_pages[0]['identifying_selectors'],
            'dummy2': test_pages[1]['identifying_selectors'],
            'dummy3': test_pages[2]['identifying_selectors'],
        }}
        # Test dummy1.html
        self.driver.get('http://localhost:5001/dummy1.html')
        pages = actions.get_current_pages(test_pages, applications_pages)
        self.assertIsInstance(pages, list)
        self.assertTrue(any(p['id'] == 'dummy1' for p in pages))
        # Test dummy2.html
        self.driver.get('http://localhost:5001/dummy2.html')
        pages = actions.get_current_pages(test_pages, applications_pages)
        self.assertIsInstance(pages, list)
        self.assertTrue(any(p['id'] == 'dummy2' for p in pages))
        # Test dummy3.html
        self.driver.get('http://localhost:5001/dummy3.html')
        pages = actions.get_current_pages(test_pages, applications_pages)
        self.assertIsInstance(pages, list)
        self.assertTrue(any(p['id'] == 'dummy3' for p in pages))
        # Test with no matching page (remove visible element)
        self.driver.get('http://localhost:5001/dummy1.html')
        # Remove element via JS
        self.driver.execute_script("document.getElementById('page-identifier-1').style.display='none';")
        pages = actions.get_current_pages(test_pages, applications_pages)
        self.assertIsInstance(pages, list)
        self.assertEqual(len(pages), 0)
    @classmethod
    def setUpClass(cls):
        os.environ['SELENIUM_MODE'] = 'local'
        os.environ['INTERACTIVE_MODE'] = 'True'
        global server_thread
        if server_thread is None:
            server_thread = threading.Thread(target=run_test_server, daemon=True)
            server_thread.start()
        cls.session_id = browser_manager.create_session()
        cls.driver = browser_manager.get_session(cls.session_id)

    @classmethod
    def tearDownClass(cls):
        browser_manager.close_session(cls.session_id)

    def test_element_presence(self):
        from src.browser_actions import BrowserActions
        self.driver.get('http://localhost:5001/test.html')
        actions = BrowserActions(self.driver)
        selectors = ["//*[@id='test-element']"]
        result = actions.check_selectors(selectors)
        self.assertIn(selectors[0], result)
        self.assertTrue(result[selectors[0]]['existing'])
    def test_create_and_close_session(self):
        # Use the class session for testing close and re-create
        browser_manager.close_session(self.session_id)
        self.assertNotIn(self.session_id, browser_manager.sessions)
        # Re-create session for further tests
        BrowserManagerTestCase.session_id = browser_manager.create_session()
        BrowserManagerTestCase.driver = browser_manager.get_session(BrowserManagerTestCase.session_id)

    def test_take_screenshot(self):
        self.driver.get('http://localhost:5001/test.html')
        screenshot = self.driver.get_screenshot_as_png()
        self.assertIsInstance(screenshot, bytes)
        self.assertGreater(len(screenshot), 0)

    def test_get_dom(self):
        self.driver.get('http://localhost:5001/test.html')
        dom = self.driver.page_source
        self.assertIsInstance(dom, str)
        self.assertIn('<html', dom)
    def test_selector_visibility(self):
        from src.browser_actions import BrowserActions
        self.driver.get('http://localhost:5001/test.html')
        actions = BrowserActions(self.driver)
        selectors = [
            "//*[@id='test-element']",
            "//*[@id='invisible-element']",
            "//*[@id='does-not-exist']"
        ]
        result = actions.check_selectors(selectors)
        self.assertIn(selectors[0], result)
        self.assertTrue(result[selectors[0]]['existing'])
        self.assertTrue(result[selectors[0]]['visible'])
        self.assertIn(selectors[1], result)
        self.assertTrue(result[selectors[1]]['existing'])
        self.assertFalse(result[selectors[1]]['visible'])
        self.assertIn(selectors[2], result)
        self.assertFalse(result[selectors[2]]['existing'])

if __name__ == '__main__':
    unittest.main()