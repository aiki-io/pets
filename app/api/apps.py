import uuid
from datetime import datetime, timedelta
from flask.views import MethodView
from flask import request, abort, jsonify

from app import bcrypt
from app.api.models import App, Access
from app.api import bp


class AppApi(MethodView):

    def __init__(self):
        if not request.json:
            abort(400)

    def post(self):
        if 'app_id' not in request.json or 'app_secret' not in request.json:
            error = {
                'code': 'MISSING_APP_ID_OR_APP_SECRET'
            }
            return jsonify({'error': error}), 400

        existing_app = App.objects.filter(
            app_id=request.json.get('app_id')
        ).first()
        if existing_app:
            error = {
                'code': 'APP_ID_ALREADY_EXISTS'
            }
            return jsonify({'error': error}), 400
        else:
            hashed_password = bcrypt.generate_password_hash(
                request.json.get('app_secret')
            )
            app = App(
                app_id=request.json.get('app_id'),
                app_secret=hashed_password
            )
            app.save()
            return jsonify({'result': 'ok'})


class AccessApi(MethodView):

    def __init__(self):
        if not request.json:
            abort(400)

    def post(self):
        app_id = request.json.get('app_id')
        app_secret = request.json.get('app_secret')
        if not app_id or not app_secret:
                error = {
                    'code': 'MISSING_APP_ID_OR_APP_SECRET'
                }
                return jsonify({'error': error}), 400
        app = App.objects.filter(
            app_id=app_id
        ).first()
        if not app:
            error = {
                'code': 'INVALID_CREDENTIALS'
            }
            return jsonify({'error': error}), 400
        else:
            if bcrypt.check_password_hash(
                app.app_secret,
                request.json['app_secret']
            ):
                tokens = Access.objects.filter(app=app)
                tokens.delete()
                token = str(uuid.uuid4())
                now = datetime.utcnow()
                expires = now + timedelta(days=30)
                access = Access(
                    app=app,
                    token=token,
                    expires=expires
                )
                access.save()
                expires_3339 = expires.isoformat('T') + 'Z'
                return jsonify({
                    'token': token,
                    'expires': expires_3339
                }), 200

            else:
                error = {
                    'code': 'INVALID_CREDENTIALS'
                }
                return jsonify({'error': error}), 400


app_view = AppApi.as_view('app_api')
access_view = AccessApi.as_view('access_api')

bp.add_url_rule('/apps/', view_func=app_view, methods=['POST', ])
bp.add_url_rule('/apps/tokens/', view_func=access_view, methods=['POST', ])
