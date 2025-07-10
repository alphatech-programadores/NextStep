# backend/models/user.py

from extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    confirmation_token = db.Column(db.String(128), unique=True, nullable=True)

    # Campos para intentos de login y bloqueo
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_until = db.Column(db.DateTime, nullable=True)

    # Relaciones
    role = db.relationship('Role', back_populates='users')
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, lazy=True)
    institution_profile = db.relationship('InstitutionProfile', back_populates='user', uselist=False, lazy=True)
    applications = db.relationship('Application', back_populates='student', lazy=True)
    # NUEVO CAMBIO AQUÍ: Añadir la relación 'notifications'
    notifications = db.relationship('Notification', back_populates='user', lazy=True)


    def __init__(self, email, name, role, is_confirmed=False, confirmed_on=None, confirmation_token=None):
        self.email = email
        self.name = name
        self.role = role
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on
        self.confirmation_token = confirmation_token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role.name if self.role else None,
            'is_confirmed': self.is_confirmed,
            'confirmed_on': self.confirmed_on.isoformat() if self.confirmed_on else None,
            'failed_login_attempts': self.failed_login_attempts,
            'lockout_until': self.lockout_until.isoformat() if self.lockout_until else None
        }

    def __repr__(self):
        return f"<User {self.email}>"

