# models/saved_vacancy.py
from extensions import db
from datetime import datetime

class SavedVacancy(db.Model):
    __tablename__ = 'saved_vacancies'

    # Clave primaria compuesta para asegurar que un estudiante no guarde la misma vacante múltiples veces
    student_email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True, nullable=False)
    vacant_id = db.Column(db.Integer, db.ForeignKey('vacants.id'), primary_key=True, nullable=False)
    
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones:
    # Relación con el usuario (estudiante que guarda la vacante)
    student = db.relationship('User', backref=db.backref('saved_vacancies_entries', lazy=True))
    # Relación con la vacante guardada
    vacant = db.relationship('Vacant', backref=db.backref('saved_by_students', lazy=True))

    def __repr__(self):
        return f"<SavedVacancy Student: {self.student_email}, Vacant: {self.vacant_id}>"

    def to_dict(self):
        # Cuando convertimos a dict, podemos incluir detalles de la vacante si se cargó
        vacant_data = self.vacant.to_dict() if self.vacant else None
        
        # Opcional: limpiar campos no necesarios si la vacante es muy grande
        if vacant_data:
            # Ejemplo: eliminar la descripción larga si no se necesita en la vista guardada
            vacant_data.pop('description', None) 
            vacant_data.pop('requirements', None)

        return {
            "student_email": self.student_email,
            "vacant_id": self.vacant_id,
            "saved_at": self.saved_at.isoformat(),
            "vacant_details": vacant_data # Incluir detalles de la vacante
        }