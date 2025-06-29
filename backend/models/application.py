# models/application.py
from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String, db.ForeignKey('users.email'), nullable=False)
    vacant_id = db.Column(db.Integer, db.ForeignKey('vacants.id'), nullable=False)
    status = db.Column(db.String(20), default="pendiente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text, nullable=True)

 
    # Permite hacer `application.student`
    student = db.relationship("User", back_populates="applications")

    # Permite hacer `application.vacant`
    vacant = db.relationship("Vacant", back_populates="applications")
