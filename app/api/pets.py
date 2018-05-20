from flask import jsonify, request, abort
from flask.views import MethodView
from app.api import bp


class PetView(MethodView):

    pets = [
        {
            'id': 1,
            'name': 'Mac',
            'links': [
                {
                    'rel': 'self',
                    'href': '/api/pets/1'
                }
            ]
        },
        {
            'id': 2,
            'name': 'Leo',
            'links': [
                {
                    'rel': 'self',
                    'href': '/api/pets/2'
                }
            ]
        },
        {
            'id': 3,
            'name': 'Brownie',
            'links': [
                {
                    'rel': 'self',
                    'href': '/api/pets/3'
                }
            ]
        },
    ]

    def get(self, pet_id):
        if pet_id:
            return jsonify({'pet': self.pets[pet_id - 1]})
        else:
            return jsonify({'pets': self.pets})

    def post(self):
        if not request.json or 'name' not in request.json:
            abort(400)
        pet = {
            'id': len(self.pets) + 1,
            'name': request.json['name'],
            'links': [
                {
                    'rel': 'self',
                    'href': '/api/pets/' + str(len(self.pets) + 1)
                }
            ]
        }
        self.pets.append(pet)
        return jsonify({'pet': pet}), 201

    def put(self, pet_id):
        if not request.json or 'name' not in request.json:
            abort(400)
        pet = self.pets[pet_id - 1]
        pet['name'] = request.json['name']
        return jsonify({'pet': pet}), 200

    def delete(self, pet_id):
        del(self.pets[pet_id - 1])
        return jsonify({}), 204


pet_view = PetView.as_view('pet_api')
bp.add_url_rule(
    '/pets/',
    defaults={'pet_id': None},
    view_func=pet_view,
    methods=['GET', ]
    )
bp.add_url_rule('/pets/', view_func=pet_view, methods=['POST'])

bp.add_url_rule(
    '/pets/<int:pet_id>',
    view_func=pet_view,
    methods=['GET', 'PUT', 'DELETE', ]
)
