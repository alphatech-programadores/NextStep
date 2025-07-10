# services/saved_vacancies_service.py
from extensions import db
from repositories.saved_vacancy_repository import SavedVacancyRepository
from repositories.user_repository import UserRepository # Para verificar si el usuario existe
from repositories.vacant_repository import VacantRepository # Para verificar si la vacante existe
from models.saved_vacancy import SavedVacancy # Para tipos de retorno

class SavedVacanciesService:
    def __init__(self):
        self.saved_vacancy_repo = SavedVacancyRepository(db.session)
        self.user_repo = UserRepository(db.session)
        self.vacant_repo = VacantRepository(db.session)

    def toggle_save_vacancy(self, student_email: str, vacant_id: int) -> dict:
        """
        Guarda una vacante si no está guardada, o la elimina si ya lo está.
        Retorna un mensaje indicando la acción realizada.
        """
        user = self.user_repo.get_by_email(student_email)
        if not user or user.role.name != 'student':
            raise ValueError("Usuario no encontrado o no es un estudiante válido.")
        
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")

        existing_entry = self.saved_vacancy_repo.get_saved_vacancy(student_email, vacant_id)

        try:
            if existing_entry:
                self.saved_vacancy_repo.delete_saved_vacancy(existing_entry)
                db.session.commit()
                return {"message": "Vacante eliminada de tus guardados.", "action": "removed"}
            else:
                self.saved_vacancy_repo.create_saved_vacancy(student_email, vacant_id)
                db.session.commit()
                return {"message": "Vacante guardada exitosamente.", "action": "added"}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al guardar/eliminar vacante: {e}")

    def get_user_saved_vacancies(self, student_email: str) -> list[dict]:
        """
        Obtiene todas las vacantes guardadas por un estudiante.
        Retorna una lista de diccionarios con detalles de la vacante.
        """
        user = self.user_repo.get_by_email(student_email)
        if not user or user.role.name != 'student':
            raise ValueError("Usuario no encontrado o no es un estudiante válido.")

        try:
            saved_entries = self.saved_vacancy_repo.get_all_saved_vacancies_by_student(student_email)
            # El to_dict de SavedVacancy ya incluye los detalles de la vacante gracias al joinedload
            return [entry.to_dict() for entry in saved_entries]
        except Exception as e:
            db.session.rollback() # No debería necesitar rollback si es solo lectura, pero por seguridad
            raise RuntimeError(f"Error al obtener vacantes guardadas: {e}")
            
    def is_vacant_saved(self, student_email: str, vacant_id: int) -> bool:
        """Verifica si una vacante específica ya ha sido guardada por el estudiante."""
        user = self.user_repo.get_by_email(student_email)
        if not user or user.role.name != 'student':
            raise ValueError("Usuario no encontrado o no es un estudiante válido.")
        
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant: # La vacante debe existir para ser guardada
            raise ValueError("Vacante no encontrada.")

        try:
            return self.saved_vacancy_repo.is_vacant_saved_by_student(student_email, vacant_id)
        except Exception as e:
            raise RuntimeError(f"Error al verificar si la vacante está guardada: {e}")