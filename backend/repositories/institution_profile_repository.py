# repositories/institution_profile_repository.py
from models.institution_profile import InstitutionProfile
from extensions import db

class InstitutionProfileRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_profile(self, email: str) -> InstitutionProfile:
        profile = InstitutionProfile(email=email)
        self.db_session.add(profile)
        return profile
    
    def get_by_email(self, email: str) -> InstitutionProfile | None:
        return self.db_session.query(InstitutionProfile).filter_by(email=email).first()

    def update_profile(self, profile: InstitutionProfile, data: dict) -> InstitutionProfile:
        """
        Actualiza los atributos de un perfil de institución existente.
        Los campos no especificados en 'data' no se modifican.
        """
        for key, value in data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        self.db_session.add(profile) # Asegura que el objeto esté en la sesión para el tracking de cambios
        return profile

    def delete_profile(self, profile: InstitutionProfile):
        """Elimina un perfil de institución."""
        self.db_session.delete(profile)

    # Puedes añadir otros métodos específicos si los necesitas, por ejemplo:
    # def get_all_institution_profiles(self) -> list[InstitutionProfile]:
    #     return self.db_session.query(InstitutionProfile).all()