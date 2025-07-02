# repositories/saved_vacancy_repository.py
from extensions import db
from models.saved_vacancy import SavedVacancy
from models.vacant import Vacant # Importar Vacant para poder unirse en consultas
from datetime import datetime
from sqlalchemy.orm import joinedload # Para eager loading en consultas

class SavedVacancyRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_saved_vacancy(self, student_email: str, vacant_id: int) -> SavedVacancy:
        """Crea y guarda una nueva entrada de vacante guardada."""
        saved_entry = SavedVacancy(student_email=student_email, vacant_id=vacant_id)
        self.db_session.add(saved_entry)
        # El commit se hará en el servicio
        return saved_entry

    def get_saved_vacancy(self, student_email: str, vacant_id: int) -> SavedVacancy | None:
        """Obtiene una entrada de vacante guardada específica."""
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email, vacant_id=vacant_id
        ).first()

    def get_all_saved_vacancies_by_student(self, student_email: str) -> list[SavedVacancy]:
        """Obtiene todas las vacantes guardadas por un estudiante, con detalles de la vacante."""
        return self.db_session.query(SavedVacancy)\
            .filter_by(student_email=student_email)\
            .options(joinedload(SavedVacancy.vacant))\
            .order_by(SavedVacancy.saved_at.desc())\
            .all()

    def delete_saved_vacancy(self, saved_entry: SavedVacancy):
        """Elimina una entrada de vacante guardada."""
        self.db_session.delete(saved_entry)
        # El commit se hará en el servicio

    def is_vacant_saved_by_student(self, student_email: str, vacant_id: int) -> bool:
        """Verifica si una vacante específica ya ha sido guardada por un estudiante."""
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email, vacant_id=vacant_id
        ).count() > 0

    def get_saved_vacancies_count_by_student(self, student_email: str) -> int:
        """Obtiene el número total de vacantes guardadas por un estudiante."""
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email
        ).count()