# routes/notifications.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

notification_service = NotificationService()

@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_notifications_route():
    current_user_email = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    unread_only = request.args.get("unread_only", "false").lower() == "true" # Query param para solo no leídas

    try:
        notifications_data = notification_service.get_user_notifications(current_user_email, page, per_page, unread_only)
        return jsonify(notifications_data), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener notificaciones: {e}"}), 500

@notifications_bp.route("/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_notification_as_read_route(notification_id: int):
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.mark_notification_as_read(notification_id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al marcar notificación como leída: {e}"}), 500

@notifications_bp.route("/mark-all-read", methods=["PATCH"])
@jwt_required()
def mark_all_notifications_as_read_route():
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.mark_all_notifications_as_read(current_user_email)
        return jsonify(result), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al marcar todas las notificaciones como leídas: {e}"}), 500

@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification_route(notification_id: int):
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.delete_notification(notification_id, current_user_email)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al eliminar notificación: {e}"}), 500

@notifications_bp.route("/count", methods=["GET"])
@jwt_required()
def get_unread_notifications_count_route():
    current_user_email = get_jwt_identity()
    try:
        count = notification_service.get_unread_notifications_count(current_user_email)
        return jsonify({"count": count}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error al obtener el conteo de notificaciones no leídas: {e}"}), 500