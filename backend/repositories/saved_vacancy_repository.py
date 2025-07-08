# repositories/saved_vacancy_repository.py
from extensions import db
from models.saved_vacancy import SavedVacancy
from models.vacant import Vacant
from sqlalchemy.orm import joinedload # Importar joinedload
from datetime import datetime

class SavedVacancyRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_saved_vacancy(self, student_email: str, vacant_id: int) -> SavedVacancy:
        saved_entry = SavedVacancy(student_email=student_email, vacant_id=vacant_id)
        self.db_session.add(saved_entry)
        return saved_entry

    def get_saved_vacancy(self, student_email: str, vacant_id: int) -> SavedVacancy | None:
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email, vacant_id=vacant_id
        ).first()

    # --- CAMBIO CLAVE AQUÍ: joinedload para Vacant y Vacant.institution_profile ---
    def get_all_saved_vacancies_by_student(self, student_email: str) -> list[SavedVacancy]:
        return self.db_session.query(SavedVacancy)\
            .filter_by(student_email=student_email)\
            .options(
                joinedload(SavedVacancy.vacant).joinedload(Vacant.institution_profile) # Carga la vacante y su perfil de institución
            )\
            .order_by(SavedVacancy.saved_at.desc())\
            .all()
    # ---------------------------------------------------------------------------------

    def delete_saved_vacancy(self, saved_entry: SavedVacancy):
        self.db_session.delete(saved_entry)

    def is_vacant_saved_by_student(self, student_email: str, vacant_id: int) -> bool:
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email, vacant_id=vacant_id
        ).count() > 0

    def get_saved_vacancies_count_by_student(self, student_email: str) -> int:
        return self.db_session.query(SavedVacancy).filter_by(
            student_email=student_email
        ).count()