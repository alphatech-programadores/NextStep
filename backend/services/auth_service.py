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
from services.notification_service import NotificationService 

from extensions import db, mail
from flask import current_app
from flask_jwt_extended import create_access_token, decode_token 
from datetime import timedelta, datetime
from flask_mail import Message
from flask_jwt_extended import get_jwt
from extensions import jwt_redis_blacklist

import random # NUEVO: Para generar códigos aleatorios
import string # NUEVO: Para caracteres de códigos aleatorios


LAST_RESEND_TIME = {}

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository(db.session)
        self.student_profile_repo = StudentProfileRepository(db.session)
        self.institution_profile_repo = InstitutionProfileRepository(db.session)
        self.application_repo = ApplicationRepository(db.session)
        self.vacant_repo = VacantRepository(db.session)
        self.notification_service = NotificationService()


    # --- NUEVA FUNCIÓN AUXILIAR PARA GENERAR CÓDIGO DE CONFIRMACIÓN ---
    def _generate_confirmation_code(self, length=6):
        characters = string.ascii_uppercase + string.digits # Letras mayúsculas y números
        return ''.join(random.choice(characters) for i in range(length))
    # ------------------------------------------------------------------

    def register_user(self, email: str, password: str, name: str, role_name: str):
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
            user.set_password(password)
            user.is_confirmed = False

            # --- NUEVO: Generar y guardar código de confirmación ---
            confirmation_code = self._generate_confirmation_code()
            user.confirmation_code = confirmation_code
            user.confirmation_code_expires_at = datetime.utcnow() + timedelta(hours=2) # Código expira en 2 horas
            # --------------------------------------------------------

            if role_name == "student":
                self.student_profile_repo.create_profile(email=email)
            elif role_name == "institution":
                self.institution_profile_repo.create_profile(email=email)
            
            db.session.commit()

            confirm_token = create_access_token(identity=email, expires_delta=timedelta(days=1), additional_claims={"confirm": True})
            BASE_URL = current_app.config["BASE_URL"]
            confirm_url = f"{BASE_URL}/auth/confirm/{confirm_token}"

            msg = Message(subject="Confirma tu correo en NextStep",
                        sender=current_app.config["MAIL_DEFAULT_SENDER"],
                        recipients=[email])
            # --- MODIFICADO: Incluir código en el cuerpo del correo ---
            msg.body = (f"Hola {name},\n\n"
                        f"Para confirmar tu correo, por favor visita este enlace: {confirm_url}\n\n"
                        f"O, si lo prefieres, introduce este código en la página de confirmación: {confirmation_code}\n\n"
                        f"Este código es válido por 2 horas.\n\n"
                        f"¡Gracias por unirte a NextStep!")
            # -----------------------------------------------------------
            mail.send(msg)

            return {"message": "Usuario registrado correctamente. Revisa tu correo para confirmar tu cuenta."}
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al registrar usuario: {e}")

    # --- MODIFICADO: Función confirm_email para aceptar token O email/código ---
    def confirm_email(self, token: str = None, email: str = None, code: str = None):
        user = None
        # Priorizar confirmación por token de URL
        if token:
            try:
                decoded = decode_token(token)
                email_from_token = decoded["sub"]
                claims = decoded.get("confirm", False)

                if not claims:
                    raise ValueError("Token inválido para confirmación.")
                
                user = self.user_repo.get_by_email(email_from_token)
                if not user:
                    raise ValueError("Usuario no encontrado para el token.")
                
                if user.is_confirmed:
                    return {"message": "Correo ya confirmado."}

                user.is_confirmed = True
                user.confirmed_on = datetime.utcnow()
                user.confirmation_code = None # Limpiar código y expiración al confirmar
                user.confirmation_code_expires_at = None
                db.session.commit()
                return {"message": "Correo confirmado exitosamente por enlace."}

            except Exception as e:
                db.session.rollback()
                if "Signature has expired" in str(e):
                    raise ValueError("Token expirado. Por favor, solicita un nuevo enlace de confirmación.")
                elif "Invalid signature" in str(e) or "Not enough segments" in str(e):
                    raise ValueError("Token inválido o malformado.")
                else:
                    raise RuntimeError(f"Error al confirmar correo con token: {e}")
        
        # Si no hay token o falló la validación del token, intentar con email y código
        elif email and code:
            user = self.user_repo.get_by_email(email)
            if not user:
                raise ValueError("Credenciales de confirmación inválidas.") # No revelar si el email existe

            if user.is_confirmed:
                return {"message": "Correo ya confirmado."}
            
            # Validar código y expiración
            if user.confirmation_code != code.upper(): # Convertir a mayúsculas para ser case-insensitive
                raise ValueError("Código de confirmación inválido.")
            
            if user.confirmation_code_expires_at and datetime.utcnow() > user.confirmation_code_expires_at:
                raise ValueError("El código de confirmación ha expirado. Por favor, solicita uno nuevo.")
            
            user.is_confirmed = True
            user.confirmed_on = datetime.utcnow()
            user.confirmation_code = None # Limpiar código y expiración al confirmar
            user.confirmation_code_expires_at = None
            db.session.commit()
            return {"message": "Correo confirmado exitosamente por código."}
        
        else:
            raise ValueError("No se proporcionó token ni email/código para la confirmación.")


    def login_user(self, email: str, password: str):
        try:
            if not email or not password:
                raise ValueError("Email y contraseña requeridos.")
            
            user = self.user_repo.get_by_email(email)
            if not user or not user.check_password(password):
                raise ValueError("Credenciales inválidas.")

            if not user.is_confirmed:
                raise ValueError("Confirma tu correo para iniciar sesión.")
            
            access_token = create_access_token(
                identity=user.email,
                additional_claims={"role": user.role.name},
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
            db.session.rollback()
            raise RuntimeError(f"Error inesperado en el servicio de login: {e}")

    def forgot_password(self, email: str):
        if not email:
            raise ValueError("Email requerido.")

        user = self.user_repo.get_by_email(email)
        if not user:
            return {"message": "Si el correo está registrado, se enviará un enlace de recuperación."}

        try:
            reset_token = create_access_token(
                identity=user.email,
                expires_delta=timedelta(hours=1),
                additional_claims={"reset": True}
            )

            BASE_URL = current_app.config["BASE_URL"]
            reset_url = f"{BASE_URL}/auth/reset-password/{reset_token}"

            msg = Message(
                subject="Restablece tu contraseña en NextStep",
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email],
                body=f"Hola, puedes restablecer tu contraseña con este enlace:\n{reset_url}\n\nEste enlace es válido por 1 hora."
            )
            mail.send(msg)
            return {"message": "Si el correo está registrado, se enviará un enlace de recuperación."}
        except Exception as e:
            raise RuntimeError(f"Error al enviar correo de recuperación: {e}")

    def delete_account(self, current_user_email: str):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        try:
            if user.role.name == "student":
                student_applications = self.application_repo.get_all_applications_by_student(current_user_email)
                for app in student_applications:
                    self.application_repo.update_application_status(app, "cancelada_por_eliminacion_cuenta_estudiante")
                    if app.vacant and app.vacant.institution_email:
                        self.notification_service.create_and_send_notification(
                            recipient_email=app.vacant.institution_email,
                            sender_email=current_user_email,
                            type="student_account_deleted",
                            message=f"El estudiante {user.name} ha eliminado su cuenta. Su postulación a '{app.vacant.area}' ha sido cancelada.",
                            link=f"/dashboard/vacants/{app.vacant.id}/applications",
                            related_id=app.id,
                            send_email_too=True
                        )
                
            elif user.role.name == "institution":
                institution_vacants = user.institution_profile.vacants
                for vacant in institution_vacants:
                    applications_to_vacant = self.application_repo.get_all_applications_by_vacant(vacant.id)
                    for app in applications_to_vacant:
                        self.application_repo.update_application_status(app, "cancelada_por_institucion")
                        self.notification_service.create_and_send_notification(
                            recipient_email=app.student_email,
                            sender_email=current_user_email,
                            type="institution_account_deleted",
                            message=f"La institución '{user.name}' ha eliminado su cuenta. Tu postulación a '{vacant.area}' ha sido cancelada.",
                            link="/dashboard/my-applications",
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
        jti = get_jwt()["jti"]
        jwt_redis_blacklist.add(jti)
        return {"message": "Sesión cerrada correctamente"}

    def get_current_user_info(self, current_user_email: str):
        user = self.user_repo.get_by_email(current_user_email)
        if not user:
            raise ValueError("Usuario no encontrado.")
        
        return {"user": user.to_dict()}
    
    def resend_confirmation_email(self, email: str):
        if not email:
            raise ValueError("Email es requerido.")

        user = self.user_repo.get_by_email(email)
        if not user:
                return {"message": "Si el correo está registrado y no confirmado, se ha enviado un nuevo enlace de confirmación."}

        if user.is_confirmed:
                return {"message": "Tu correo ya está confirmado."}

        now = datetime.utcnow()
        last_sent = LAST_RESEND_TIME.get(email)
        resend_cooldown = timedelta(minutes=1)

        if last_sent and (now - last_sent) < resend_cooldown:
                remaining_time_seconds = (resend_cooldown - (now - last_sent)).total_seconds()
                raise RuntimeError(f"Por favor, espera {int(remaining_time_seconds)} segundos antes de intentar reenviar de nuevo.")

        try:
            # --- NUEVO: Generar y guardar nuevo código de confirmación ---
            confirmation_code = self._generate_confirmation_code()
            user.confirmation_code = confirmation_code
            user.confirmation_code_expires_at = datetime.utcnow() + timedelta(hours=2) # Código expira en 2 horas
            # -------------------------------------------------------------

            confirm_token = create_access_token(identity=email, expires_delta=timedelta(days=1), additional_claims={"confirm": True})
            BASE_URL = current_app.config["BASE_URL"]
            confirm_url = f"{BASE_URL}/auth/confirm/{confirm_token}"

            msg = Message(subject="Confirma tu correo en NextStep",
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email])
            # --- MODIFICADO: Incluir código en el cuerpo del correo ---
            msg.body = (f"Hola {user.name},\n\n"
                        f"Para confirmar tu correo, por favor visita este enlace: {confirm_url}\n\n"
                        f"O, si lo prefieres, introduce este código en la página de confirmación: {confirmation_code}\n\n"
                        f"Este código es válido por 2 horas.\n\n"
                        f"¡Gracias por unirte a NextStep!")
            # -----------------------------------------------------------

            mail.send(msg)
            LAST_RESEND_TIME[email] = now

            db.session.commit() # Asegura que el nuevo código y expiración se guarden
            return {"message": "Si el correo está registrado y no confirmado, se ha enviado un nuevo enlace de confirmación."}
        except Exception as e:
            raise RuntimeError(f"Error al reenviar correo de confirmación: {e}")
        
    def reset_password(self, token: str, new_password: str):
        if not new_password:
            raise ValueError("Contraseña nueva requerida.")

        try:
            decoded = decode_token(token)
            if not decoded.get("reset", False):
                raise ValueError("Token inválido para restablecimiento.")

            email = decoded["sub"]
            user = self.user_repo.get_by_email(email)

            if not user:
                raise ValueError("Usuario no encontrado.")

            user.set_password(new_password)
            if hasattr(user, 'last_password_reset'):
                user.last_password_reset = datetime.utcnow()

            # --- NUEVO: Confirmar usuario automáticamente al restablecer contraseña ---
            if not user.is_confirmed: # Solo si no está ya confirmado (opcional, pero buena práctica)
                user.is_confirmed = True
                user.confirmed_on = datetime.utcnow()
                # También limpiar cualquier código de confirmación pendiente
                user.confirmation_code = None
                user.confirmation_code_expires_at = None
            # ------------------------------------------------------------------------
            
            db.session.commit()
            return {"message": "Contraseña actualizada exitosamente."}

        except Exception as e:
            db.session.rollback()
            if "Signature has expired" in str(e):
                raise ValueError("Token expirado. Por favor, solicita un nuevo enlace para restablecer tu contraseña.")
            elif "Invalid signature" in str(e) or "Not enough segments" in str(e):
                raise ValueError("Token inválido o malformado.")
            else:
                raise RuntimeError(f"Error al restablecer contraseña: {e}")