# services/profile_service.py
import os
from flask import current_app
from extensions import db
from models.user import User
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile
from werkzeug.utils import secure_filename

# Importar repositorios
from repositories.user_repository import UserRepository
from repositories.student_profile_repository import StudentProfileRepository
from repositories.institution_profile_repository import InstitutionProfileRepository

class ProfileService:
    def __init__(self):
        self.user_repo = UserRepository(db.session)
        self.student_profile_repo = StudentProfileRepository(db.session)
        self.institution_profile_repo = InstitutionProfileRepository(db.session)

    # --- Funciones auxiliares para manejo de archivos (mantenidas aquí para encapsulación del servicio) ---
    def _allowed_file(self, filename, allowed_extensions):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    def _save_uploaded_file(self, file, upload_subdir, allowed_extensions):
        if not file or file.filename == '':
            return None, "No se seleccionó ningún archivo o el archivo está vacío."

        if not self._allowed_file(file.filename, allowed_extensions):
            return None, "Tipo de archivo no permitido."

        filename = secure_filename(file.filename)
        target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_subdir)
        os.makedirs(target_dir, exist_ok=True) 
        
        filepath = os.path.join(target_dir, filename)
        try:
            file.save(filepath)
            # Retorna la ruta relativa para guardar en la base de datos
            return os.path.join(upload_subdir, filename).replace(os.sep, '/'), None
        except Exception as e:
            current_app.logger.error(f"Error al guardar archivo {filename} en {filepath}: {e}")
            return None, f"Error interno al guardar el archivo: {str(e)}"
    # --- Fin Funciones auxiliares de archivo ---


    def _get_or_create_profile(self, user: User):
        """Función auxiliar para obtener o crear el perfil del usuario."""
        if user.role.name == "student":
            profile = self.student_profile_repo.get_by_email(user.email)
            if not profile:
                profile = self.student_profile_repo.create_profile(user.email)
                db.session.commit()
            return profile, "student"
        elif user.role.name == "institution":
            profile = self.institution_profile_repo.get_by_email(user.email)
            if not profile:
                profile = self.institution_profile_repo.create_profile(user.email)
                db.session.commit()
            return profile, "institution"
        return None, None

    def get_my_profile(self, current_user_email: str):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")

        profile, profile_type = self._get_or_create_profile(user)

        if not profile:
            raise ValueError("No hay perfil disponible para este rol.")

        profile_data = user.to_dict()
        profile_data.update(profile.to_dict())

        # Generar URLs completas para archivos subidos
        # Usar os.path.basename para obtener solo el último componente de la ruta si la carpeta uploads
        # es el último segmento de la ruta UPLOAD_FOLDER
        upload_base_url_segment = os.path.basename(current_app.config['UPLOAD_FOLDER'])
        
        if profile_type == "student":
            if profile.cv_path:
                profile_data['cv_url'] = f"{current_app.config['BASE_URL']}/{upload_base_url_segment}/{profile.cv_path}"
            else:
                profile_data['cv_url'] = None
            if profile.profile_picture_url:
                profile_data['profile_picture_url'] = f"{current_app.config['BASE_URL']}/{upload_base_url_segment}/{profile.profile_picture_url}"
            else:
                profile_data['profile_picture_url'] = None
        elif profile_type == "institution":
            if profile.logo_url:
                profile_data['logo_url'] = f"{current_app.config['BASE_URL']}/{upload_base_url_segment}/{profile.logo_url}"
            else:
                profile_data['logo_url'] = None
            profile_data['website'] = getattr(profile, "website", "") # Asegura que exista el campo

        return profile_data, profile_type

    def update_my_profile(self, current_user_email: str, form_data: dict, files_data: dict):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        profile, profile_type = self._get_or_create_profile(user)

        if not profile:
            raise ValueError("Este rol no tiene un perfil actualizable.")

        try:
            update_data = {} # Diccionario para pasar al método update_profile del repositorio

            if profile_type == "student":
                update_data["career"] = form_data.get("career", profile.career)
                
                semestre_str = form_data.get("semestre")
                if semestre_str is not None:
                    if semestre_str == "":
                        update_data["semestre"] = None
                    else:
                        try:
                            update_data["semestre"] = int(semestre_str)
                        except ValueError:
                            raise ValueError("El semestre debe ser un número entero válido.")
                else: # Si no se provee, usar el valor actual del perfil
                    update_data["semestre"] = profile.semestre

                average_str = form_data.get("average")
                if average_str is not None:
                    if average_str == "":
                        update_data["average"] = None
                    else:
                        try:
                            update_data["average"] = float(average_str)
                        except ValueError:
                            raise ValueError("El promedio debe ser un número decimal válido.")
                else: # Si no se provee, usar el valor actual del perfil
                    update_data["average"] = profile.average

                update_data["phone"] = form_data.get("phone", profile.phone)
                update_data["address"] = form_data.get("address", profile.address)
                update_data["availability"] = form_data.get("availability", profile.availability)
                update_data["skills"] = form_data.get("skills", profile.skills)
                update_data["portfolio_url"] = form_data.get("portfolio_url", profile.portfolio_url)

                # Manejo de subida de CV
                if 'cv_file' in files_data and files_data['cv_file']:
                    cv_file = files_data['cv_file']
                    cv_path, error = self._save_uploaded_file(cv_file, 'cvs', current_app.config['ALLOWED_EXTENSIONS_CV'])
                    if error:
                        raise RuntimeError(f"Error al subir CV: {error}")
                    if cv_path:
                        if profile.cv_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.cv_path)):
                            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.cv_path))
                        update_data["cv_path"] = cv_path # Añadir al diccionario de actualización
                else: # Si no se provee un nuevo archivo, mantener el existente
                    update_data["cv_path"] = profile.cv_path

                # Manejo de subida de Foto de Perfil
                if 'profile_picture_file' in files_data and files_data['profile_picture_file']:
                    profile_picture_file = files_data['profile_picture_file']
                    pic_path, error = self._save_uploaded_file(profile_picture_file, 'profile_pics', current_app.config['ALLOWED_EXTENSIONS_IMG'])
                    if error:
                        raise RuntimeError(f"Error al subir foto de perfil: {error}")
                    if pic_path:
                        if profile.profile_picture_url and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture_url)):
                            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture_url))
                        update_data["profile_picture_url"] = pic_path # Añadir al diccionario de actualización
                else: # Si no se provee un nuevo archivo, mantener el existente
                    update_data["profile_picture_url"] = profile.profile_picture_url
                
                # Llamar al repositorio para actualizar
                self.student_profile_repo.update_profile(profile, update_data)

            elif profile_type == "institution":
                update_data["institution_name"] = form_data.get("institution_name", profile.institution_name)
                update_data["contact_person"] = form_data.get("contact_person", profile.contact_person)
                update_data["contact_phone"] = form_data.get("contact_phone", profile.contact_phone)
                update_data["sector"] = form_data.get("sector", profile.sector)
                update_data["address"] = form_data.get("address", profile.address)
                update_data["description"] = form_data.get("description", profile.description)
                update_data["website"] = form_data.get("website", getattr(profile, "website", "")) # Usar getattr para website por si no existe en el perfil sembrado

                # Manejo de subida de Logo
                if 'logo_file' in files_data and files_data['logo_file']:
                    logo_file = files_data['logo_file']
                    logo_path, error = self._save_uploaded_file(logo_file, 'logos', current_app.config['ALLOWED_EXTENSIONS_IMG'])
                    if error:
                        raise RuntimeError(f"Error al subir logo: {error}")
                    if logo_path:
                        if profile.logo_url and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.logo_url)):
                            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], profile.logo_url))
                        update_data["logo_url"] = logo_path # Añadir al diccionario de actualización
                else: # Si no se provee un nuevo archivo, mantener el existente
                    update_data["logo_url"] = profile.logo_url
                
                # Llamar al repositorio para actualizar
                self.institution_profile_repo.update_profile(profile, update_data)
            
            db.session.commit()
            return {"message": "Perfil actualizado exitosamente."}

        except ValueError as e: # Captura las validaciones de tipo
            db.session.rollback()
            raise e
        except RuntimeError as e: # Captura errores de subida de archivos
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al actualizar el perfil: {e}")

    def delete_account(self, current_user_email: str):
        # ... (Este método no necesita cambios ya que opera sobre user_repo.delete_user) ...
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        try:
            self.user_repo.delete_user(user)
            db.session.commit()
            return {"message": "Cuenta eliminada correctamente."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al eliminar cuenta: {e}")

    def get_current_user_info_for_auth(self, current_user_email: str):
        # ... (Este método no necesita cambios ya que opera sobre user_repo.get_by_email) ...
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        return {"user": user.to_dict()}

    def get_student_profile_completeness(self, current_user_email: str):
        # ... (Este método no necesita cambios, ya usa get_by_email del repo) ...
        student_profile = self.student_profile_repo.get_by_email(current_user_email)
        
        if not student_profile:
            return {
                "profile": None,
                "profile_completeness": 0,
                "message": "El perfil del estudiante no ha sido creado aún."
            }

        fields_to_check = [
            'career', 'semestre', 'average', 'phone', 'address', 
            'availability', 'skills', 'portfolio_url', 'cv_path', 'profile_picture_url'
        ]
        
        completed_fields = 0
        for field in fields_to_check:
            value = getattr(student_profile, field)
            if value is not None and value != "" and (isinstance(value, (int, float)) or (isinstance(value, str) and value.strip() != "")):
                completed_fields += 1
                
        total_fields = len(fields_to_check)
        profile_completeness = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0

        return {
            "profile": student_profile.to_dict(),
            "profile_completeness": profile_completeness
        }