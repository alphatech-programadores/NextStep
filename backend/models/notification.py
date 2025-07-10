# models/notification.py
from extensions import db
from datetime import datetime
# REMOVED: from services.notification_service import NotificationService # This causes the circular import

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    sender_email = db.Column(db.String(120), nullable=True) # Quién generó la notificación (ej. institución, sistema)
    
    # Tipo de notificación (ej. 'application_status_change', 'new_vacant_match', 'account_deleted_vacant_cancelled')
    type = db.Column(db.String(100), nullable=False)
    
    # Mensaje corto para mostrar directamente
    message = db.Column(db.String(500), nullable=False)
    
    # URL a la que se debe redirigir al usuario al hacer clic en la notificación (ej. /dashboard/applications/123)
    link = db.Column(db.String(500), nullable=True)
    
    # ID de la entidad relacionada (ej. ID de la postulación, ID de la vacante)
    related_id = db.Column(db.Integer, nullable=True)
    
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relación inversa con el usuario receptor
    # NOTE: Ensure that in User model, you have notifications = db.relationship('Notification', back_populates='recipient')
    # Or adjust this to 'user' if User model has 'notifications = db.relationship('Notification', back_populates='user')'
    # Based on previous conversation, it should be 'user'
    user = db.relationship('User', back_populates='notifications') # Changed from 'recipient' to 'user' to match User model

    def to_dict(self):
        return {
            "id": self.id,
            "recipient_email": self.recipient_email,
            "sender_email": self.sender_email,
            "type": self.type,
            "message": self.message,
            "link": self.link,
            "related_id": self.related_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
