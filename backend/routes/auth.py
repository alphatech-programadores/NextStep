# backend/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
# CAMBIO AQUÍ: Añadir get_jwt a la importación
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies, get_jwt
from services.auth_service import AuthService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # Importar excepciones
from config import Config
from flask_mail import Message
from extensions import mail # Asegúrate de que mail esté importado

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

# Inicializar el serializador para tokens de confirmación/restablecimiento
s = URLSafeTimedSerializer(Config.SECRET_KEY)

@auth_bp.route("/register", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
def register():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role_name = data.get("role")

    if not all([email, password, name, role_name]):
        return jsonify({"error": "Faltan campos obligatorios."}), 400

    try:
        user = auth_service.register_user(email, password, name, role_name)

        # Generar token de confirmación
        token = s.dumps(user.email, salt='email-confirm')
        user.confirmation_token = token
        user.confirmed_on = None
        # La llamada a db.session.commit() ya se hace en auth_service.register_user
        # auth_service.user_repository.db_session.commit() # No es necesario aquí

        # Enviar correo de confirmación
        msg = Message("Confirma tu cuenta",
                      sender=Config.MAIL_USERNAME,
                      recipients=[user.email])
        link = f"{Config.FRONTEND_URL}/auth/confirm/{token}"
        msg.body = f"Tu enlace de confirmación es {link}"
        mail.send(msg)

        return jsonify({"message": "Registro exitoso. Se ha enviado un correo de confirmación."}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error en el registro: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500

@auth_bp.route("/confirm/<token>", methods=["GET", "OPTIONS"]) # Añadir OPTIONS
def confirm_email(token):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        user = auth_service.user_repository.get_by_email(email)

        if not user:
            return jsonify({"error": "Token inválido o usuario no encontrado."}), 400

        if user.is_confirmed:
            return jsonify({"message": "La cuenta ya ha sido confirmada."}), 200

        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()
        user.confirmation_token = None
        auth_service.user_repository.db_session.commit()
        return jsonify({"message": "Cuenta confirmada exitosamente."}), 200
    except SignatureExpired:
        return jsonify({"error": "El token ha expirado."}), 400
    except BadTimeSignature:
        return jsonify({"error": "Token inválido."}), 400
    except Exception as e:
        current_app.logger.error(f"Error al confirmar email: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500

@auth_bp.route("/login", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
def login():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Faltan correo electrónico o contraseña."}), 400

    try:
        auth_data = auth_service.login_user(email, password)
        response = jsonify(auth_data)
        return response, 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Error en el login: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500

@auth_bp.route("/refresh", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
@jwt_required(refresh=True)
def refresh():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        auth_data = auth_service.refresh_access_token()
        response = jsonify(auth_data)
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error al refrescar token: {e}")
        return jsonify({"error": "Error al refrescar token."}), 401

@auth_bp.route("/logout", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
@jwt_required()
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    jti = get_jwt()["jti"]
    try:
        auth_service.logout_user(jti)
        response = jsonify({"message": "Sesión cerrada correctamente."})
        unset_jwt_cookies(response)
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error al cerrar sesión: {e}")
        return jsonify({"error": "Error al cerrar sesión."}), 500

@auth_bp.route("/reset-request", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
def reset_password_request():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Correo electrónico es obligatorio."}), 400
    try:
        auth_service.reset_password_request(email)
        return jsonify({"message": "Si tu cuenta existe, se ha enviado un correo para restablecer la contraseña."}), 200
    except ValueError as e:
        return jsonify({"message": "Si tu cuenta existe, se ha enviado un correo para restablecer la contraseña."}), 200
    except Exception as e:
        current_app.logger.error(f"Error en la solicitud de restablecimiento: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500

@auth_bp.route("/reset-password/<token>", methods=["POST", "OPTIONS"]) # Añadir OPTIONS
def reset_password(token): # Asegúrate de que 'token' sea un argumento de la función
    if request.method == 'OPTIONS':
        return '', 200
    # token = request.view_args['token'] # Ya se pasa como argumento
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "Nueva contraseña es obligatoria."}), 400

    try:
        auth_service.reset_password(token, new_password)
        return jsonify({"message": "Contraseña restablecida correctamente."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error al restablecer contraseña: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500

