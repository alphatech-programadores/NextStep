from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.vacant_service import VacantService # Importa tu nuevo servicio

vacants_bp = Blueprint("vacants", __name__, url_prefix="/api/vacants")

# Instancia del servicio
vacant_service = VacantService()

@vacants_bp.route("/filters/areas", methods=["GET"])
def get_unique_areas_route():
    try:
        areas = vacant_service.get_unique_areas()
        return jsonify(areas), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener áreas únicas: {e}"}), 500

@vacants_bp.route("/filters/modalities", methods=["GET"])
def get_unique_modalities_route():
    try:
        modalities = vacant_service.get_unique_modalities()
        return jsonify(modalities), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener modalidades únicas: {e}"}), 500

@vacants_bp.route("/filters/locations", methods=["GET"])
def get_unique_locations_route():
    try:
        locations = vacant_service.get_unique_locations()
        return jsonify(locations), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener ubicaciones únicas: {e}"}), 500

@vacants_bp.route("/filters/tags", methods=["GET"])
def get_unique_tags_route():
    try:
        tags = vacant_service.get_unique_tags()
        return jsonify(tags), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener tags únicos: {e}"}), 500

@vacants_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def list_and_search_vacants_route():
    identity = get_jwt_identity() # Será None si no hay token
    
    # Extraer filtros de request.args
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
        return jsonify({"error": f"Error al listar/buscar vacantes: {e}"}), 500

@vacants_bp.route("/<int:vacant_id>", methods=["GET"])
def get_vacant_details_route(vacant_id: int):
    try:
        details = vacant_service.get_vacant_details(vacant_id)
        return jsonify(details), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener detalles de la vacante: {e}"}), 500

@vacants_bp.route("/<int:vacant_id>/apply", methods=["POST"])
@jwt_required()
def apply_to_vacant_route(vacant_id: int):
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.apply_to_vacant(vacant_id, current_user_email)
        return jsonify(result), 201
    except ValueError as e:
        # 403 para denegado, 404 para no encontrada, 409 para ya postuló
        if "Acceso denegado" in str(e):
            return jsonify({"error": str(e)}), 403
        elif "Vacante no encontrada" in str(e):
            return jsonify({"error": str(e)}), 404
        elif "Ya has postulado" in str(e):
            return jsonify({"error": str(e)}), 409
        else:
            return jsonify({"error": str(e)}), 400 # Otros errores de validación
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al postular: {e}"}), 500

@vacants_bp.route("/check_status/<int:vacant_id>", methods=["GET"])
@jwt_required()
def check_application_status_route(vacant_id: int):
    current_user_email = get_jwt_identity()
    try:
        status = vacant_service.check_application_status(vacant_id, current_user_email)
        return jsonify(status), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403 # Acceso denegado
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al verificar estado de postulación: {e}"}), 500

@vacants_bp.route("/", methods=["POST"])
@jwt_required()
def create_vacant_route():
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
        return jsonify({"error": f"Error inesperado al crear vacante: {e}"}), 500

# Endpoint para listar mis vacantes
@vacants_bp.route("/my", methods=["GET"])
@jwt_required()
def list_my_vacants_route():
    current_user_email = get_jwt_identity()
    try:
        vacants = vacant_service.list_my_vacants(current_user_email)
        return jsonify(vacants), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403 # Solo instituciones pueden ver sus vacantes
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al listar mis vacantes: {e}"}), 500

# Actualizar una vacante
@vacants_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_vacant_route(id: int):
    current_user_email = get_jwt_identity()
    data = request.get_json()
    try:
        result = vacant_service.update_vacant(id, current_user_email, data)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else: # Vacante no encontrada o fechas mal formateadas
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al actualizar vacante: {e}"}), 500

# Eliminar vacante
@vacants_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_vacant_route(id: int):
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.delete_vacant(id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else: # Vacante no encontrada
            return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al eliminar vacante: {e}"}), 500

# Activar o desactivar vacante
@vacants_bp.route("/<int:id>/status", methods=["PATCH"])
@jwt_required()
def toggle_vacant_status_route(id: int):
    current_user_email = get_jwt_identity()
    new_status = request.get_json().get("status")
    try:
        result = vacant_service.toggle_vacant_status(id, current_user_email, new_status)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else: # Vacante no encontrada o estado inválido
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al cambiar estado de vacante: {e}"}), 500

# Publicar borrador
@vacants_bp.route("/<int:id>/publish", methods=["PATCH"])
@jwt_required()
def publish_vacant_route(id: int):
    current_user_email = get_jwt_identity()
    try:
        result = vacant_service.publish_vacant(id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else: # Vacante no encontrada
            return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al publicar vacante: {e}"}), 500

@vacants_bp.route("/<int:id>/applications", methods=["GET"])
@jwt_required()
def get_applications_for_vacant_route(id: int):
    current_user_email = get_jwt_identity()
    try:
        applications_data = vacant_service.get_applications_for_vacant(id, current_user_email)
        return jsonify(applications_data), 200
    except ValueError as e:
        if "no tienes permiso" in str(e):
            return jsonify({"error": str(e)}), 403
        else: # Vacante no encontrada
            return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al obtener postulaciones: {e}"}), 500

@vacants_bp.route("/<int:application_id>/decision", methods=["PATCH"])
@jwt_required()
def decide_application_route(application_id: int):
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
        else: # Decisión inválida
            return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado al decidir sobre postulación: {e}"}), 500

@vacants_bp.route("/map", methods=["GET"])
@jwt_required(optional=True)
def vacants_for_map_route():
    try:
        vacants = vacant_service.get_vacants_for_map()
        return jsonify([v.to_dict() for v in vacants]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener vacantes para el mapa: {e}"}), 500