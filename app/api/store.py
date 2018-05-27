from flask.views import MethodView
from app.api import bp


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
