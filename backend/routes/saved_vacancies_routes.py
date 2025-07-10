# routes/saved_vacancies_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.saved_vacancies_service import SavedVacanciesService
from extensions import db # Para asegurar el commit

saved_vacancies_bp = Blueprint("saved_vacancies", __name__, url_prefix="/api/saved-vacancies")

saved_vacancies_service = SavedVacanciesService()

# --- RUTA PARA AÑADIR/ELIMINAR (TOGGLE) UNA VACANTE GUARDADA ---
@saved_vacancies_bp.route("/toggle/<int:vacant_id>", methods=["POST"])
@jwt_required()
def toggle_saved_vacancy(vacant_id):
    current_user_email = get_jwt_identity()
    try:
        result = saved_vacancies_service.toggle_save_vacancy(
            student_email=current_user_email,
            vacant_id=vacant_id
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        db.session.rollback() # Asegura rollback en caso de error de servicio
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al hacer toggle de vacante guardada: {e}")
        return jsonify({"error": "Ocurrió un error inesperado al gestionar la vacante guardada."}), 500

# --- RUTA PARA OBTENER TODAS LAS VACANTES GUARDADAS POR EL USUARIO ---
@saved_vacancies_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_saved_vacancies():
    current_user_email = get_jwt_identity()
    try:
        saved_vacancies = saved_vacancies_service.get_user_saved_vacancies(
            student_email=current_user_email
        )
        return jsonify({"data": saved_vacancies}), 200 # Envuelve en 'data' para consistencia con otros endpoints
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error inesperado al obtener vacantes guardadas: {e}")
        return jsonify({"error": "Ocurrió un error inesperado al obtener tus vacantes guardadas."}), 500

# --- RUTA PARA VERIFICAR SI UNA VACANTE ESPECÍFICA ESTÁ GUARDADA POR EL USUARIO ---
@saved_vacancies_bp.route("/is-saved/<int:vacant_id>", methods=["GET"])
@jwt_required()
def is_vacant_saved_route(vacant_id):
    current_user_email = get_jwt_identity()
    try:
        is_saved = saved_vacancies_service.is_vacant_saved(
            student_email=current_user_email,
            vacant_id=vacant_id
        )
        return jsonify({"is_saved": is_saved}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error inesperado al verificar si vacante está guardada: {e}")
        return jsonify({"error": "Ocurrió un error inesperado al verificar el estado de la vacante."}), 500