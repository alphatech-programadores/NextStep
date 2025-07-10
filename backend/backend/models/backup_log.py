# models/backup_log.py
from extensions import db
from datetime import datetime

class BackupLog(db.Model):
    __tablename__ = 'backup_log'

    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(10), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    record_id = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=True)  # Se puede usar get_jwt_identity()
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
