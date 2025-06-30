from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from extensions import mail
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token #
from services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__)

# Instancia del servicio
auth_service = AuthService()

# Pruebas (dejar fuera del servicio si es solo para testing de infraestructura)
@auth_bp.route("/testemail", methods=["GET"])
def testemail():
    try:
        msg = Message(
            subject="Prueba de correo",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=["sanchez.hernandez.luis.felipe12@gmail.com", "alejandrofuentes.glz@gmail.com", "juarez.botello.samuel@gmail.com"],
            body="Este es un mensaje de prueba desde Flask usando Mailtrap."
        )
        mail.send(msg) #
        return jsonify({"message": "Correo enviado correctamente (verifica Mailtrap)."}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

# Registro de usuario
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role_name = data.get("role", "student")

    try:
        result = auth_service.register_user(email, password, name, role_name)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado durante el registro."}), 500

# Confirmación de correo
@auth_bp.route("/confirm/<token>", methods=["GET"])
def confirm_email(token):
    try:
        result = auth_service.confirm_email(token)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado al confirmar el correo."}), 500

# Login de usuario
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        result = auth_service.login_user(email, password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado durante el login."}), 500

# Olvidó su contraseña
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    try:
        result = auth_service.forgot_password(email)
        return jsonify(result), 200
    except ValueError as e: # Esto no debería ocurrir si el servicio maneja el mensaje "si existe"
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado al solicitar restablecimiento de contraseña."}), 500

# Resetear contraseña
@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request.get_json()
    new_password = data.get("password")

    try:
        result = auth_service.reset_password(token, new_password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado al restablecer la contraseña."}), 500

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        result = auth_service.logout_user()
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error inesperado durante el cierre de sesión."}), 500
    
@auth_bp.route("/resend-confirmation", methods=["POST"])
def resend_confirmation():
    data = request.get_json()
    email = data.get("email")

    try:
        result = auth_service.resend_confirmation_email(email)
        return jsonify(result), 200
    except ValueError as e: # Para validación de 'email requerido'
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e: # Para errores como el rate limiting o fallos de envío
        return jsonify({"error": str(e)}), 429 if "espera" in str(e) else 500 # 429 Too Many Requests para rate limiting
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al reenviar el correo de confirmación: {e}"}), 500
