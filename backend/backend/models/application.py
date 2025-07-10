# models/application.py
from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String, db.ForeignKey('users.email'), nullable=False)
    vacant_id = db.Column(db.Integer, db.ForeignKey('vacants.id'), nullable=False)
    # Cambié application_date por created_at para coincidir con tu uso en el servicio
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Si created_at es nullable=True, podría ser None
    status = db.Column(db.String(50), default='pendiente', nullable=False)
    
    # Relaciones
    student = db.relationship('User', back_populates='applications')
    vacant = db.relationship('Vacant', back_populates='applications')

    def to_dict(self):
        return {
            "id": self.id,
            "student_email": self.student_email,
            "vacant_id": self.vacant_id,
            # Maneja created_at/application_date que podría ser None
            "applied_at": self.created_at.isoformat() if self.created_at else None, # Usa isoformat o strftime
            "status": self.status,
            "vacant_title": self.vacant.area if self.vacant else None, # Asegura que vacant no sea None
            "company_name": self.vacant.institution_profile.institution_name if self.vacant and self.vacant.institution_profile else "N/A"
        }