from extensions import db
#  models/institution_profile.py
class InstitutionProfile(db.Model):
    __tablename__ = 'institution_profiles'

    email = db.Column(db.String(120), db.ForeignKey('users.email'), primary_key=True)

    institution_name = db.Column(db.String(100))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    sector = db.Column(db.String(50))  # educativo, salud, etc.
    address = db.Column(db.String(100))
    description = db.Column(db.Text)
