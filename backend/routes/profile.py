from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.profile_service import ProfileService # Importa tu nuevo servicio
from flask import current_app
from extensions import db

# Creamos el Blueprint
profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

# Instancia del servicio
profile_service = ProfileService()

# --- RUTA PARA OBTENER EL PERFIL DEL USUARIO LOGUEADO (Estudiante o Institución) ---
@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile_route():
    current_user_email = get_jwt_identity()
    try:
        profile_data, profile_type = profile_service.get_my_profile(current_user_email)
        return jsonify(profile_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al obtener el perfil: {e}"}), 500

# --- RUTA PARA ACTUALIZAR EL PERFIL DEL USUARIO LOGUEADO (Estudiante o Institución) ---
@profile_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_profile_route():
    current_user_email = get_jwt_identity()
    # request.form contiene los campos de texto, request.files contiene los archivos
    form_data = request.form
    files_data = request.files

    try:
        result = profile_service.update_my_profile(current_user_email, form_data, files_data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e: # Errores como fallos en la subida de archivos
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al actualizar el perfil: {e}"}), 500

# --- RUTA PARA SUBIR FOTO DE PERFIL (Si quieres mantenerla separada, aunque update_my_profile ya maneja esto) ---
# Si update_my_profile maneja archivos, esta ruta podría ser redundante.
# Si la dejas, el servicio debería tener un método específico como upload_profile_picture(email, file).
@profile_bp.route('/me/upload-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture_route():
    current_user_email = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la solicitud."}), 400
    
    file = request.files['file']
    try:
        # Aquí el servicio podría tener un método específico como profile_service.upload_profile_picture(current_user_email, file)
        # Por simplicidad, y ya que update_my_profile lo hace, considera integrarlo allí.
        # Si la dejas separada, la lógica de _save_uploaded_file debería estar en un método público del servicio.
        # Por ahora, la lógica directa es solo para demostración si se mantiene separada.
        pic_path, error = profile_service._save_uploaded_file(file, 'profile_pics', current_app.config['ALLOWED_EXTENSIONS_IMG']) # Llama a la función auxiliar del servicio
        if error:
            return jsonify({"error": f"Error al subir imagen: {error}"}), 400
        
        # Una vez guardado, actualiza el perfil del usuario (esto lo harías en el servicio)
        user = profile_service.user_repo.get_by_email(current_user_email)
        if user and user.student_profile:
            # Aquí podrías llamar a un método específico del repo de StudentProfile para actualizar solo la URL
            user.student_profile.profile_picture_url = pic_path
            db.session.commit()
            return jsonify({"message": "Imagen de perfil subida correctamente", "url": f"{current_app.config['BASE_URL']}/uploads/{pic_path}"}), 200
        else:
            return jsonify({"error": "No se pudo asociar la imagen al perfil."}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al subir la imagen: {e}"}), 500


# --- RUTA PARA OBTENER COMPLETITUD DEL PERFIL DE ESTUDIANTE (Si se mantiene separada) ---
@profile_bp.route("/student/me", methods=["GET"])
@jwt_required()
def get_my_student_profile_completeness_route():
    current_user_email = get_jwt_identity()
    try:
        result = profile_service.get_student_profile_completeness(current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al obtener la completitud del perfil: {e}"}), 500

# --- RUTA PARA ELIMINAR CUENTA (Movida aquí desde auth.py) ---
@profile_bp.route("/delete-account", methods=["DELETE"]) # Nombre de ruta más descriptivo
@jwt_required()
def delete_my_account_route():
    current_email = get_jwt_identity()
    try:
        result = profile_service.delete_account(current_email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error inesperado al eliminar la cuenta: {e}"}), 500