
from flask import jsonify, request, abort
from flask.views import MethodView
from app.api import bp
from app.api.store import store_obj
from app.api.models import Pet
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
            'pattern': '^[0-9]{4}-[0-9]{2)-[0-9{2}T[0-9]{2}:[0-9]{2}-[0-9]{2}Z$' # noqa
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
    return {
        'id': pet.external_id,
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'age': pet.age,
        'store': store_obj(pet.store),
        'price': pet.price,
        'received_date': str(pet.received_date.isoformat()[0:19]) + 'Z',
        'links': [
            {
                'rel': 'self',
                'href': '/api/pets/' + pet.external_id
            }
        ]
    }


def pets_obj(pets, store=True):
    pets_obj = []
    for pet in pets.items:
        pets_obj.append(pet_obj(pet))
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
        pass

    def put(self, pet_id):
        pass

    def delete(self, pet_id):
        pass


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
