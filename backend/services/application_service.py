# services/application_service.py
from collections import Counter
from sqlalchemy.orm import joinedload
from extensions import db
from models.application import Application
from models.vacant import Vacant
from models.user import User
from models.institution_profile import InstitutionProfile

# Repositorios
from repositories.application_repository import ApplicationRepository
from repositories.user_repository import UserRepository # Asegúrate de que esto esté importado
# from repositories.vacant_repository import VacantRepository # No es necesario para este error, pero podrías necesitarlo
# from repositories.institution_profile_repository import InstitutionProfileRepository # No es necesario para este error, pero podrías necesitarlo

class ApplicationService:
    def __init__(self):
        self.application_repo = ApplicationRepository(db.session)
        self.user_repo = UserRepository(db.session) # <-- ¡AÑADE ESTA LÍNEA!
        # Puedes añadir otros repositorios si el servicio los necesita
        # self.vacant_repo = VacantRepository(db.session)
        # self.institution_profile_repo = InstitutionProfileRepository(db.session)

    def get_my_applications(self, current_user_email: str, status_filter: str | None, page: int, per_page: int):
        user = self.user_repo.get_by_email(current_user_email) # Esta línea ahora funcionará
        if not user or user.role.name != 'student':
            raise ValueError("Acceso denegado. Solo estudiantes pueden ver sus postulaciones.")

        stats = self.application_repo.get_application_status_counts(user.email)
        
        paginated_applications = self.application_repo.get_paginated_applications_by_student(
            user.email, status_filter, page, per_page
        )

        applications_list = [{
            "id": app.id,
            **app.to_dict(), # Usamos ** para desempaquetar el diccionario de to_dict()
        } for app in paginated_applications.items]

        return {
            "stats": stats,
            "applications": applications_list,
            "total_pages": paginated_applications.pages,
            "current_page": paginated_applications.page,
            "total_items": paginated_applications.total
        }