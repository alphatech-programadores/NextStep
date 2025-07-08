from extensions import db
from datetime import datetime

class Vacant(db.Model):
    __tablename__ = 'vacants'

    id = db.Column(db.Integer, primary_key=True)
    institution_email = db.Column(db.String, db.ForeignKey("institution_profiles.email"), nullable=False)
    area = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    hours = db.Column(db.String, nullable=True)
    modality = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String, nullable=True)
    tags = db.Column(db.String(20), default="")
    status = db.Column(db.String(20), default='activa')
    is_draft = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Permite hacer `vacant.applications`
    applications = db.relationship("Application", back_populates="vacant", cascade="all, delete-orphan")

    # Permite hacer `vacant.institution_profile`
    institution_profile = db.relationship("InstitutionProfile", back_populates="vacants")

    # <--- ¡EL MÉTODO to_dict DEBE ESTAR INDENTADO DENTRO DE LA CLASE! ---
    def to_dict(self):
        return {
            "id": self.id,
            "institution_email": self.institution_email,
            "area": self.area,
            "description": self.description,
            "requirements": self.requirements,
            "hours": self.hours,
            "modality": self.modality,
            "location": self.location,
            "tags": self.tags.split(',') if self.tags else [],
            "status": self.status,
            "is_draft": self.is_draft,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "start_date": self.start_date.isoformat() if self.start_date else None, # Añadir fechas
            "end_date": self.end_date.isoformat() if self.end_date else None,       # Añadir fechas
            "latitude": self.latitude,   # Añadir latitud
            "longitude": self.longitude  # Añadir longitud
        }