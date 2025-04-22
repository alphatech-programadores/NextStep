from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile
from models.user import User
from utils import session_validated

profile_bp = Blueprint("profile", __name__)

# Obtener perfil del usuario autenticado
@profile_bp.route("/me", methods=["GET"])
@jwt_required()
@session_validated
def get_my_profile():
    user = User.query.get(get_jwt_identity())

    if user.role.name == "student":
        profile = StudentProfile.query.get(user.email)
    elif user.role.name == "institution":
        profile = InstitutionProfile.query.get(user.email)
    else:
        return jsonify({"message": "No hay perfil disponible para este rol."})

    return jsonify(profile.to_dict())


# Actualizar perfil del estudiante o institución
@profile_bp.route("/me", methods=["PUT"])
@jwt_required()
@session_validated
def update_my_profile():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    if user.role.name == "student":
        profile = StudentProfile.query.get(user.email)
        for field in ["career", "semester", "average", "phone", "address", "availability", "skills", "portfolio_url", "cv_url"]:
            if field in data:
                setattr(profile, field, data[field])
    elif user.role.name == "institution":
        profile = InstitutionProfile.query.get(user.email)
        for field in ["institution_name", "contact_person", "contact_phone", "sector", "address", "description"]:
            if field in data:
                setattr(profile, field, data[field])
    else:
        return jsonify({"message": "Este rol no puede modificar perfil."}), 403

    db.session.commit()
    return jsonify({"message": "Perfil actualizado correctamente."})
