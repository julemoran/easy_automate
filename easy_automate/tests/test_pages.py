import unittest
import json
from packages.easy_automate import create_app
from packages.easy_automate import db
from packages.easy_automate.models import Application, Page
from packages.easy_automate.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class PageAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a dummy application for page association
        self.app_instance = Application(name='Test App')
        db.session.add(self.app_instance)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_page(self):
        # Test creating a new page
        page_data = {
            'name': 'Home Page',
            'application_id': self.app_instance.id,
            'identifying_selectors': [{'alias': 'logo', 'xpath': '//img[@alt="logo"]'}],
            'can_be_navigated_to': True,
            'url': 'http://example.com'
        }
        response = self.client.post('/pages',
                                    data=json.dumps(page_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Home Page')
        self.assertEqual(len(data['identifying_selectors']), 1)

    def test_get_pages(self):
        # Test getting all pages
        page = Page(
            name='Home Page',
            application_id=self.app_instance.id,
            identifying_selectors=[{'alias': 'logo', 'xpath': '//img[@alt="logo"]'}]
        )
        db.session.add(page)
        db.session.commit()

        response = self.client.get('/pages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Home Page')

    def test_get_page(self):
        # Test getting a single page
        page = Page(
            name='Home Page',
            application_id=self.app_instance.id,
            identifying_selectors=[{'alias': 'logo', 'xpath': '//img[@alt="logo"]'}]
        )
        db.session.add(page)
        db.session.commit()

        response = self.client.get(f'/pages/{page.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Home Page')

    def test_update_page(self):
        # Test updating a page
        page = Page(
            name='Home Page',
            application_id=self.app_instance.id,
            identifying_selectors=[{'alias': 'logo', 'xpath': '//img[@alt="logo"]'}]
        )
        db.session.add(page)
        db.session.commit()

        update_data = {'name': 'Updated Home Page'}
        response = self.client.put(f'/pages/{page.id}',
                                   data=json.dumps(update_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Home Page')

    def test_delete_page(self):
        # Test deleting a page
        page = Page(
            name='Home Page',
            application_id=self.app_instance.id,
            identifying_selectors=[{'alias': 'logo', 'xpath': '//img[@alt="logo"]'}]
        )
        db.session.add(page)
        db.session.commit()

        response = self.client.delete(f'/pages/{page.id}')
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(Page.query.get(page.id))

if __name__ == '__main__':
    unittest.main()