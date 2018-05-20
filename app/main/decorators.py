from functools import wraps
from flask import request, jsonify


def app_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-APP-ID'):
            return jsonify({}), 403
        app_id = request.headers.get('X-APP-ID')
        app_secret = request.headers.get('X-APP-SECRET')
        print(app_id, app_secret)
        if app_id != 'lech' or app_secret != '123':
            return jsonify({}), 403
        else:
            return f(*args, **kwargs)
    return decorated_function
