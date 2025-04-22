from functools import wraps
from flask_jwt_extended import get_jwt_identity, get_jwt
from models.user import User
from datetime import datetime
from flask import jsonify

def session_validated(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        user = User.query.get(identity)
        token_time = datetime.fromtimestamp(get_jwt()["iat"])

        if token_time < user.last_password_reset:
            return jsonify({"error": "Sesión expirada. Inicia sesión de nuevo."}), 401

        return fn(*args, **kwargs)
    return wrapper
