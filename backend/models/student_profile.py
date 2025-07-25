# models/student_profile.py
from extensions import db

class SerializableMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True)
    career = db.Column(db.String(100), nullable=False, default="")
    semestre = db.Column(db.Integer, nullable=True)
    average = db.Column(db.Float, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.String(30), nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    cv_path = db.Column(db.String(255), nullable=True)
    profile_picture_url = db.Column(db.String(255), nullable=True)

    # Relación inversa para conectar de vuelta con el User
    user = db.relationship('User', back_populates='student_profile')

    def to_dict(self):
        return {
            "email": self.email,
            "career": self.career,
            "semestre": self.semestre,
            "average": getattr(self, "average", None),
            "phone": getattr(self, "phone", ""),
            "address": getattr(self, "address", ""),
            "availability": getattr(self, "availability", ""),
            "skills": getattr(self, "skills", ""),
            "portfolio_url": getattr(self, "portfolio_url", ""),
            "cv_path": getattr(self, "cv_path", ""),
            "profile_picture_url": getattr(self, "profile_picture_url", "")
        }
