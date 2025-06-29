# models/user.py
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # La relación se define aquí y se vincula a 'users' en el modelo Role.
    role = db.relationship('Role', back_populates='users')

    applications = db.relationship("Application", back_populates="student", lazy="dynamic", cascade="all, delete-orphan")
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    institution_profile = db.relationship('InstitutionProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")




    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    def to_dict(self):
        data = {
            "email": self.email,
            "name": self.name,
            "role": self.role.name if self.role else None
        }

        return data