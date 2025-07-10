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


class ApplicationService:
    def __init__(self):
        self.application_repo = ApplicationRepository(db.session)
        self.user_repo = UserRepository(db.session)

    def get_my_applications(self, current_user_email: str, status_filter: str | None, page: int, per_page: int):
        user = self.user_repo.get_by_email(current_user_email)
        if not user or user.role.name != 'student':
            raise ValueError("Acceso denegado. Solo estudiantes pueden ver sus postulaciones.")

        stats = self.application_repo.get_application_status_counts(user.email)

        paginated_applications = self.application_repo.get_paginated_applications_by_student(
            user.email, status_filter, page, per_page
        )

        applications_list = [{
            "id": app.id,
            **app.to_dict(),
        } for app in paginated_applications.items]

        return {
            "stats": stats,
            "applications": applications_list,
            "total_pages": paginated_applications.pages,
            "current_page": paginated_applications.page,
            "total_items": paginated_applications.total
        }

    def decide_application(self, user_email: str, application_id: int, new_status: str, feedback: str | None = None):
        user = self.user_repo.get_by_email(user_email)
        if not user or user.role.name != "institution":
            raise ValueError("Solo instituciones pueden tomar decisiones sobre postulaciones.")

        app = self.application_repo.get_application_by_id(application_id)
        if not app:
            raise ValueError("La postulación no existe.")

        if app.vacant.institution_profile.user_email != user.email:
            raise ValueError("No tienes permiso para modificar esta postulación.")

        if new_status == "aceptado":
            accepted = self.application_repo.get_accepted_application_for_vacant(app.vacant_id)
            if accepted and accepted.id != application_id:
                raise ValueError("Ya hay una postulación aceptada para esta vacante.")

        updated_app = self.application_repo.update_application_status(app, new_status, feedback)
        db.session.commit()

        return updated_app.to_dict()

    def get_applications_by_vacant(self, vacant_id: int) -> list[dict]:
        apps = self.application_repo.get_applications_with_student_profiles_by_vacant(vacant_id)
        result = []

        for app in apps:
            student = app.student
            student_profile = student.student_profile if student else None

            result.append({
                "application_id": app.id,
                "status": app.status,
                "submitted_at": app.created_at.isoformat() if app.created_at else None,
                "student": {
                    "name": getattr(student_profile, "full_name", None) or student.email,
                    "email": student.email,
                    "career": getattr(student_profile, "career", "N/A"),
                    "semester": getattr(student_profile, "semester", "N/A"),
                    "skills": student_profile.skills.split(",") if student_profile and student_profile.skills else [],
                    "cv_url": getattr(student_profile, "cv_url", None),
                }
            })

        return result


    def cancel_application(self, user_email: str, application_id: int):
            app = self.application_repo.get_application_by_id(application_id)
            if not app:
                raise ValueError("La postulación no existe.")

            # Ensure the student is the owner of the application
            if app.student_email != user_email:
                raise ValueError("No tienes permiso para cancelar esta postulación.")

            # Prevent cancellation if already accepted/rejected (or any other final status)
            if app.status in ["aceptado", "rechazado", "cancelada"]:
                raise ValueError(f"No se puede cancelar una postulación con estado '{app.status}'.")

            # Update the application status to 'cancelada'
            updated_app = self.application_repo.update_application_status(app, "cancelada", "Cancelada por el estudiante")
            db.session.commit()
            return updated_app.to_dict()
