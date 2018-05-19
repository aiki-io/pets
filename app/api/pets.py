from flask import jsonify, request, abort
from flask.views import MethodView
from app.api import bp


class PetView(MethodView):

    pets = [
        dict(id=1, name='Mac'),
        dict(id=2, name='Leo'),
        dict(id=3, name='Brownie'),
    ]

    def get(self):
        return jsonify({'pets': self.pets})

    def post(self):
        if not request.json or 'name' not in request.json:
            abort(400)
        pet = {
            'id': len(self.pets) + 1,
            'name': request.json['name']
        }
        self.pets.append(pet)
        return jsonify({'pet': pet}), 201


bp.add_url_rule('/pets/', view_func=PetView.as_view('pets'))
