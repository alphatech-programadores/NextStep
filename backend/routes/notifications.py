# routes/notification_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import NotificationService
from extensions import db # Para asegurar la sesión de la base de datos
from flask import current_app # Necesario para logging si lo tienes en el servicio

notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

notification_service = NotificationService()

# --- RUTA PARA OBTENER TODAS LAS NOTIFICACIONES DEL USUARIO ---
# CAMBIO AQUÍ: La ruta es '' en lugar de '/' para coincidir con la solicitud sin trailing slash
@notification_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    current_user_email = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'

    try:
        notifications_data = notification_service.get_user_notifications(
            recipient_email=current_user_email,
            page=page,
            per_page=per_page,
            unread_only=unread_only
        )
        return jsonify(notifications_data), 200
    except ValueError as e:
        current_app.logger.error(f"Error de valor al obtener notificaciones para {current_user_email}: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al obtener notificaciones para {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al obtener notificaciones."}), 500

# --- RUTA PARA OBTENER EL CONTEO DE NOTIFICACIONES NO LEÍDAS ---
@notification_bp.route("/unread_count", methods=["GET"])
@jwt_required()
def get_unread_count():
    current_user_email = get_jwt_identity()
    try:
        count = notification_service.get_unread_notifications_count(current_user_email)
        return jsonify({"unread_count": count}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al obtener conteo de no leídas para {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al obtener el conteo de notificaciones no leídas."}), 500

# --- RUTA PARA MARCAR UNA NOTIFICACIÓN ESPECÍFICA COMO LEÍDA ---
@notification_bp.route("/<int:notification_id>/mark_read", methods=["PUT"])
@jwt_required()
def mark_notification_read(notification_id):
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.mark_notification_as_read(notification_id, current_user_email)
        db.session.commit()
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f"Error de valor al marcar notificación {notification_id} como leída para {current_user_email}: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al marcar notificación {notification_id} como leída para {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al marcar la notificación como leída."}), 500

# --- RUTA PARA MARCAR TODAS LAS NOTIFICACIONES COMO LEÍDAS ---
@notification_bp.route("/mark_all_read", methods=["PUT"])
@jwt_required()
def mark_all_notifications_read():
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.mark_all_notifications_as_read(current_user_email)
        db.session.commit()
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f"Error de valor al marcar todas las notificaciones como leídas para {current_user_email}: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al marcar todas las notificaciones como leídas para {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al marcar todas las notificaciones como leídas."}), 500

# --- RUTA PARA ELIMINAR UNA NOTIFICACIÓN ---
@notification_bp.route("/<int:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id):
    current_user_email = get_jwt_identity()
    try:
        result = notification_service.delete_notification(notification_id, current_user_email)
        db.session.commit()
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f"Error de valor al eliminar notificación {notification_id} para {current_user_email}: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inesperado al eliminar notificación {notification_id} para {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al eliminar la notificación."}), 500