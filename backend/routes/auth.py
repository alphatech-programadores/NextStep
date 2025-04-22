from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User, Role
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token
from datetime import timedelta, datetime
from flask_mail import Message
from extensions import mail
from utils import session_validated  

auth_bp = Blueprint("auth", __name__)

# Pruebas
@auth_bp.route("/testemail", methods=["GET"])
def testemail():
    msg = Message(
        subject="Prueba de correo",
        sender="noreply@nextstep.com",
        recipients=["juarez.botello.samuel@gmail.com"],
        body="Este es un mensaje de prueba desde Flask usando Mailtrap."
    )
    try:
        mail.send(msg)
        return jsonify({"message": "Correo enviado correctamente (verifica Mailtrap)."}), 200
    except Exception as e:
        print(str(e))  # o loggear como quieras
        return jsonify({"error": str(e)}), 500


# Registro de usuario
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role_name = data.get("role", "student")  # default: student

    if not email or not password or not name:
        return jsonify({"error": "Todos los campos son obligatorios."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El usuario ya existe."}), 409

    if role_name not in ["student", "institution"]:
        return jsonify({"error": "Rol inválido."}), 400
    
    # Buscar o crear el rol
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        db.session.commit()    

    user = User(email=email, name=name, role_id=role.id)
    user.set_password(password)

    db.session.add(user)

    if role_name == "student":
        student_profile = StudentProfile(
        email=email,
        career="",
        semestre=None,
        average=None,
        phone="",
        address="",
        availability="",
        skills="",
        portfolio_url="",
        cv_url=""
    )

        db.session.add(student_profile)
        
    elif role_name == "institution":
        institution_profile = InstitutionProfile(
        email=email,
        website="",
        sector="",
        descripcion=""
    )   
        db.session.add(institution_profile)
        
    db.session.commit()

    confirm_token = create_access_token(identity=email, expires_delta=timedelta(days=1), additional_claims={"confirm": True})

    confirm_url = f"http://localhost:5000/confirm/{confirm_token}"
    msg = Message(subject="Confirma tu correo",
                sender="noreply@nextstep.com",
                recipients=[email])
    msg.body = f"Hola {name}, por favor confirma tu correo visitando este enlace: {confirm_url}"

    mail.send(msg)

    return jsonify({"message": "Usuario registrado correctamente."}), 201

# Confirmación de correo
@auth_bp.route("/confirm/<token>", methods=["GET"])
def confirm_email(token):
    try:
        decoded = decode_token(token)
        email = decoded["sub"]
        claims = decoded.get("confirm", False)

        if not claims:
            return jsonify({"error": "Token inválido para confirmación"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if user.is_confirmed:
            return jsonify({"message": "Correo ya confirmado"}), 200

        user.is_confirmed = True
        db.session.commit()
        return jsonify({"message": "Correo confirmado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Token inválido o expirado"}), 400


# Login de usuario
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales inválidas."}), 401

    if not user.is_confirmed:
        return jsonify({"error": "Confirma tu correo para iniciar sesión."}), 403

    access_token = create_access_token(
        identity=user.email,
        additional_claims={"role": user.role.name}
    )

    return jsonify({
        "message": "Inicio de sesión exitoso.",
        "access_token": access_token,
        "user": {
            "email": user.email,
            "name": user.name,
            "role": user.role.name
        }
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email requerido"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Si el correo está registrado, se enviará un enlace de recuperación."}), 200

    reset_token = create_access_token(
        identity=user.email,
        expires_delta=timedelta(hours=1),
        additional_claims={"reset": True}
    )

    reset_url = f"http://localhost:5000/reset-password/{reset_token}"
    msg = Message(
        subject="Restablece tu contraseña",
        sender="noreply@nextstep.com",
        recipients=[email],
        body=f"Hola, puedes restablecer tu contraseña con este enlace:\n{reset_url}"
    )

    mail.send(msg)
    return jsonify({"message": "Si el correo está registrado, se enviará un enlace de recuperación."}), 200

from flask_jwt_extended import decode_token

@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request.get_json()
    new_password = data.get("password")

    if not new_password:
        return jsonify({"error": "Contraseña nueva requerida"}), 400

    try:
        decoded = decode_token(token)
        if not decoded.get("reset", False):
            return jsonify({"error": "Token inválido para restablecimiento"}), 400

        email = decoded["sub"]
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user.set_password(new_password)
        user.last_password_reset = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Contraseña actualizada exitosamente."}), 200

    except Exception as e:
        return jsonify({"error": "Token inválido o expirado"}), 400


@auth_bp.route("/delete", methods=["DELETE"])
@jwt_required()
@session_validated
def delete_account():
    current_email = get_jwt_identity()
    user = User.query.get(current_email)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Borrar perfil asociado
    if user.role.name == "student":
        profile = StudentProfile.query.get(current_email)
        if profile:
            db.session.delete(profile)

        # Borrar postulaciones
        from models.application import Application
        Application.query.filter_by(student_email=current_email).delete()

    elif user.role.name == "institution":
        profile = InstitutionProfile.query.get(current_email)
        if profile:
            db.session.delete(profile)

        # Borrar vacantes y postulaciones a esas vacantes
        from models.vacant import Vacant
        from models.application import Application
        vacants = Vacant.query.filter_by(institution_email=current_email).all()
        for v in vacants:
            Application.query.filter_by(vacant_id=v.id).delete()
            db.session.delete(v)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Cuenta eliminada correctamente."}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@session_validated
def logout():
    # Implementar revocación, aquí se agrega el JWT a una blacklist
    return jsonify({"message": "Sesión cerrada."}), 200

