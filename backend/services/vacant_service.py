# services/vacant_service.py
from datetime import datetime, date
from models import vacant
from sqlalchemy.orm import joinedload
from collections import Counter
from extensions import db
from flask import current_app

# Models
from models.vacant import Vacant
from models.user import User
from models.institution_profile import InstitutionProfile
from models.student_profile import StudentProfile
from models.application import Application

# Repositorios
from repositories.user_repository import UserRepository
from repositories.vacant_repository import VacantRepository
from repositories.application_repository import ApplicationRepository
from repositories.institution_profile_repository import InstitutionProfileRepository
from repositories.student_profile_repository import StudentProfileRepository

# Services
from services.notification_service import NotificationService


class VacantService:
    def __init__(self):
        self.user_repo = UserRepository(db.session)
        self.vacant_repo = VacantRepository(db.session)
        self.application_repo = ApplicationRepository(db.session)
        self.institution_profile_repo = InstitutionProfileRepository(db.session)
        self.student_profile_repo = StudentProfileRepository(db.session)
        self.notification_service = NotificationService()


    def get_unique_areas(self):
        return self.vacant_repo.get_unique_areas()

    def get_unique_modalities(self):
        return self.vacant_repo.get_unique_modalities()

    def get_unique_locations(self):
        return self.vacant_repo.get_unique_locations()

    def get_unique_tags(self):
        return self.vacant_repo.get_unique_tags()

    def list_and_search_vacants(self, user_email: str | None, filters: dict, page: int, per_page: int):
        # Si el estudiante ya fue aceptado en una vacante, no mostrarle más
        if user_email:
            user = self.user_repo.get_by_email(user_email)
            if user and user.role.name == "student":
                accepted = self.application_repo.get_accepted_application_by_student(user.email)
                if accepted:
                    return {
                        "vacancies": [],
                        "total_pages": 0,
                        "current_page": 0,
                        "total_items": 0
                    }

        paginated_result = self.vacant_repo.get_paginated_vacants_with_filters(filters, page, per_page)
        vacants_list = []
        for vacant in paginated_result.items:
            vacant_dict = vacant.to_dict()
            # Añadir nombre de la empresa
            institution_profile = self.institution_profile_repo.get_by_email(vacant.institution_email)
            vacant_dict["company_name"] = institution_profile.institution_name if institution_profile else "Desconocido"
            vacants_list.append(vacant_dict)

        return {
            "vacancies": vacants_list,
            "total_pages": paginated_result.pages,
            "current_page": paginated_result.page,
            "total_items": paginated_result.total
        }

    def get_vacant_details(self, vacant_id: int):
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant or vacant.status != 'activa' or vacant.is_draft:
            raise ValueError("Vacante no encontrada o inactiva.")

        institution_profile = self.institution_profile_repo.get_by_email(vacant.institution_email)
        company_name = institution_profile.institution_name if institution_profile else "Desconocido"

        return {
            "id": vacant.id,
            "title": vacant.area, # Usar area como title
            "description": vacant.description,
            "requirements": vacant.requirements,
            "responsibilities": vacant.requirements, # Usar requirements si no tienes responsibilities separadas
            "location": vacant.location,
            "modality": vacant.modality,
            "type": vacant.area, # Usar area como type
            "salary_range": vacant.hours, # Usar hours como salary_range si no hay campo de salario
            "posted_date": vacant.start_date.strftime("%Y-%m-%d") if vacant.start_date else None,
            "application_deadline": vacant.end_date.strftime("%Y-%m-%d") if vacant.end_date else None,
            "company_name": company_name,
            "institution_email": vacant.institution_email,
            "tags": vacant.tags.split(',') if vacant.tags else []
        }

    def apply_to_vacant(self, vacant_id: int, student_email: str):
        user = self.user_repo.get_by_email(student_email)
        if not user or user.role.name != 'student':
            raise ValueError("Acceso denegado. Solo estudiantes pueden postular.")

        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant or vacant.status != 'activa' or vacant.is_draft:
            raise ValueError("Vacante no encontrada o inactiva.")

        existing_application = self.application_repo.get_application_by_student_and_vacant(student_email, vacant_id)
        # Allow re-application if the previous application was cancelled or rejected
        if existing_application and existing_application.status not in ["cancelada", "rechazado"]:
            raise ValueError("Ya tienes una postulación activa o aceptada para esta vacante.")
        
        # If an application exists and is cancelled/rejected, update it instead of creating a new one
        if existing_application and existing_application.status in ["cancelada", "rechazado"]:
            try:
                # Update existing application to 'pendiente'
                updated_app = self.application_repo.update_application_status(
                    existing_application, "pendiente", "Re-postulación"
                )
                db.session.commit()
                return {"message": "Postulación re-enviada exitosamente!", "application_id": updated_app.id}
            except Exception as e:
                db.session.rollback()
                raise RuntimeError(f"Error al re-postular a la vacante: {e}")
        else:
            try:
                new_application = self.application_repo.create_application(
                    student_email=student_email,
                    vacant_id=vacant.id,
                    status="pendiente"
                )
                db.session.commit()
                return {"message": "Postulación enviada exitosamente!", "application_id": new_application.id}
            except Exception as e:
                db.session.rollback()
                raise RuntimeError(f"Error al postular a la vacante: {e}")


    def check_application_status(self, vacant_id: int, student_email: str):
        user = self.user_repo.get_by_email(student_email)
        if not user or user.role.name != 'student':
            raise ValueError("Acceso denegado.")

        application = self.application_repo.get_application_by_student_and_vacant(student_email, vacant_id)
        
        # Return the actual status or None if no application exists
        return {"application_status": application.status if application else None}

    def create_vacant(self, institution_email: str, data: dict):
        user = self.user_repo.get_by_email(institution_email)
        if not user or user.role.name != "institution":
            raise ValueError("Solo instituciones pueden crear vacantes.")

        try:
            # Validar y convertir fechas
            start_date = None
            if data.get("start_date"):
                try:
                    start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Fecha de inicio mal formateada. Usa Букмекерлар-MM-DD.")
            
            end_date = None
            if data.get("end_date"):
                try:
                    end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Fecha de fin mal formateada. Usa Букмекерлар-MM-DD.")

            vacant = self.vacant_repo.create_vacant(
                institution_email=institution_email,
                area=data.get("area"),
                hours=data.get("hours"),
                modality=data.get("modality"),
                start_date=start_date,
                end_date=end_date,
                description=data.get("description"),
                requirements=data.get("requirements"),
                status=data.get("status", "activa"),
                location=data.get("location", ""),
                tags=data.get("tags", ""),
                is_draft=data.get("is_draft", False),
                latitude=data.get("latitude"),
                longitude=data.get("longitude")
            )
            db.session.commit()
            return {"message": "Vacante creada exitosamente.", "id": vacant.id}
        except ValueError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al crear la vacante: {e}")

    def list_my_vacants(self, institution_email: str):
        user = self.user_repo.get_by_email(institution_email)
        if not user or user.role.name != "institution":
            raise ValueError("Solo las instituciones pueden ver sus vacantes.")

        vacants = self.vacant_repo.get_institution_vacants(institution_email)

        result = []
        for v in vacants:
            applications_count = self.application_repo.count_applications_for_vacant(v.id)
            accepted_application = self.application_repo.get_accepted_application_for_vacant(v.id)

            status_summary = ""
            if v.is_draft:
                status_summary = "borrador"
            elif accepted_application:
                status_summary = "cerrada"
            elif applications_count > 0:
                status_summary = "activa_con_postulaciones"
            else:
                status_summary = "activa_sin_postulaciones"

            vacant_dict = v.to_dict()
            vacant_dict["applications_count"] = applications_count
            vacant_dict["status_summary"] = status_summary
            result.append(vacant_dict)
        return result

    def update_vacant(self, vacant_id: int, institution_email: str, data: dict):
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")
        
        if vacant.institution_email != institution_email:
            raise ValueError("No tienes permiso para modificar esta vacante.")

        try:
            start_date = None
            if data.get("start_date"):
                try:
                    start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Fecha de inicio mal formateada. Usa Букмекерлар-MM-DD.")
            else:
                start_date = vacant.start_date # Mantener el valor existente si no se provee

            end_date = None
            if data.get("end_date"):
                try:
                    end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Fecha de fin mal formateada. Usa Букмекерлар-MM-DD.")
            else:
                end_date = vacant.end_date # Mantener el valor existente si no se provee

            self.vacant_repo.update_vacant(
                vacant,
                {
                    "area": data.get("area"),
                    "hours": data.get("hours"),
                    "description": data.get("description"),
                    "modality": data.get("modality"),
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": data.get("status"),
                    "requirements": data.get("requirements"),
                    "location": data.get("location"),
                    "tags": ','.join(data.get("tags")) if isinstance(data.get("tags"), list) else data.get("tags"),
                    "is_draft": data.get("is_draft"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude")
                }
            )
            db.session.commit()
            return {"message": "Vacante actualizada correctamente."}
        except ValueError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al actualizar la vacante: {e}")

    def delete_vacant(self, vacant_id: int, institution_email: str):
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")
        
        if vacant.institution_email != institution_email:
            raise ValueError("No tienes permiso para eliminar esta vacante.")

        try:
            applications_to_vacant = self.application_repo.get_all_applications_by_vacant(vacant.id)
            for app in applications_to_vacant:
                self.application_repo.update_application_status(app, "cancelada_por_institucion")
                self.notification_service.create_and_send_notification(
                    recipient_email=app.student_email,
                    sender_email=institution_email, # El email de la institución que elimina
                    type="vacant_deleted",
                    message=f"La vacante '{vacant.area}' ha sido eliminada por la institución. Tu postulación ha sido cancelada.",
                    link=f"/dashboard/my-applications",
                    related_id=app.id,
                    send_email_too=True
                )
            self.vacant_repo.delete_vacant(vacant)
            db.session.commit()
            return {"message": "Vacante eliminada."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al eliminar la vacante: {e}")

    def toggle_vacant_status(self, vacant_id: int, institution_email: str, new_status: str):
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")

        if vacant.institution_email != institution_email:
            raise ValueError("No tienes permiso para modificar esta vacante.")

        if new_status not in ["activa", "inactiva"]:
            raise ValueError("Estado inválido (usa 'activa' o 'inactiva').")

        try:
            self.vacant_repo.update_vacant(vacant, {"status": new_status})
            db.session.commit()
            return {"message": f"Vacante marcada como '{new_status}'."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al cambiar el estado de la vacante: {e}")

    def publish_vacant(self, vacant_id: int, institution_email: str):
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")

        if vacant.institution_email != institution_email:
            raise ValueError("No tienes permiso para publicar esta vacante.")

        if not vacant.is_draft:
            return {"message": "Esta vacante ya está publicada."} # No es un error, solo informativo

        try:
            self.vacant_repo.update_vacant(vacant, {"is_draft": False})
            db.session.commit()
            return {"message": "Vacante publicada correctamente."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al publicar la vacante: {e}")

    def get_applications_for_vacant(self, vacant_id: int, institution_email: str):
        vacant = self.vacant_repo.get_by_id(vacant_id)
        if not vacant:
            raise ValueError("Vacante no encontrada.")
        
        if vacant.institution_email != institution_email:
            raise ValueError("No tienes permiso para ver estas postulaciones.")

        applications = self.application_repo.get_applications_with_student_profiles_by_vacant(vacant_id)

        result = []
        for app in applications:
            if app.student and app.student.student_profile:
                student_user = app.student
                student_profile = app.student.student_profile

                student_data = {
                    "name": student_user.name,
                    "email": student_user.email,
                    "career": student_profile.career,
                    "semester": student_profile.semestre,
                    "skills": student_profile.skills.split(',') if student_profile.skills else [],
                    "cv_url": f"{current_app.config['UPLOADED_FILES_BASE_URL']}/uploads/{student_profile.cv_path}" if student_profile.cv_path else None # Generar URL completa
                }
                
                result.append({
                    "application_id": app.id,
                    "status": app.status,
                    "submitted_at": app.created_at.isoformat() if app.created_at else None,
                    "student": student_data
                })
        return result

    def decide_application(self, application_id: int, current_user_email: str, decision: str, feedback: str):
        # Fetch the application first
        app = self.application_repo.get_application_by_id(application_id)
        if not app:
            raise ValueError("Postulación no encontrada.")

        # Ensure the current user (institution) has permission to decide on this application
        if app.vacant.institution_email != current_user_email:
            raise ValueError("No tienes permiso para decidir sobre esta postulación.")

        try:
            self.application_repo.update_application_status(app, decision, feedback)
            
            # Notificación al estudiante sobre el cambio de estado de SU postulación
            self.notification_service.create_and_send_notification(
                recipient_email=app.student_email,
                sender_email=current_user_email, # Email de la institución que decide
                type=f"application_{decision}", # Ej. 'application_aceptado', 'application_rechazado'
                message=f"Tu postulación a la vacante '{app.vacant.area}' ha sido marcada como '{decision}'.",
                link=f"/dashboard/my-applications/{app.id}",
                related_id=app.id,
                send_email_too=True
            )

            if decision == "aceptado":
                other_applications = self.application_repo.get_all_applications_by_student(app.student_email)
                for other_app in other_applications:
                    if other_app.id != app.id and other_app.status in ["pendiente", "en_revision", "en_entrevista"]:
                        self.application_repo.update_application_status(other_app, "retirada_por_aceptacion_en_otra")
                        # Notificar a las otras instituciones
                        if other_app.vacant and other_app.vacant.institution_email:
                            self.notification_service.create_and_send_notification(
                                recipient_email=other_app.vacant.institution_email,
                                sender_email=app.student.name, # El estudiante fue aceptado
                                type="student_accepted_elsewhere",
                                message=f"El estudiante {app.student.name} ha sido aceptado en otra vacante. Su postulación a '{other_app.vacant.area}' ha sido retirada.",
                                link=f"/dashboard/vacants/{other_app.vacant.id}/applications",
                                related_id=other_app.id,
                                send_email_too=True
                            )
            db.session.commit()
            return {"message": f"Postulación marcada como '{decision}' correctamente."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al decidir sobre la postulación: {e}")

    def get_vacants_for_map(self):
        # Esta función podría ser más compleja si tienes lógica de geocodificación aquí.
        # Por ahora, solo lista vacantes activas con lat/lon.
        return self.vacant_repo.get_active_vacants_with_coordinates()
    
    def get_unique_hours(self):
        return self.vacant_repo.get_unique_hours()

