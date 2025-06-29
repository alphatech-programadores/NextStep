# models/user.py
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # --- RELACIÓN CORREGIDA ---
    # La relación se define aquí y se vincula a 'role' en el modelo User.
    # Reemplazamos el `backref` con `back_populates`.
    users = db.relationship('User', back_populates='role')