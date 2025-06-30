# models/institution_profile.py
from extensions import db

class InstitutionProfile(db.Model):
    __tablename__ = 'institution_profiles'

    email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True)
    institution_name = db.Column(db.String(150), nullable=False)
    sector = db.Column(db.String(100))
    contact_person = db.Column(db.String(255), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(510), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
      
    # Relación inversa para conectar de vuelta con el User
    user = db.relationship('User', back_populates='institution_profile')

    # Permite hacer `institution_profile.vacants`
    vacants = db.relationship('Vacant', back_populates='institution_profile', lazy='dynamic')
    
    def to_dict(self):
        return {
            "email": self.email,
            "institution_name": self.institution_name,
            "sector": self.sector,
            "contact_person": getattr(self, "contact_person", ""),
            "contact_phone": getattr(self, "contact_phone", ""),
            "address": getattr(self, "address", ""),
            "description": getattr(self, "description", ""),
            "logo_url": getattr(self, "logo_url", ""),
            "website": getattr(self, "website", "")
        }

