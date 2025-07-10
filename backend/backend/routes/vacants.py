from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import application_service
from services.vacant_service import VacantService # Importa tu nuevo servicio
from flask import current_app # Necesario para logging si lo tienes en el servicio

vacants_bp = Blueprint("vacants", __name__, url_prefix="/api/vacants")

# Instancia del servicio
vacant_service = VacantService()

@vacants_bp.route("/filters/areas", methods=["GET", "OPTIONS"])
def get_unique_areas_route():
    # Si es una solicitud OPTIONS, simplemente responde OK para la preflight
    if request.method == 'OPTIONS':
        return '', 200
    try:
        areas = vacant_service.get_unique_areas()
        return jsonify(areas), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener áreas únicas: {e}")
        return jsonify({"error": f"Error al obtener áreas únicas: {e}"}), 500

@vacants_bp.route("/filters/modalities", methods=["GET", "OPTIONS"])
def get_unique_modalities_route():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        modalities = vacant_service.get_unique_modalities()
        return jsonify(modalities), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener modalidades únicas: {e}")
        return jsonify({"error": f"Error al obtener modalidades únicas: {e}"}), 500

@vacants_bp.route("/filters/locations", methods=["GET", "OPTIONS"])
def get_unique_locations_route():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        locations = vacant_service.get_unique_locations()
        return jsonify(locations), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener ubicaciones únicas: {e}")
        return jsonify({"error": f"Error al obtener ubicaciones únicas: {e}"}), 500

@vacants_bp.route("/filters/tags", methods=["GET", "OPTIONS"])
def get_unique_tags_route():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        tags = vacant_service.get_unique_tags()
        return jsonify(tags), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener tags únicos: {e}")
        return jsonify({"error": f"Error al obtener tags únicos: {e}"}), 500

# --- CORRECCIÓN PRINCIPAL PARA EL ERROR 500 ---
@vacants_bp.route("/", methods=["GET", "OPTIONS"])
@jwt_required(optional=True) # @jwt_required maneja OPTIONS si está configurado en CORS
def list_and_search_vacants_route():
    # Si la solicitud es OPTIONS (preflight), simplemente respondemos OK y terminamos aquí
    if request.method == 'OPTIONS':
        return '', 200 # Respuesta vacía con 200 OK para preflight

    identity = get_jwt_identity()
    
    filters = {
        "area": request.args.get("area", "").strip(),
        "modality": request.args.get("modality", "").strip(),
        "location": request.args.get("location", "").strip(),
        "tag": request.args.get("tag", "").strip(),
        "keyword": request.args.get("q", "").strip()
    }
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
        result = vacant_service.list_and_search_vacants(identity, filters, page, per_page)
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al listar/buscar vacantes: {e}", exc_info=True)
        return jsonify({"error": f"Error al listar/buscar vacantes: {e}"}), 500

@vacants_bp.route("/<int:vacant_id>", methods=["GET", "OPTIONS"])
def get_vacant_details_route(vacant_id: int):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        details = vacant_service.get_vacant_details(vacant_id)
        return jsonify(details), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener detalles de la vacante: {e}")
        return jsonify({"error": f"Error al obtener detalles de la vacante: {e}"}), 500

@vacants_bp.route("/<int:vacant_id>/apply", methods=["POST", "OPTIONS"])
@jwt_required()
def apply_to_vacant_route(vacant_id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.apply_to_vacant(vacant_id, current_user_email)
        return jsonify(result), 201
    except ValueError as e:
        if "Acceso denegado" in str(e):
            return jsonify({"error": str(e)}), 403
        elif "Vacante no encontrada" in str(e):
            return jsonify({"error": str(e)}), 404
        elif "Ya has postulado" in str(e):
            return jsonify({"error": str(e)}), 409
        else:
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al postular: {e}")
        return jsonify({"error": f"Error inesperado al postular: {e}"}), 500

@vacants_bp.route("/check_status/<int:vacant_id>", methods=["GET", "OPTIONS"])
@jwt_required()
def check_application_status_route(vacant_id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        status = vacant_service.check_application_status(vacant_id, current_user_email)
        return jsonify(status), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al verificar estado de postulación: {e}")
        return jsonify({"error": f"Error al verificar estado de postulación: {e}"}), 500

@vacants_bp.route("/", methods=["POST", "OPTIONS"])
@jwt_required()
def create_vacant_route():
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    data = request.get_json()
    try:
        result = vacant_service.create_vacant(current_user_email, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al crear vacante: {e}")
        return jsonify({"error": f"Error inesperado al crear vacante: {e}"}), 500

@vacants_bp.route("/my", methods=["GET", "OPTIONS"])
@jwt_required()
def list_my_vacants_route():
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        vacants = vacant_service.list_my_vacants(current_user_email)
        return jsonify(vacants), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al listar mis vacantes: {e}")
        return jsonify({"error": f"Error al listar mis vacantes: {e}"}), 500

@vacants_bp.route("/<int:id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_vacant_route(id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    data = request.get_json()
    try:
        result = vacant_service.update_vacant(id, current_user_email, data)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else:
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al actualizar vacante: {e}")
        return jsonify({"error": f"Error inesperado al actualizar vacante: {e}"}), 500

@vacants_bp.route("/<int:id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_vacant_route(id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.delete_vacant(id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else:
            return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al eliminar vacante: {e}")
        return jsonify({"error": f"Error inesperado al eliminar vacante: {e}"}), 500

@vacants_bp.route("/<int:id>/status", methods=["PATCH", "OPTIONS"])
@jwt_required()
def toggle_vacant_status_route(id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    new_status = request.get_json().get("status")
    try:
        result = vacant_service.toggle_vacant_status(id, current_user_email, new_status)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else:
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al cambiar estado de vacante: {e}")
        return jsonify({"error": f"Error inesperado al cambiar estado de vacante: {e}"}), 500

@vacants_bp.route("/<int:id>/publish", methods=["PATCH", "OPTIONS"])
@jwt_required()
def publish_vacant_route(id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.publish_vacant(id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else:
            return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al publicar vacante: {e}")
        return jsonify({"error": f"Error inesperado al publicar vacante: {e}"}), 500

@vacants_bp.route("/<int:id>/applications", methods=["GET", "OPTIONS"])
@jwt_required()
def get_applications_for_vacant_route(id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    try:
        applications_data = vacant_service.get_applications_for_vacant(id, current_user_email)
        return jsonify(applications_data), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else:
            return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al obtener postulaciones: {e}")
        return jsonify({"error": f"Error inesperado al obtener postulaciones: {e}"}), 500

@vacants_bp.route("/<int:application_id>/decision", methods=["PATCH", "OPTIONS"])
@jwt_required()
def decide_application_route(application_id: int):
    if request.method == 'OPTIONS':
        return '', 200
    current_user_email = get_jwt_identity()
    data = request.get_json()
    decision = data.get("decision")
    feedback = data.get("feedback", "")
    try:
        result = vacant_service.decide_application(application_id, current_user_email, decision, feedback)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        elif "Postulación no encontrada" in str(e):
            return jsonify({"error": str(e)}), 404
        else:
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error inesperado al decidir sobre postulación: {e}")
        return jsonify({"error": f"Error inesperado al decidir sobre postulación: {e}"}), 500

@vacants_bp.route("/map", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def vacants_for_map_route():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        vacants = vacant_service.get_vacants_for_map()
        return jsonify([v.to_dict() for v in vacants]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error al obtener vacantes para el mapa: {e}")
        return jsonify({"error": f"Error al obtener vacantes para el mapa: {e}"}), 500
    
@vacants_bp.route("/filters/hours", methods=["GET", "OPTIONS"]) # ASEGÚRATE DE QUE "OPTIONS" ESTÉ AQUÍ
def get_unique_hours_route():
    # --- ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ AL PRINCIPIO DE LA FUNCIÓN ---
    if request.method == 'OPTIONS':
        return '', 200 # Respuesta OK para la solicitud preflight
    # ------------------------------------------------------------------
    try:
        hours = vacant_service.get_unique_hours()
        return jsonify(hours), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Asegúrate de que current_app esté importado si usas logging aquí
        # current_app.logger.error(f"Error al obtener horas únicas: {e}")
        return jsonify({"error": f"Error al obtener horas únicas: {e}"}), 500
    
@vacants_bp.route("/<int:vacant_id>/application", methods=["GET"])
@jwt_required()
def get_applications_for_vacant(vacant_id):
    try:
        applications = application_service.get_applications_by_vacant(vacant_id)
        return jsonify(applications), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener postulaciones: {e}"}), 500
    
