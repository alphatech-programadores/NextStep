# En backend/routes/application.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.application_service import ApplicationService # Importar tu servicio

app_bp = Blueprint("application", __name__, url_prefix="/api/apply")

# Instancia del servicio
application_service = ApplicationService()

@app_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_applications_route():
    current_user_email = get_jwt_identity()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
        result = application_service.get_my_applications(
            current_user_email, status_filter, page, per_page
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403 # Acceso denegado
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al obtener mis postulaciones: {e}"}), 500