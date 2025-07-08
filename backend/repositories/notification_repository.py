# repositories/notification_repository.py
from extensions import db
from models.notification import Notification
from datetime import datetime

class NotificationRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_notification(
        self,
        recipient_email: str,
        type: str,
        message: str,
        link: str = None,
        related_id: int = None,
        sender_email: str = None
    ) -> Notification:
        notification = Notification(
            recipient_email=recipient_email,
            sender_email=sender_email,
            type=type,
            message=message,
            link=link,
            related_id=related_id,
            is_read=False,
            created_at=datetime.utcnow()
        )
        self.db_session.add(notification)
        return notification

    def get_notifications_by_recipient(self, recipient_email: str, page: int = 1, per_page: int = 10, unread_only: bool = False):
        query = self.db_session.query(Notification).filter_by(recipient_email=recipient_email)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        query = query.order_by(Notification.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_notification_by_id(self, notification_id: int) -> Notification | None:
        return self.db_session.query(Notification).get(notification_id)

    def mark_as_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db_session.add(notification)
        return notification

    def mark_all_as_read(self, recipient_email: str):
        self.db_session.query(Notification).filter_by(recipient_email=recipient_email, is_read=False)\
            .update({"is_read": True}, synchronize_session=False)

    def delete_notification(self, notification: Notification):
        self.db_session.delete(notification)
        
    def get_unread_count(self, recipient_email: str) -> int:
        return self.db_session.query(Notification).filter_by(recipient_email=recipient_email, is_read=False).count()