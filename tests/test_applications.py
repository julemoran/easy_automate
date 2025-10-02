import unittest
import json
from packages.easy_automate import create_app
from packages.easy_automate import db
from packages.easy_automate.models import Application
from packages.easy_automate.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ApplicationAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_application(self):
        # Test creating a new application
        response = self.client.post('/applications',
                                    data=json.dumps({'name': 'Test App'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test App')

    def test_get_applications(self):
        # Test getting all applications
        app = Application(name='Test App')
        db.session.add(app)
        db.session.commit()

        response = self.client.get('/applications')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test App')

    def test_get_application(self):
        # Test getting a single application
        app = Application(name='Test App')
        db.session.add(app)
        db.session.commit()

        response = self.client.get(f'/applications/{app.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test App')

    def test_update_application(self):
        # Test updating an application
        app = Application(name='Test App')
        db.session.add(app)
        db.session.commit()

        response = self.client.put(f'/applications/{app.id}',
                                   data=json.dumps({'name': 'Updated App'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated App')

    def test_delete_application(self):
        # Test deleting an application
        app = Application(name='Test App')
        db.session.add(app)
        db.session.commit()

        response = self.client.delete(f'/applications/{app.id}')
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(Application.query.get(app.id))

if __name__ == '__main__':
    unittest.main()