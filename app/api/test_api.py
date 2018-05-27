import json
import datetime as dt
import pytest
from mongoengine.connection import _get_db
from app import create_app
from config import TestConfig
from app.models import Access


class TestApp:

    @pytest.fixture(scope='function')
    def client(self):
        app = create_app(TestConfig)
        app_context = app.app_context()
        app_context.push()
        db = _get_db()
        client = app.test_client()

        yield client
        db.client.drop_database(db)
        app_context.pop()

    def help_create_app(self, client):
            payload = json.dumps({
                    'app_id': 'pet_client',
                    'app_secret': 'secret'
                })
            return client.post(
                '/api/apps/',
                data=payload,
                content_type='application/json'
            )

    def help_create_token(self, client):
            payload = json.dumps({
                 'app_id': 'pet_client',
                 'app_secret': 'secret'
             })
            rq = client.post(
                '/api/apps/tokens/',
                data=payload,
                content_type='application/json'
            )
            assert rq.status_code == 200
            return json.loads(rq.data.decode('utf-8'))['token']

    def test_create_app(self, client):
        rq = self.help_create_app(client)
        assert rq.status_code == 200

    def test_create_app_missing_secret(self, client):
        payload = json.dumps({
            'app_id': 'pet_client',
        })
        rq = client.post(
            '/api/apps/',
            data=payload,
            content_type='application/json'
        )
        assert 'MISSING_APP_ID_OR_APP_SECRET' in str(rq.data)

    def test_create_app_double_registration(self, client):
        self.help_create_app(client)
        rq = self.help_create_app(client)
        assert 'APP_ID_ALREADY_EXISTS' in str(rq.data)

    def test_create_token(self, client):
        self.help_create_app(client)
        token = self.help_create_token(client)
        assert token

    def test_create_token_missing_secret(self, client):
            self.help_create_app(client)
            payload = json.dumps({
                 'app_id': 'pet_client',
             })
            rq = client.post(
                '/api/apps/tokens/',
                data=payload,
                content_type='application/json'
            )
            assert 'MISSING_APP_ID_OR_APP_SECRET' in str(rq.data)

    def test_create_token_wrong_secret(self, client):
            self.help_create_app(client)
            payload = json.dumps({
                'app_id': 'pet_client',
                'app_secret': 'bogus'
                })
            rq = client.post(
                '/api/apps/tokens/',
                data=payload,
                content_type='application/json'
            )
            assert 'INVALID_CREDENTIALS' in str(rq.data)

    def test_token_works(self, client):
        self.help_create_app(client)
        token = self.help_create_token(client)
        rq = client.get(
            '/api/pets/',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            },
            content_type='application/json'
        )
        assert rq.status_code == 200

    def test_wrong_token(self, client):
        self.help_create_app(client)
        self.help_create_token(client)

        rq = client.get(
            '/api/pets/',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': 'bogus-token'
            },
            content_type='application/json'
        )
        assert rq.status_code == 403

    def test_expired_token(self, client):
        self.help_create_app(client)
        token = self.help_create_token(client)
        now = dt.datetime.utcnow().replace(second=0, microsecond=0)
        expires = now + dt.timedelta(days=-31)
        access = Access.objects.first()
        access.expires = expires
        access.save()

        rq = client.get(
            '/api/pets/',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token
            },
            content_type='application/json'
        )
        assert 'TOKEN_EXPIRED' in str(rq.data)
