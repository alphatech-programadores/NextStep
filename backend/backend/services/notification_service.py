# services/notification_service.py
from extensions import db, mail # Si planeas enviar notificaciones por correo también
from repositories.notification_repository import NotificationRepository
from repositories.user_repository import UserRepository # Para verificar existencia de usuarios
from flask import current_app # Para generar links absolutos
from flask_mail import Message

class NotificationService:
    def __init__(self):
        self.notification_repo = NotificationRepository(db.session)
        self.user_repo = UserRepository(db.session)

    def create_and_send_notification(
        self,
        recipient_email: str,
        type: str,
        message: str,
        link: str = None,
        related_id: int = None,
        sender_email: str = None,
        send_email_too: bool = False # Opcional: para enviar por correo además de guardar en BD
    ):
        # Opcional: Verificar que el usuario receptor exista
        # recipient_user = self.user_repo.get_by_email(recipient_email)
        # if not recipient_user:
        #     current_app.logger.warning(f"Intento de enviar notificación a email no existente: {recipient_email}")
        #     return None # No se envía si el usuario no existe

        try:
            notification = self.notification_repo.create_notification(
                recipient_email=recipient_email,
                type=type,
                message=message,
                link=link,
                related_id=related_id,
                sender_email=sender_email
            )
            db.session.add(notification) # Asegura que la notificación está en la sesión
            db.session.commit()

            # Lógica para enviar correo electrónico (si send_email_too es True)
            if send_email_too:
                recipient_user = self.user_repo.get_by_email(recipient_email)
                if recipient_user:
                    msg = Message(
                        subject=f"NextStep: Notificación - {type.replace('_', ' ').title()}",
                        sender=current_app.config["MAIL_DEFAULT_SENDER"],
                        recipients=[recipient_email]
                    )
                    email_body = f"Hola {recipient_user.name},\n\n{message}"
                    if link:
                        email_body += f"\n\nPuedes ver los detalles aquí: {current_app.config['BASE_URL']}{link}"
                    msg.body = email_body
                    mail.send(msg)
                else:
                    current_app.logger.warning(f"No se pudo enviar correo a {recipient_email}: Usuario no encontrado.")

            return notification.to_dict()

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear/enviar notificación: {e}")
            raise RuntimeError(f"Error interno del sistema de notificaciones: {e}")

    def get_user_notifications(self, recipient_email: str, page: int, per_page: int, unread_only: bool = False):
        paginated_notifications = self.notification_repo.get_notifications_by_recipient(recipient_email, page, per_page, unread_only)
        
        notifications_list = [n.to_dict() for n in paginated_notifications.items]
        
        return {
            "notifications": notifications_list,
            "total_pages": paginated_notifications.pages,
            "current_page": paginated_notifications.page,
            "total_items": paginated_notifications.total
        }

    def mark_notification_as_read(self, notification_id: int, recipient_email: str):
        notification = self.notification_repo.get_notification_by_id(notification_id)
        if not notification:
            raise ValueError("Notificación no encontrada.")
        if notification.recipient_email != recipient_email:
            raise ValueError("No tienes permiso para marcar esta notificación como leída.")
        if notification.is_read:
            return {"message": "Notificación ya marcada como leída."}

        try:
            self.notification_repo.mark_as_read(notification)
            db.session.commit()
            return {"message": "Notificación marcada como leída."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al marcar notificación como leída: {e}")

    def mark_all_notifications_as_read(self, recipient_email: str):
        try:
            self.notification_repo.mark_all_as_read(recipient_email)
            db.session.commit()
            return {"message": "Todas las notificaciones marcadas como leídas."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al marcar todas las notificaciones como leídas: {e}")

    def delete_notification(self, notification_id: int, recipient_email: str):
        notification = self.notification_repo.get_notification_by_id(notification_id)
        if not notification:
            raise ValueError("Notificación no encontrada.")
        if notification.recipient_email != recipient_email:
            raise ValueError("No tienes permiso para eliminar esta notificación.")
        
        try:
            self.notification_repo.delete_notification(notification)
            db.session.commit()
            return {"message": "Notificación eliminada correctamente."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al eliminar notificación: {e}")

    def get_unread_notifications_count(self, recipient_email: str) -> int:
        return self.notification_repo.get_unread_count(recipient_email)