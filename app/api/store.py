from flask.views import MethodView
from app.api import bp

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
    pass


store_view = StoreApi.as_view('store_api')
bp.add_url_rule('/stores/', defaults={'store_id': None},
                view_func=store_view,
                methods=['GET']
                )
bp.add_url_rule('/stores/',
                view_func=store_view,
                methods=['POST']
                )
bp.add_url_rule('/stores/',
                view_func=store_view,
                methods=['GET', 'PUT', 'DELETE']
                )
