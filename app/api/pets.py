import uuid
import datetime as dt
from flask import jsonify, request, abort
from flask.views import MethodView
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from app.api import bp
from app.api.models import Pet, Store
from app.main.decorators import app_required


SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'species': {'type': 'string'},
        'breed': {'type': 'string'},
        'age': {'type': 'number'},
        'store': {'type': 'string'},
        'price': {'type': 'string'},
        'received_date': {
            'type': 'string',
            'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' # noqa
        }
    },
    'required': [
        'species',
        'breed',
        'age',
        'price',
        'received_date'
    ]
}

PETS_PER_PAGE = 10


def pet_obj(pet, store=True):
    pet_obj = {
        'id': pet.external_id,
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'age': pet.age,
        'price': str(pet.price),
        'received_date': str(pet.received_date.isoformat()[0:19]) + 'Z',
        'links': [
            {
                'rel': 'self',
                'href': '/api/pets/' + pet.external_id
            }
        ]
    }
    if store:
        from app.api.store import store_obj
        pet_obj['store'] = store_obj(pet.store)

    return pet_obj


def pets_obj(pets, store=True):
    pets_obj = []
    for pet in pets.items:
        pets_obj.append(pet_obj(pet, store=store))
    return pets_obj


class PetApi(MethodView):

    decorators = [app_required]

    def __init__(self):
        if request.method not in ['GET', 'DELETE'] and not request.json:
            abort(400)

    def get(self, pet_id):
        if pet_id:
            pet = Pet.objects.filter(
                external_id=pet_id,
                live=True
            ).first()
            if pet:
                response = {
                    'result': 'ok',
                    'pet': pet_obj(pet)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            pets = Pet.objects.filter(live=True)
            page = int(request.args.get('page', 1))
            pets = pets.paginate(page=page, per_page=PETS_PER_PAGE)
            response = {
                'result': 'ok',
                'links': [
                    {
                        'rel': 'self',
                        'href': f'/api/pets/?page={page}'
                    }
                ],
                'pets': pets_obj(pets)
            }
            if pets.has_prev:
                response['links'].append({
                        'rel': 'previous',
                        'href': f'/api/pets/?page={pets.prev_num}'
                    })
            if pets.has_next:
                response['links'].append({
                    'rel': 'next',
                    'href': f'/api/pets/?page={pets.next_num}'
                })
            return jsonify(response), 200

    def post(self):
        pet_json = request.json
        error = best_match(Draft4Validator(SCHEMA).iter_errors(pet_json))
        if error:
            return jsonify({
                'error': error.message
            }), 400
        store = Store.objects.filter(external_id=pet_json.get('store')).first()
        if not store:
            error = 'STORE_NOT_FOUND'
            return jsonify({
                'error': error
            }), 400
        try:
            received_date = dt.datetime.strptime(
                pet_json.get('received_date'),
                '%Y-%m-%dT%H:%M:%SZ'
            )
        except: # noqa
            return jsonify({'error': 'INVALID_DATE'}), 400

        pet = Pet(
            external_id=str(uuid.uuid4()),
            name=pet_json.get('name'),
            species=pet_json.get('species'),
            breed=pet_json.get('breed'),
            age=pet_json.get('age'),
            store=store,
            price=pet_json.get('price'),
            received_date=received_date
        )
        pet.save()
        response = {
            'result': 'ok',
            'pet': pet_obj(pet)
        }
        return jsonify(response), 201

    def put(self, pet_id):
        pet = Pet.objects.filter(external_id=pet_id).first()
        if not pet:
            return jsonify({}), 404
        pet_json = request.json
        error = best_match(Draft4Validator(SCHEMA).iter_errors(pet_json))
        if error:
            return jsonify({
                'error': error.message
            }), 400
        store = Store.objects.filter(
            external_id=pet_json.get('store')
        ).first()
        if not store:
            error = {
                'code': 'STORE_NOT_FOUND'
            }
            return jsonify({'error': error}), 400
        try:
            received_date = dt.datetime.strptime(
                pet_json.get('received_date'),
                '%Y-%m-%dT%H:%M:%SZ'
            )
        except: # noqa
            return jsonify({'error': 'INVALID_DATE'}), 400

        pet.name = pet_json.get('name')
        pet.species = pet_json.get('species')
        pet.breed = pet_json.get('breed')
        pet.age = pet_json.get('age')
        pet.store = store
        pet.price = pet_json.get('price')
        pet.received_date = received_date
        pet.save()
        response = {
            'result': 'ok',
            'pet': pet_obj(pet)
        }
        return jsonify(response), 200

    def delete(self, pet_id):
        pet = Pet.objects.filter(external_id=pet_id).first()
        if not pet:
            return jsonify({}), 404
        pet.live = False
        pet.save()
        return jsonify({}), 204


pet_view = PetApi.as_view('pet_api')
bp.add_url_rule(
    '/pets/',
    defaults={'pet_id': None},
    view_func=pet_view,
    methods=['GET', ]
    )
bp.add_url_rule('/pets/', view_func=pet_view, methods=['POST'])

bp.add_url_rule(
    '/pets/<pet_id>',
    view_func=pet_view,
    methods=['GET', 'PUT', 'DELETE', ]
)
