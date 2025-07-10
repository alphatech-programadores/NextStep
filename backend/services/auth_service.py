# services/auth_service.py

import re
from datetime import datetime, timedelta
from extensions import db, jwt_redis_blacklist # Asegurarse de que db esté importado
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity
from models.user import User
from models.role import Role
from repositories.user_repository import UserRepository
from flask import current_app # Para logging o configuración

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository(db.session)
        self.LOCKOUT_DURATION_MINUTES = 30
        self.MAX_LOGIN_ATTEMPTS = 3

    def _validate_password_strength(self, password: str):
        if len(password) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"[a-z]", password):
            raise ValueError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r"\d", password):
            raise ValueError("La contraseña debe contener al menos un dígito.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("La contraseña debe contener al menos un carácter especial.")

    def register_user(self, email, password, name, role_name):
        if self.user_repository.get_by_email(email):
            raise ValueError("El correo electrónico ya está registrado.")

        self._validate_password_strength(password)

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f"Rol '{role_name}' no encontrado.")

        new_user = User(email=email, name=name, role=role)
        new_user.set_password(password)
        # CORREGIDO: Usar db.session.add en lugar de self.user_repository.add
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def login_user(self, email, password):
        user = self.user_repository.get_by_email(email)

        if not user:
            raise ValueError("Credenciales inválidas.")

        if user.lockout_until and user.lockout_until > datetime.utcnow():
            remaining_time = user.lockout_until - datetime.utcnow()
            minutes = int(remaining_time.total_seconds() / 60)
            seconds = int(remaining_time.total_seconds() % 60)
            raise ValueError(f"Cuenta bloqueada. Intenta de nuevo en {minutes} minutos y {seconds} segundos.")

        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.MAX_LOGIN_ATTEMPTS:
                user.lockout_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
                user.failed_login_attempts = 0
                db.session.commit()
                raise ValueError(f"Demasiados intentos fallidos. Tu cuenta ha sido bloqueada por {self.LOCKOUT_DURATION_MINUTES} minutos.")
            db.session.commit()
            raise ValueError("Credenciales inválidas.")

        user.failed_login_attempts = 0
        user.lockout_until = None
        db.session.commit()

        access_token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)

        return {"access_token": access_token, "refresh_token": refresh_token, "user_role": user.role.name}

    def refresh_access_token(self): # Eliminado jti_claim como argumento para coincidir con la llamada en routes/auth.py
        current_user_email = get_jwt_identity()
        access_token = create_access_token(identity=current_user_email)
        return {"access_token": access_token}

    def logout_user(self, jti):
        jwt_redis_blacklist.set(jti, "true", ex=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
        return {"message": "Sesión cerrada correctamente"}

    def reset_password_request(self, email):
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("No se encontró una cuenta con ese correo electrónico.")
        return {"message": "Si tu cuenta existe, se ha enviado un correo para restablecer la contraseña."}

    def reset_password(self, token, new_password):
        user = self.user_repository.get_by_confirmation_token(token)
        if not user:
            raise ValueError("Token de restablecimiento inválido o expirado.")

        self._validate_password_strength(new_password)

        user.set_password(new_password)
        user.confirmation_token = None
        db.session.commit()
        return {"message": "Contraseña restablecida correctamente."}
