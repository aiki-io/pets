import json
import pytest
from mongoengine.connection import _get_db
from app import create_app
from config import TestConfig
from app.api.models import Pet
from app.api.test_apps import help_create_app, help_create_token
from app.api.test_stores import help_create_store, help_import_test_data


def help_create_pet(client, store, token):
    raw_payload = {
        'name': 'Mac',
        'species': 'dog',
        'breed': 'ShiTzu',
        'age': 11,
        'store': store,
        'price': '855.22',
        'received_date': '2018-02-28T12:00:00Z'
    }
    payload = json.dumps(raw_payload)
    rv = client.post('/api/pets/',
                     data=payload,
                     content_type='application/json',
                     headers={
                         'X-APP-ID': 'pet_client',
                         'X-APP-TOKEN': token,
                     })
    assert rv.status_code == 201
    pet = json.loads(rv.data.decode('utf-8'))['pet']['id']
    return pet


class TestPets:

    @pytest.fixture
    def client(self):
        app = create_app(TestConfig)
        db = _get_db()
        app_context = app.app_context()
        app_context.push()
        client = app.test_client()
        yield client
        app_context.pop()
        db.client.drop_database(db)

    def test_pet_create(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        pet = help_create_pet(client, store, token)
        assert pet

    def test_pet_read(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        pet = help_create_pet(client, store, token)
        rv = client.get(
            '/api/pets/' + pet,
            content_type='application/json',
            headers={
                 'X-APP-ID': 'pet_client',
                 'X-APP-TOKEN': token,
            })
        assert rv.status_code == 200
        assert json.loads(rv.data.decode('utf-8'))['pet']['name'] == 'Mac'

    def test_pet_update(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        pet = help_create_pet(client, store, token)
        raw_payload = {
            'name': 'Lala',
            'species': 'dog',
            'breed': 'ShiTzu',
            'age': 11,
            'store': store,
            'price': '855.22',
            'received_date': '2018-02-28T12:00:00Z'
        }
        rv = client.put(
            '/api/pets/' + pet,
            data=json.dumps(raw_payload),
            content_type='application/json',
            headers={
                 'X-APP-ID': 'pet_client',
                 'X-APP-TOKEN': token,
            })
        assert rv.status_code == 200
        assert json.loads(rv.data.decode('utf-8'))['pet']['name'] == 'Lala'

    def test_pet_delete(self, client):
        help_create_app(client)
        token = help_create_token(client)
        store = help_create_store(client, token)
        pet = help_create_pet(client, store, token)
        rv = client.delete(
            '/api/pets/' + pet,
            content_type='application/json',
            headers={
                'X-APP-ID': 'pet_client',
                'X-APP-TOKEN': token,
                })
        assert rv.status_code == 204
        assert Pet.objects.filter(live=False).count() == 1

    def test_pet_pagination(self, client):
        help_import_test_data('store', 'data/stores.json')
        help_import_test_data('pet', 'data/pets.json')
        help_create_app(client)
        token = help_create_token(client)
        rv = client.get(
            '/api/pets/',
            content_type='application/json',
            headers={
                'X-APP-ID': 'pet_client',
                            'X-APP-TOKEN': token,
            }
        )
        assert 'next' in str(rv.data)
        rv = client.get(
                    '/api/pets/?page=2',
                    content_type='application/json',
                    headers={
                        'X-APP-ID': 'pet_client',
                                    'X-APP-TOKEN': token,
                    }
                )
        assert 'previous' in str(rv.data)
