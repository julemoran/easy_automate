import unittest
import json
from src import create_app
from src.browser_manager import browser_manager
from src.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class BrowserAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up any stray sessions
        for session_id in list(browser_manager.sessions.keys()):
            browser_manager.close_session(session_id)
        self.app_context.pop()

    @unittest.skip("Skipping browser tests due to environment issues.")
    def test_open_and_close_session(self):
        # Test opening a new session
        response = self.client.post('/browser/open',
                                    data=json.dumps({'timeout': 30}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('session_id', data)
        session_id = data['session_id']
        self.assertIn(session_id, browser_manager.sessions)

        # Test closing the session
        response = self.client.post(f'/browser/{session_id}/close')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(session_id, browser_manager.sessions)

    @unittest.skip("Skipping browser tests due to environment issues.")
    def test_take_screenshot(self):
        # Test taking a screenshot
        response = self.client.post('/browser/open')
        session_id = json.loads(response.data)['session_id']

        response = self.client.post(f'/browser/{session_id}/screenshot')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('screenshot', data)

        # Clean up
        self.client.post(f'/browser/{session_id}/close')

    @unittest.skip("Skipping browser tests due to environment issues.")
    def test_get_dom(self):
        # Test getting the DOM
        response = self.client.post('/browser/open')
        session_id = json.loads(response.data)['session_id']

        response = self.client.get(f'/browser/{session_id}/dom')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dom', data)

        # Clean up
        self.client.post(f'/browser/{session_id}/close')

if __name__ == '__main__':
    unittest.main()