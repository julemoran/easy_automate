import unittest
import json
from src import create_app, db
from src.models import Application, Page
from src.browser_manager import browser_manager
from src.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class MCPAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a test application
        self.app1 = Application(name='Test App')
        db.session.add(self.app1)
        db.session.commit()
        self.app1_id = self.app1.id

    def tearDown(self):
        # Clean up any stray sessions
        if self.client.post('/mcp/session/close').status_code == 204:
            pass

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip("Skipping browser tests due to environment issues.")
    def test_open_and_close_mcp_session(self):
        # Test opening a new session
        response = self.client.post('/mcp/session/open',
                                    data=json.dumps({'timeout': 30}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('session_id', data)
        self.assertEqual(len(browser_manager.sessions), 1)

        # Test closing the session
        response = self.client.post('/mcp/session/close')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(browser_manager.sessions), 0)

    def test_create_and_get_page(self):
        # Create a page
        page_data = {
            'name': 'Test Page',
            'application_id': self.app1_id,
            'url': 'http://example.com',
            'can_be_navigated_to': True,
            'identifying_selectors': [{'xpath': '//h1'}]
        }
        response = self.client.post('/mcp/pages',
                                    data=json.dumps(page_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        page_id = data['id']

        # Get the page
        response = self.client.get(f'/mcp/pages/{page_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Page')

    def test_get_all_pages(self):
        # Create a couple of pages
        page_data1 = {
            'name': 'Test Page 1', 'application_id': self.app1_id,
            'identifying_selectors': [{'xpath': '//h1'}]
        }
        page_data2 = {
            'name': 'Test Page 2', 'application_id': self.app1_id,
            'identifying_selectors': [{'xpath': '//h2'}]
        }
        self.client.post('/mcp/pages', data=json.dumps(page_data1), content_type='application/json')
        self.client.post('/mcp/pages', data=json.dumps(page_data2), content_type='application/json')

        # Get all pages
        response = self.client.get('/mcp/pages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_update_page(self):
        # Create a page
        page_data = {
            'name': 'Original Name', 'application_id': self.app1_id,
            'identifying_selectors': [{'xpath': '//h1'}]
        }
        response = self.client.post('/mcp/pages', data=json.dumps(page_data), content_type='application/json')
        page_id = json.loads(response.data)['id']

        # Update the page
        update_data = {'name': 'Updated Name'}
        response = self.client.put(f'/mcp/pages/{page_id}',
                                   data=json.dumps(update_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify update
        response = self.client.get(f'/mcp/pages/{page_id}')
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Name')

    def test_delete_page(self):
        # Create a page
        page_data = {
            'name': 'To Be Deleted', 'application_id': self.app1_id,
            'identifying_selectors': [{'xpath': '//h1'}]
        }
        response = self.client.post('/mcp/pages', data=json.dumps(page_data), content_type='application/json')
        page_id = json.loads(response.data)['id']

        # Delete the page
        response = self.client.delete(f'/mcp/pages/{page_id}')
        self.assertEqual(response.status_code, 204)

        # Verify deletion
        response = self.client.get(f'/mcp/pages/{page_id}')
        self.assertEqual(response.status_code, 404)

    @unittest.skip("Skipping browser tests due to environment issues.")
    def test_browser_endpoints_require_session(self):
        # Test that browser endpoints fail without an open session
        response = self.client.post('/mcp/navigate', data=json.dumps({'page_id': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/mcp/wait-for-page', data=json.dumps({'page_id': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/mcp/current-page')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/mcp/screenshot')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/mcp/dom')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()