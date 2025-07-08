from flask import Blueprint, request, jsonify, current_app # Import current_app for logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.application_service import ApplicationService # Correct import
import traceback # Import traceback for error logging

app_bp = Blueprint("application", __name__, url_prefix="/api/apply")

# Instantiate the service here
application_service = ApplicationService() # Moved instantiation here for consistency if needed, or keep it imported directly as 'services.application_service'

@app_bp.route("/me", methods=["GET", "OPTIONS"]) # This is the missing route!
@jwt_required()
def get_my_applications_route():
    if request.method == "OPTIONS":
        return jsonify({}), 200 # Handle CORS preflight

    try:
        current_user_email = get_jwt_identity()
        status_filter = request.args.get("status") # Get status filter from query params
        page = request.args.get("page", 1, type=int) # Get page from query params, default 1
        per_page = request.args.get("per_page", 10, type=int) # Get per_page from query params, default 10

        applications_data = application_service.get_my_applications(
            current_user_email, status_filter, page, per_page
        )
        return jsonify(applications_data), 200
    except ValueError as e:
        current_app.logger.error(f"Validation Error in get_my_applications_route: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        current_app.logger.error(f"Error fetching applications for student: {e}")
        return jsonify({"error": "Error al cargar tus postulaciones."}), 500

@app_bp.route("/<int:application_id>/decision", methods=["PATCH", "OPTIONS"])
@jwt_required()
def decide_application(application_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()
    new_status = data.get("status")
    feedback = data.get("feedback", None)
    user_email = get_jwt_identity() # Get institution email

    if new_status not in ["aceptado", "rechazado"]:
        return jsonify({"error": "Estado inválido. Usa 'aceptado' o 'rechazado'."}), 400

    try:
        # Pass user_email to the service method
        app_result = application_service.decide_application(
            user_email, application_id, new_status, feedback
        )
        return jsonify({"message": f"Postulación {new_status} correctamente", "application": app_result}), 200
    except ValueError as e:
        current_app.logger.error(f"Validation Error in decide_application: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al actualizar la postulación: {e}")
        return jsonify({"error": f"Error al actualizar la postulación: {e}"}), 500
    


@app_bp.route("/<int:application_id>/cancel", methods=["PATCH", "OPTIONS"]) # New route for cancellation
@jwt_required()
def cancel_application_route(application_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        current_user_email = get_jwt_identity()
        app_result = application_service.cancel_application(current_user_email, application_id)
        return jsonify({"message": "Postulación cancelada correctamente", "application": app_result}), 200
    except ValueError as e:
        current_app.logger.error(f"Validation Error in cancel_application_route: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        current_app.logger.error(f"Error al cancelar la postulación: {e}")
        return jsonify({"error": f"Error al cancelar la postulación: {e}"}), 500