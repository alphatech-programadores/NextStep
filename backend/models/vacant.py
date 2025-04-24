from extensions import db
from datetime import datetime

class Vacant(db.Model):
    __tablename__ = 'vacants'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    hours = db.Column(db.String, nullable=True)
    modality = db.Column(db.String, nullable=True)  # presencial, híbrido, remoto
    requirements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String, default='activa')  # activa / inactiva
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    # Campos nuevos:
    location = db.Column(db.String, nullable=True)  # ej. "CDMX", "Querétaro"
    tags = db.Column(db.String, default="")  # Coma-separados: "Python,Full-time,Remoto"
    is_draft = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    institution_email = db.Column(db.String, db.ForeignKey("institution_profiles.email"), nullable=False)
