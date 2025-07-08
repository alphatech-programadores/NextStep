# repositories/application_repository.py
from datetime import datetime
from sqlalchemy.orm import joinedload
from extensions import db
from models.application import Application
from models.vacant import Vacant
from models.user import User
from models.student_profile import StudentProfile
from collections import Counter


class ApplicationRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_application_by_id(self, app_id: int) -> Application | None:
        return self.db_session.query(Application).get(app_id)

    def get_application_by_student_and_vacant(self, student_email: str, vacant_id: int) -> Application | None:
        return self.db_session.query(Application).filter_by(
            student_email=student_email, vacant_id=vacant_id
        ).first()

    def create_application(self, student_email: str, vacant_id: int, status: str = "pendiente") -> Application:
        app = Application(
            student_email=student_email,
            vacant_id=vacant_id,
            created_at=datetime.utcnow(),
            status=status
        )
        self.db_session.add(app)
        return app

    def get_accepted_application_by_student(self, student_email: str) -> Application | None:
        return self.db_session.query(Application).filter_by(
            student_email=student_email, status="aceptado"
        ).first()

    def get_applications_with_student_profiles_by_vacant(self, vacant_id: int) -> list[Application]:
        return self.db_session.query(Application).options(
            joinedload(Application.student).joinedload(User.student_profile)
        ).filter_by(vacant_id=vacant_id).order_by(Application.created_at.desc()).all()

    def count_applications_for_vacant(self, vacant_id: int) -> int:
        return self.db_session.query(Application).filter_by(vacant_id=vacant_id).count()

    def get_accepted_application_for_vacant(self, vacant_id: int) -> Application | None:
        return self.db_session.query(Application).filter_by(vacant_id=vacant_id, status="aceptado").first()

    def update_application_status(self, app: Application, new_status: str, feedback: str | None = None) -> Application:
        app.status = new_status
        if feedback is not None: # Solo si el modelo Application tiene campo feedback
            if hasattr(app, 'feedback'):
                app.feedback = feedback
        self.db_session.add(app)
        return app

    def get_paginated_applications_by_student(self, student_email: str, status_filter: str | None, page: int, per_page: int):
        query = self.db_session.query(Application).options(
            joinedload(Application.vacant).joinedload(Vacant.institution_profile) # <-- ¡Asegura que estas cargas estén aquí!
        ).filter(Application.student_email == student_email)

        if status_filter:
            query = query.filter(Application.status == status_filter)

        query = query.order_by(Application.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_application_status_counts(self, student_email: str) -> dict:
        all_user_applications = self.db_session.query(Application).filter_by(student_email=student_email).all()
        status_counts = Counter(app.status for app in all_user_applications) # Esta línea ahora funcionará
        return {
            'total': len(all_user_applications),
            'pending': status_counts.get('pendiente', 0),
            'interview': status_counts.get('entrevista', 0),
            'accepted': status_counts.get('aceptado', 0)
        }