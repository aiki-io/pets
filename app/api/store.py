import uuid
from flask import jsonify, request, abort
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

STORES_PER_PAGE = 10


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
    stores_obj = []
    for store in stores.items:
        stores_obj.append(store_obj(store))
    return stores_obj


class StoreApi(MethodView):
    decorators = [app_required]

    def __init__(self):
        if (
            request.method != 'GET'
            and request.method != 'DELETE'
        ) and not request.json:
                abort(400)

    def get(self, store_id):
        if store_id:
            store = Store.objects.filter(
                external_id=store_id,
                live=True
            ).first()
            if store:
                response = {
                    'result': 'ok',

                    'store': store_obj(store)
                }
                return jsonify(response), 200

        else:
            stores = Store.objects.filter(live=True)
            page = int(request.args.get('page', 1))
            stores = stores.paginate(page=page, per_page=STORES_PER_PAGE)
            response = {
                'result': 'ok',
                'stores': stores_obj(stores),
                'links': [
                        {
                            'href': f'/api/stores/?page={page}',
                            'rel': 'self'
                        }
                    ],
            }
            if stores.has_prev:
                response['links'].append({
                    'href': f'/api/stores/?page={stores.prev_num}',
                    'rel': 'previous'
                })
            if stores.has_next:
                response['links'].append({
                    'href': f'/api/stores/?page={stores.next_num}',
                    'rel': 'next'
                })
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
                phone=store_json.get('phone'),
            )
            store.save()
            response = {
                'result': 'ok',
                'store': store_obj(store)
            }
            return jsonify(response), 201

    def put(self, store_id):
        store = Store.objects.filter(
            external_id=store_id,
            live=True
        ).first()
        if not store:
            return jsonify({}), 404
        store_json = request.json
        error = best_match(Draft4Validator(SCHEMA).iter_errors(store_json))
        if error:
            return jsonify(
                {'error': error.message}

            ), 400
        else:
            store.neighborhood = store_json.get('neighborhood')
            store.street_adress = store_json.get('street_adress')
            store.city = store_json.get('city')
            store.state = store_json.get('state')
            store.zip = store_json.get('zip')
            store.phone = store_json.get('phone')
            store.save()
            response = {
                'result': 'ok',
                'store': store_obj(store)
            }
            return jsonify(response), 200

    def delete(self, store_id):
        store = Store.objects.filter(
            external_id=store_id,
            live=True
        ).first()
        if not store:
            return jsonify({}), 404
        store.live = False
        store.save()
        return jsonify({}), 204


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
bp.add_url_rule('/stores/<store_id>',
                view_func=store_view,
                methods=['GET', 'PUT', 'DELETE', ]
                )
