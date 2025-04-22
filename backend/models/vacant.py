from extensions import db
# models/vacant.py
from datetime import date

class Vacant(db.Model):
    __tablename__ = 'vacants'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(50), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    modality = db.Column(db.String(30))  # remota, presencial, híbrida
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)  # texto libre o JSON
    status = db.Column(db.String(20), default="abierta")  # abierta, cerrada

    institution_email = db.Column(db.String, db.ForeignKey('users.email'), nullable=False)
