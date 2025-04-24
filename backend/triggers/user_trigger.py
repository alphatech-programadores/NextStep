from models.user import User
from models.backup_log import BackupLog
from extensions import db
from sqlalchemy import event

@event.listens_for(User, 'after_insert')
def backup_user_insert(mapper, connection, target):
    connection.execute(
        db.insert(BackupLog).values(
            table='users',
            operation='INSERT',
            record_id=target.email,
            user='system'  # Puedes poner aquí get_jwt_identity() si lo capturas
        )
    )

@event.listens_for(User, 'after_update')
def backup_user_update(mapper, connection, target):
    connection.execute(
        db.insert(BackupLog).values(
            table='users',
            operation='UPDATE',
            record_id=target.email,
            user='system'
        )
    )

@event.listens_for(User, 'after_delete')
def backup_user_delete(mapper, connection, target):
    connection.execute(
        db.insert(BackupLog).values(
            table='users',
            operation='DELETE',
            record_id=target.email,
            user='system'
        )
    )
