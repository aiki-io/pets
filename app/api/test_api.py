import json
import pytest
from mongoengine.connection import _get_db
from app import create_app
from config import TestConfig


class TestApp:

    @pytest.fixture(scope='function')
    def fixture(self):
        app = create_app(TestConfig)
        app_context = app.app_context()
        app_context.push()
        db = _get_db()
        client = app.test_client()
        payload = json.dumps({
                    'app_id': 'pet_client',
                    'app_secret': 'secret'
                })
        yield (client, payload)
        db.client.drop_database(db)
        app_context.pop()

    def test_create_app(self, fixture):
        client, payload = fixture
        request = client.post(
            '/api/apps/',
            data=payload,
            content_type='application/json'
        )
        assert request.status_code == 200
