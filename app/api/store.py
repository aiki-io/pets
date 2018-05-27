import json
import uuid
from flask import jsonify, request, abort, render_template
from flask.views import MethodView
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from app.api import bp
from app.main.decorators import app_required
from app.api.models import Store

SCHEMA = {
    'type': 'object',
    'properties': {
        'neighborhood': {'type': 'string'},
        'street_adress': {'type': 'string'},
        'city': {'type': 'string'},
        'state': {'type': 'string', 'pattern': '^[A-Z]{2}$'},
        'phone': {'type': 'string', 'pattern': '^[0-9]{3}-[0-9]{3}-[0-9]{4}$'},
    },
    'required': [
        'neighborhood',
        'street_adress',
        'city', 'state',
        'zip',
        'phone'
    ]
}


def store_obj(doc):
    return {
        'id': doc.external_id,
        'neighborhood': doc.neighborhood,
        'street_adress': doc.street_adress,
        'city': doc.city,
        'state': doc.state,
        'zip': doc.zip,
        'phone': doc.phone,
        'links': [
            {
                'rel': 'self',
                'href': '/api/stores/' + doc.external_id
            }

        ]
    }


def stores_obj(stores):
    stores = []
    return stores


class StoreApi(MethodView):
    decorators = [app_required]

    def __init__(self):
        if request.method != 'GET'and not request.json:
            abort(400)

    def get(self, store_id):
        if store_id:
            store = Store.objects.filter(external_id=store_id).first()
            if store:
                response = {
                    'result': 'ok',
                    'store': store_obj(store)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            stores = Store.objects.all()
            response = {
                'result': 'ok',
                'stores': stores_obj(stores)
            }
            return jsonify(response), 200

    def post(self):
        store_json = request.json
        error = best_match(Draft4Validator(SCHEMA).iter_errors(store_json))
        if error:
            return jsonify(
                {'error': error.message}

            ), 400
        else:
            store = Store(
                external_id=str(uuid.uuid4()),
                neighborhood=store_json.get('neighborhood'),
                street_adress=store_json.get('street_adress'),
                city=store_json.get('city'),
                state=store_json.get('state'),
                zip=store_json.get('zip'),
                phone=store_json.get('phone')
            )
            store.save()
            response = {
                'result': 'ok',
                'store': store_obj(store)
            }
            return jsonify(response), 201

    def put(self, store_id):
        pass

    def delete(self, store_id):
        pass


store_view = StoreApi.as_view('store_api')

bp.add_url_rule(
    '/stores/',
    defaults={'store_id': None},
    view_func=store_view,
    methods=['GET', ]
    )
bp.add_url_rule('/stores/',
                view_func=store_view,
                methods=['POST', ]
                )
bp.add_url_rule('/stores/<string:store_id>',
                view_func=store_view,
                methods=['GET', 'PUT', 'DELETE',]
                )
