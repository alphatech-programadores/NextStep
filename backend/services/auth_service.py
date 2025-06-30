# services/auth_service.py

# Repositorios
from repositories.application_repository import ApplicationRepository
from repositories.user_repository import UserRepository
from repositories.student_profile_repository import StudentProfileRepository
from repositories.institution_profile_repository import InstitutionProfileRepository
from repositories.vacant_repository import VacantRepository


# Models
from models.application import Application 
from models.vacant import Vacant 
from models.user import User
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile

# Servicios
from services.notification_service import NotificationService # Importa el servicio de notificación

from extensions import db, mail
from flask import current_app
from flask_jwt_extended import create_access_token, decode_token # Asegúrate de que decode_token esté aquí
from datetime import timedelta, datetime
from flask_mail import Message


LAST_RESEND_TIME = {}

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository(db.session)
        self.student_profile_repo = StudentProfileRepository(db.session)
        self.institution_profile_repo = InstitutionProfileRepository(db.session)
        self.application_repo = ApplicationRepository(db.session)
        self.vacant_repo = VacantRepository(db.session)
        self.notification_service = NotificationService()

    def register_user(self, email: str, password: str, name: str, role_name: str):
        # ... (Mantén el código existente para register_user) ...
        if not email or not password or not name:
            raise ValueError("Todos los campos son obligatorios.")

        if self.user_repo.get_by_email(email):
            raise ValueError("El usuario ya existe.")

        if role_name not in ["student", "institution"]:
            raise ValueError("Rol inválido.")
        
        try:
            role = self.user_repo.get_role_by_name(role_name)
            if not role:
                role = self.user_repo.create_role(role_name)

            user = self.user_repo.create_user(email=email, name=name, 
                                            password_hash="", role_id=role.id)
            user.set_password(password) # Establece la contraseña hasheada
            user.is_confirmed = False # Los nuevos registros no están confirmados hasta que se verifica el email

            if role_name == "student":
                self.student_profile_repo.create_profile(email=email)
            elif role_name == "institution":
                self.institution_profile_repo.create_profile(email=email)
            
            db.session.commit() #

            confirm_token = create_access_token(identity=email, expires_delta=timedelta(days=1), additional_claims={"confirm": True}) #
            BASE_URL = current_app.config["BASE_URL"]
            confirm_url = f"{BASE_URL}/auth/confirm/{confirm_token}"

            msg = Message(subject="Confirma tu correo",
                        sender=current_app.config["MAIL_DEFAULT_SENDER"],
                        recipients=[email])
            msg.body = f"Hola {name}, por favor confirma tu correo visitando este enlace: {confirm_url}"
            mail.send(msg)

            return {"message": "Usuario registrado correctamente."}
        except Exception as e:
            db.session.rollback() #
            raise RuntimeError(f"Error al registrar usuario: {e}")

    def confirm_email(self, token: str):
        try:
            decoded = decode_token(token) #
            email = decoded["sub"]
            claims = decoded.get("confirm", False)

            if not claims:
                raise ValueError("Token inválido para confirmación.")

            user = self.user_repo.get_by_email(email)
            if not user:
                raise ValueError("Usuario no encontrado.")

            if user.is_confirmed: #
                return {"message": "Correo ya confirmado."} # Devuelve un mensaje en lugar de levantar error para este caso

            user.is_confirmed = True #
            db.session.commit() #
            return {"message": "Correo confirmado exitosamente."}

        except Exception as e:
            db.session.rollback() #
            # Captura errores específicos de JWT (ExpiredSignatureError, InvalidTokenError)
            if "Signature has expired" in str(e):
                raise ValueError("Token expirado. Por favor, solicita un nuevo enlace de confirmación.")
            elif "Invalid signature" in str(e) or "Not enough segments" in str(e):
                raise ValueError("Token inválido o malformado.")
            else:
                raise RuntimeError(f"Error al confirmar correo: {e}")

    def login_user(self, email: str, password: str):
        # ... (Mantén el código existente para login_user) ...
        try:
            if not email or not password:
                raise ValueError("Email y contraseña requeridos.")
            
            user = self.user_repo.get_by_email(email) #
            if not user or not user.check_password(password): #
                raise ValueError("Credenciales inválidas.")

            if not user.is_confirmed: #
                raise ValueError("Confirma tu correo para iniciar sesión.")
            
            access_token = create_access_token(
                identity=user.email,
                additional_claims={"role": user.role.name}, #
                expires_delta=timedelta(hours=4)
            ) 

            return {
                "message": "Inicio de sesión exitoso.",
                "access_token": access_token,
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "role": user.role.name
                }
            }
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback() # No debería necesitar rollback en un GET, pero si hay escritura en el futuro...
            raise RuntimeError(f"Error inesperado en el servicio de login: {e}")

    def forgot_password(self, email: str):
        if not email:
            raise ValueError("Email requerido.")

        user = self.user_repo.get_by_email(email) #
        # Por seguridad, siempre responde con el mismo mensaje si el correo existe o no
        if not user:
            return {"message": "Si el correo está registrado, se enviará un enlace de recuperación."}

        try:
            reset_token = create_access_token(
                identity=user.email,
                expires_delta=timedelta(hours=1), #
                additional_claims={"reset": True} #
            )

            BASE_URL = current_app.config["BASE_URL"]
            # Asumiendo que esta URL apunta a tu frontend
            reset_url = f"{BASE_URL}/auth/reset-password/{reset_token}" #

            msg = Message(
                subject="Restablece tu contraseña",
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email],
                body=f"Hola, puedes restablecer tu contraseña con este enlace:\n{reset_url}" #
            )
            mail.send(msg) #
            return {"message": "Si el correo está registrado, se enviará un enlace de recuperación."}
        except Exception as e:
            raise RuntimeError(f"Error al enviar correo de recuperación: {e}")

    def reset_password(self, token: str, new_password: str):
        if not new_password:
            raise ValueError("Contraseña nueva requerida.")

        try:
            decoded = decode_token(token) #
            if not decoded.get("reset", False): #
                raise ValueError("Token inválido para restablecimiento.")

            email = decoded["sub"]
            user = self.user_repo.get_by_email(email) #

            if not user:
                raise ValueError("Usuario no encontrado.")

            user.set_password(new_password) #
            # Opcional: registrar la última vez que se cambió la contraseña (si tienes el campo)
            if hasattr(user, 'last_password_reset'):
                user.last_password_reset = datetime.utcnow()
            
            db.session.commit() #
            return {"message": "Contraseña actualizada exitosamente."}

        except Exception as e:
            db.session.rollback() #
            if "Signature has expired" in str(e):
                raise ValueError("Token expirado. Por favor, solicita un nuevo enlace para restablecer tu contraseña.")
            elif "Invalid signature" in str(e) or "Not enough segments" in str(e):
                raise ValueError("Token inválido o malformado.")
            else:
                raise RuntimeError(f"Error al restablecer contraseña: {e}")

    def delete_account(self, current_user_email: str):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        try:
            if user.role.name == "student":
                student_applications = self.application_repo.get_all_applications_by_student(current_user_email)
                for app in student_applications:
                    self.application_repo.update_application_status(app, "cancelada_por_eliminacion_cuenta_estudiante")
                    # Notificar a la institución propietaria de la vacante
                    if app.vacant and app.vacant.institution_email:
                        self.notification_service.create_and_send_notification(
                            recipient_email=app.vacant.institution_email,
                            sender_email=current_user_email,
                            type="student_account_deleted",
                            message=f"El estudiante {user.name} ha eliminado su cuenta. Su postulación a '{app.vacant.area}' ha sido cancelada.",
                            link=f"/dashboard/vacants/{app.vacant.id}/applications", # Enlaza a la gestión de postulaciones de la vacante
                            related_id=app.id,
                            send_email_too=True # Opcional: enviar también por email
                        )
                
            elif user.role.name == "institution":
                # Al eliminar la cuenta de la institución, notificar a los estudiantes afectados
                # Accedemos a las vacantes de la institución a través de la relación
                institution_vacants = user.institution_profile.vacants # asumiendo que 'vacants' está bien relacionado en InstitutionProfile
                for vacant in institution_vacants:
                    applications_to_vacant = self.application_repo.get_all_applications_by_vacant(vacant.id)
                    for app in applications_to_vacant:
                        self.application_repo.update_application_status(app, "cancelada_por_institucion")
                        self.notification_service.create_and_send_notification(
                            recipient_email=app.student_email,
                            sender_email=current_user_email,
                            type="institution_account_deleted",
                            message=f"La institución '{user.name}' ha eliminado su cuenta. Tu postulación a '{vacant.area}' ha sido cancelada.",
                            link="/dashboard/my-applications", # Enlaza a las postulaciones del estudiante
                            related_id=app.id,
                            send_email_too=True
                        )
            
            self.user_repo.delete_user(user)
            db.session.commit()
            return {"message": "Cuenta eliminada correctamente."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al eliminar cuenta: {e}")
        
    def logout_user(self):
        return {"message": "Sesión cerrada."}

    def get_current_user_info(self, current_user_email: str):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        return {"user": user.to_dict()} #
    
    def resend_confirmation_email(self, email: str):
        if not email:
            raise ValueError("Email es requerido.")

        user = self.user_repo.get_by_email(email)
        if not user:
                # Por seguridad, no revelamos si el correo existe o no
                return {"message": "Si el correo está registrado y no confirmado, se ha enviado un nuevo enlace de confirmación."}

        if user.is_confirmed:
                return {"message": "Tu correo ya está confirmado."}

        # --- Lógica de Limitación (Rate Limiting) ---
        now = datetime.utcnow()
        last_sent = LAST_RESEND_TIME.get(email)
        resend_cooldown = timedelta(minutes=1) # Limitar a un reenvío cada 1 minuto

        if last_sent and (now - last_sent) < resend_cooldown:
                remaining_time_seconds = (resend_cooldown - (now - last_sent)).total_seconds()
                raise RuntimeError(f"Por favor, espera {int(remaining_time_seconds)} segundos antes de intentar reenviar de nuevo.")

        try:
            confirm_token = create_access_token(identity=email, expires_delta=timedelta(days=1), additional_claims={"confirm": True})
            BASE_URL = current_app.config["BASE_URL"]
            confirm_url = f"{BASE_URL}/auth/confirm/{confirm_token}"

            msg = Message(subject="Confirma tu correo",
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email])
            msg.body = f"Hola {user.name}, por favor confirma tu correo visitando este enlace: {confirm_url}"

            mail.send(msg)
            LAST_RESEND_TIME[email] = now # Actualizar el último tiempo de envío

            return {"message": "Si el correo está registrado y no confirmado, se ha enviado un nuevo enlace de confirmación."}
        except Exception as e:
            # Aquí podrías querer eliminar el email de LAST_RESEND_TIME si el envío falló
            # para no penalizar al usuario por un error del sistema. Depende de la política.
                raise RuntimeError(f"Error al reenviar correo de confirmación: {e}")

