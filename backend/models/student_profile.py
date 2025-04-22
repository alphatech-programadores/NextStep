from extensions import db

class SerializableMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StudentProfile(db.Model, SerializableMixin):  # <- OJO: SerializableMixin aquí
    __tablename__ = 'student_profiles'

    email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True)
    career = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.Integer, nullable=True)
    average = db.Column(db.Float)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    availability = db.Column(db.String(100))
    skills = db.Column(db.Text)
    portfolio_url = db.Column(db.String(255))
    cv_url = db.Column(db.String(255))
