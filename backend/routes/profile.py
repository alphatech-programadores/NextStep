# routes/profile.py
import os # Necesario para path.join, os.remove, os.sep, os.makedirs
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile
from models.user import User # Asegúrate de importar User
from werkzeug.utils import secure_filename

# from utils import session_validated # Descomentar si tu decorador session_validated es necesario

profile_bp = Blueprint("profile", __name__)

# --- FUNCIONES DE SUBIDA DE ARCHIVOS MOVIDAS AQUÍ ---
def allowed_file(filename, allowed_extensions):
    """
    Verifica si la extensión del archivo es permitida.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_subdir, allowed_extensions):
    # ... (código existente)
    
    filename = secure_filename(file.filename)
    print(f"--- DEBUG_SAVE ---")
    print(f"DEBUG_SAVE: Nombre de archivo seguro: {filename}") 
    
    
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_subdir)
    os.makedirs(target_dir, exist_ok=True)
    
    filepath = os.path.join(target_dir, filename)
    print(f"DEBUG_SAVE: Intentando guardar archivo en ruta ABSOLUTA: {filepath}") 

    try:
        file.save(filepath)
        print(f"DEBUG_SAVE: Archivo guardado EXITOSAMENTE en: {filepath}") 
        print(f"--- FIN DEBUG_SAVE ---") # Marcar el final del debug
        return os.path.join(upload_subdir, filename), None
    except Exception as e:
        current_app.logger.error(f"Error al guardar archivo {filename} en {filepath}: {e}")
        print(f"DEBUG_SAVE: ¡ERROR AL GUARDAR! Excepción: {e}") # AÑADIR ESTA LÍNEA
        print(f"--- FIN DEBUG_SAVE ---") # Marcar el final del debug
        return None, f"Error interno al guardar el archivo: {str(e)}"
# Asegúrate de importar secure_filename si no lo tienes ya

# --- FIN DE FUNCIONES DE SUBIDA DE ARCHIVOS ---


# Función auxiliar para obtener el perfil y crearlo si no existe
def _get_or_create_profile(user):
    if user.role.name == "student":
        profile = StudentProfile.query.get(user.email)
        if not profile:
            profile = StudentProfile(email=user.email)
            db.session.add(profile)
            db.session.commit()
        return profile, "student"
    elif user.role.name == "institution":
        profile = InstitutionProfile.query.get(user.email)
        if not profile:
            profile = InstitutionProfile(email=user.email)
            db.session.add(profile)
            db.session.commit()
        return profile, "institution"
    return None, None

# Obtener perfil del usuario autenticado
@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404

    profile, profile_type = _get_or_create_profile(user)

    if not profile:
        return jsonify({"message": "No hay perfil disponible para este rol."}), 404

    profile_data = user.to_dict()
    profile_data.update(profile.to_dict())

    upload_base_url_segment = current_app.config['UPLOAD_FOLDER'].split(os.sep)[-1]
    
    if profile_type == "student":
        if profile.cv_path:
            profile_data['cv_url'] = f"{request.url_root.rstrip('/')}/{upload_base_url_segment}/{profile.cv_path.replace(os.sep, '/')}"
        if profile.profile_picture_url:
            profile_data['profile_picture_url'] = f"{request.url_root.rstrip('/')}/{upload_base_url_segment}/{profile.profile_picture_url.replace(os.sep, '/')}"
    elif profile_type == "institution":
        if profile.logo_url:
            profile_data['logo_url'] = f"{request.url_root.rstrip('/')}/{upload_base_url_segment}/{profile.logo_url.replace(os.sep, '/')}"
            
    return jsonify(profile_data), 200




# Actualizar perfil del estudiante o institución (maneja archivos)
@profile_bp.route("/me", methods=["PUT"])
@jwt_required()
# @session_validated # Descomentar si tu decorador session_validated es necesario
def update_my_profile():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404
    
    profile, profile_type = _get_or_create_profile(user)

    if not profile:
        return jsonify({"message": "Este rol no tiene un perfil actualizable."}), 403

    data = request.form 

    if profile_type == "student":
        profile.career = data.get("career", profile.career)
        profile.semestre = data.get("semestre", profile.semestre)
        profile.average = data.get("average", profile.average)
        profile.phone = data.get("phone", profile.phone)
        profile.address = data.get("address", profile.address)
        profile.availability = data.get("availability", profile.availability)
        profile.skills = data.get("skills", profile.skills)
        profile.portfolio_url = data.get("portfolio_url", profile.portfolio_url)

        # Manejo de subida de CV
        if 'cv_file' in request.files:
            cv_file = request.files['cv_file']
            cv_path, error = save_uploaded_file(cv_file, 'cvs', current_app.config['ALLOWED_EXTENSIONS_CV'])
            if error:
                return jsonify({"error": f"Error al subir CV: {error}"}), 400
            if cv_path:
                if profile.cv_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.cv_path)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.cv_path))
                profile.cv_path = cv_path

        # Manejo de subida de Foto de Perfil
        if 'profile_picture_file' in request.files:
            profile_picture_file = request.files['profile_picture_file']
            pic_path, error = save_uploaded_file(profile_picture_file, 'profile_pics', current_app.config['ALLOWED_EXTENSIONS_IMG'])
            if error:
                return jsonify({"error": f"Error al subir foto de perfil: {error}"}), 400
            if pic_path:
                if profile.profile_picture_url and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture_url)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture_url))
                profile.profile_picture_url = pic_path

    elif profile_type == "institution":
        profile.institution_name = data.get("institution_name", profile.institution_name)
        profile.contact_person = data.get("contact_person", profile.contact_person)
        profile.contact_phone = data.get("contact_phone", profile.contact_phone)
        profile.sector = data.get("sector", profile.sector)
        profile.address = data.get("address", profile.address)
        profile.description = data.get("description", profile.description)

        # Manejo de subida de Logo
        if 'logo_file' in request.files:
            logo_file = request.files['logo_file']
            logo_path, error = save_uploaded_file(logo_file, 'logos', current_app.config['ALLOWED_EXTENSIONS_IMG'])
            if error:
                return jsonify({"error": f"Error al subir logo: {error}"}), 400
            if logo_path:
                if profile.logo_url and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.logo_url)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.logo_url))
                profile.logo_url = logo_path
    
    db.session.commit()
    return jsonify({"message": "Perfil actualizado exitosamente."}), 200




@profile_bp.route('/me/upload-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, 'uploads', 'profile_pics')
    os.makedirs(upload_folder, exist_ok=True)  # Asegura que exista
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    # Guarda el path relativo en la base de datos
    return jsonify({"message": "Archivo subido correctamente", "url": f"/uploads/profile_pics/{filename}"}), 200

@profile_bp.route("/student/me", methods=["GET"])
@jwt_required()
def get_my_prof():
    current_user_email = get_jwt_identity()
    
    # Buscamos el perfil del estudiante directamente usando el email
    student_profile = StudentProfile.query.filter_by(email=current_user_email).first()

    # Si un estudiante se registra pero nunca ha guardado su perfil, no existirá
    if not student_profile:
        return jsonify({
            "profile": None,
            "profile_completeness": 0,
            "message": "El perfil del estudiante no ha sido creado aún."
        }), 200 # Devolvemos 200 OK porque no es un error, simplemente no hay datos

    # --- LÓGICA DE COMPLETITUD MEJORADA ---
    # Lista de los campos que consideramos para el 100%
    # No incluimos email porque siempre está.
    fields_to_check = [
        'career', 'semestre', 'average', 'phone', 'address', 
        'availability', 'skills', 'portfolio_url', 'cv_path', 'profile_picture_url'
    ]
    
    completed_fields = 0
    for field in fields_to_check:
        # getattr(objeto, 'nombre_del_atributo') es una forma de acceder a un atributo dinámicamente
        if getattr(student_profile, field):
            completed_fields += 1
            
    total_fields = len(fields_to_check)
    profile_completeness = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0

    # Devolvemos tanto la info del perfil como el porcentaje de completitud
    return jsonify({
        "profile": student_profile.to_dict(),
        "profile_completeness": profile_completeness
    }), 200