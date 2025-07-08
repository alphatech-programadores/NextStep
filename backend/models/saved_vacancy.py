# models/saved_vacancy.py
from extensions import db
from datetime import datetime

class SavedVacancy(db.Model):
    __tablename__ = 'saved_vacancies'

    student_email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True, nullable=False)
    vacant_id = db.Column(db.Integer, db.ForeignKey('vacants.id'), primary_key=True, nullable=False)
    
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones:
    student = db.relationship('User', backref=db.backref('saved_vacancies_entries', lazy=True))
    vacant = db.relationship('Vacant', backref=db.backref('saved_by_students', lazy=True)) # La relación Vacant.institution_profile se cargará a través de Vacant

    def __repr__(self):
        return f"<SavedVacancy Student: {self.student_email}, Vacant: {self.vacant_id}>"

    def to_dict(self):
        vacant_data = None
        if self.vacant:
            vacant_data = self.vacant.to_dict()
            # Añadir company_name desde la relación institution_profile de la vacante
            if self.vacant.institution_profile: # Asegurarse de que la relación se ha cargado (joinedload)
                vacant_data['company_name'] = self.vacant.institution_profile.institution_name
            else:
                vacant_data['company_name'] = "Institución Desconocida"
            
            # Opcional: limpiar campos no necesarios si la vacante es muy grande
            vacant_data.pop('requirements', None) # Asumiendo que no necesitas requisitos aquí
            vacant_data.pop('is_draft', None)
            vacant_data.pop('last_modified', None)
            vacant_data.pop('latitude', None)
            vacant_data.pop('longitude', None)


        return {
            "student_email": self.student_email,
            "vacant_id": self.vacant_id,
            "saved_at": self.saved_at.isoformat(),
            "vacant_details": vacant_data
        }