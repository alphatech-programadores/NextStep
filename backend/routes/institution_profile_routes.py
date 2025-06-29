from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.institution_profile import InstitutionProfile

# Creamos el Blueprint
inst_profile_bp = Blueprint("institution_profile", __name__, url_prefix="/api/profile/institution")

# --- RUTA PARA OBTENER EL PERFIL DE LA INSTITUCIÓN LOGUEADA ---
@inst_profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_institution_profile():
    current_user_email = get_jwt_identity()
    
    # Verificamos que el usuario tenga el rol correcto
    user = User.query.filter_by(email=current_user_email).first()
    if not user or user.role.name != 'institution':
        return jsonify({"error": "Acceso denegado."}), 403

    # Buscamos el perfil de la institución
    profile = InstitutionProfile.query.filter_by(email=current_user_email).first()

    # Si una institución se registra pero nunca ha guardado su perfil, no existirá
    if not profile:
        # Devolvemos un perfil vacío para que el frontend pueda manejarlo
        return jsonify({
            "profile": {
                "email": current_user_email,
                "institution_name": user.name, # Usar el nombre de registro como fallback
                "contact_person": "",
                "contact_phone": "",
                "sector": "",
                "address": "",
                "description": "",
                "logo_url": None
            },
            "message": "El perfil de la institución no ha sido creado aún."
        }), 200

    return jsonify({"profile": profile.to_dict()}), 200


# --- RUTA PARA ACTUALIZAR EL PERFIL DE LA INSTITUCIÓN LOGUEADA ---
@inst_profile_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_institution_profile():
    current_user_email = get_jwt_identity()
    
    user = User.query.filter_by(email=current_user_email).first()
    if not user or user.role.name != 'institution':
        return jsonify({"error": "Acceso denegado."}), 403

    # Buscamos el perfil existente o creamos uno nuevo si no existe
    profile = InstitutionProfile.query.filter_by(email=current_user_email).first()
    if not profile:
        profile = InstitutionProfile(email=current_user_email)
        db.session.add(profile)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos."}), 400

    # Actualizamos los campos con los datos recibidos del formulario
    profile.institution_name = data.get('institution_name', profile.institution_name)
    profile.contact_person = data.get('contact_person', profile.contact_person)
    profile.contact_phone = data.get('contact_phone', profile.contact_phone)
    profile.sector = data.get('sector', profile.sector)
    profile.address = data.get('address', profile.address)
    profile.description = data.get('description', profile.description)
    # Nota: La subida de archivos (logo) se manejaría en una ruta separada o con FormData

    try:
        db.session.commit()
        return jsonify({"message": "Perfil de la institución actualizado exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar en la base de datos: {str(e)}"}), 500
