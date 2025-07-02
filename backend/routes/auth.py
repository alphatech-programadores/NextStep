# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity # Asumiendo que get_jwt_identity es usado en otras rutas

# Creamos el Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Instancia del servicio
auth_service = AuthService()

# --- RUTA DE REGISTRO ---
@auth_bp.route("/register", methods=["POST"])
def register_user_route():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role = data.get("role")

    try:
        result = auth_service.register_user(email=email, password=password, name=name, role_name=role)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado al registrar: {e}"}), 500


# --- RUTA DE CONFIRMACIÓN DE CORREO ---
# MODIFICADO: Aceptar token en la URL O email y código en el cuerpo de la solicitud
@auth_bp.route("/confirm", methods=["POST"]) # CAMBIO A POST para recibir cuerpo
@auth_bp.route("/confirm/<token>", methods=["GET"]) # Mantener GET para enlaces directos
def confirm_email_route(token=None): # 'token' es opcional ahora
    email = None
    code = None

    if request.method == 'POST':
        data = request.json
        email = data.get("email")
        code = data.get("code")
    
    try:
        # Llama al servicio pasando el token O el email y código
        result = auth_service.confirm_email(token=token, email=email, code=code)
        
        # Para la ruta GET, una confirmación exitosa normalmente redirige
        if request.method == 'GET':
            # Puedes redirigir a una página de éxito o login en tu frontend
            from flask import redirect, url_for
            # current_app.config['BASE_URL'] ya debería apuntar al frontend
            # return redirect(f"{current_app.config['BASE_URL']}/auth/login?confirmed=true")
            # Para una API RESTful, lo mejor es siempre devolver JSON, incluso para GET.
            # El frontend manejará la redirección.
            return jsonify(result), 200
        else: # Es POST
            return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado: {e}"}), 500

# --- RUTA DE INICIO DE SESIÓN ---
@auth_bp.route("/login", methods=["POST"])
def login_user_route():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        result = auth_service.login_user(email=email, password=password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado al iniciar sesión: {e}"}), 500

# --- RUTA PARA SOLICITAR RESTABLECER CONTRASEÑA ---
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    data = request.json
    email = data.get("email")
    try:
        result = auth_service.forgot_password(email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado en recuperación de contraseña: {e}"}), 500

# --- RUTA PARA RESTABLECER CONTRASEÑA ---
@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password_route(token):
    data = request.json
    new_password = data.get("new_password")
    try:
        result = auth_service.reset_password(token, new_password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado al restablecer contraseña: {e}"}), 500

# --- RUTA PARA REENVIAR CORREO DE CONFIRMACIÓN ---
@auth_bp.route("/resend-confirmation", methods=["POST"])
def resend_confirmation_email_route():
    data = request.json
    email = data.get("email")
    try:
        result = auth_service.resend_confirmation_email(email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado al reenviar correo: {e}"}), 500
    
@auth_bp.route("/logout", methods=["GET"])
def logout():    
    result = auth_service.logout_user
    return jsonify([result]), 200