from flask import jsonify
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


bp.add_url_rule('/pets/', view_func=PetView.as_view('pets'))
