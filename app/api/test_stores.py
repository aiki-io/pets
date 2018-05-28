import json
import subprocess
import pytest
from mongoengine.connection import _get_db
from app import create_app
from app.api.test_apps import help_create_app, help_create_token
from app.api.models import Store
from config import TestConfig


def help_create_store(client, token):
    raw_payload = {
        "neighborhood": "Shannonwood",
        "street_adress": "1708 211th Pl NE",
        "city": "Sammamish",
        "state": "WA",
        "zip": "98074",
        "phone": "425-894-1012"
    }
    payload = json.dumps(raw_payload)
    rq = client.post(
        '/api/stores/',
        data=payload,
        content_type='application/json',
        headers={
            'X-APP-ID': 'pet_client',
            'X-APP-TOKEN': token,
        }
    )
    assert rq.status_code == 201
    store = json.loads(rq.data.decode('utf-8')).get('store')['id']
    return store


def help_import_test_data(collection, datafile):
    host = TestConfig.MONGODB_HOST
    db = TestConfig.MONGODB_DB
    command = f'mongoimport -h {host} -d {db} -c {collection} < {datafile}'
    subprocess.call(command, shell=True)


class TestStores:
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

    def test_store_create(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        assert store

    def test_store_read(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        rq = client.get(
            '/api/stores/' + store,
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            }
        )
        assert json.loads(
            rq.data.decode('utf-8')
        )['store']['phone'] == '425-894-1012'

    def test_update(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        raw_payload = {
                "neighborhood": "Shannonwood",
                "street_adress": "1708 211th Pl NE",
                "city": "Sammamish",
                "state": "CA",
                "zip": "98074",
                "phone": "425-894-1012"
            }
        rq = client.put(
            '/api/stores/' + store,
            data=json.dumps(raw_payload),
            content_type='application/json',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            }
        )
        assert rq.status_code == 200
        assert json.loads(
            rq.data.decode('utf-8')
            )['store']['state'] == 'CA'

    def test_delete(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        rq = client.delete(
            '/api/stores/' + store,
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            }
        )
        assert rq.status_code == 204
        assert Store.objects.filter(live=False).count() == 1

    def test_pagination(self, client):
        help_import_test_data('store', 'data/stores.json')
        help_create_app(client)
        token = help_create_token(client)
        rq = client.get(
            '/api/stores/',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            }
        )
        assert 'next' in str(rq.data)
        rq = client.get(
            '/api/stores/?page=2',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
            }
        )
        assert 'previous' in str(rq.data)
        assert 'next' in str(rq.data)
