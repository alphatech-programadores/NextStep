# repositories/student_profile_repository.py
from models.student_profile import StudentProfile
from extensions import db

class StudentProfileRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_profile(self, email: str) -> StudentProfile:
        profile = StudentProfile(email=email)
        self.db_session.add(profile)
        return profile

    def get_by_email(self, email: str) -> StudentProfile | None:
        return self.db_session.query(StudentProfile).filter_by(email=email).first()

    def update_profile(self, profile: StudentProfile, data: dict) -> StudentProfile: # <--- ¡ESTE MÉTODO DEBE ESTAR AQUÍ!
        """
        Actualiza los atributos de un perfil de estudiante existente.
        Los campos no especificados en 'data' no se modifican.
        """
        for key, value in data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        self.db_session.add(profile)
        return profile

    def delete_profile(self, profile: StudentProfile):
        """Elimina un perfil de estudiante."""
        self.db_session.delete(profile)