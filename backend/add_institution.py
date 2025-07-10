from app import create_app
from extensions import db
from models.user import Role, User
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile

app = create_app()

with app.app_context():
    db.create_all()

    # Crear roles
    for role_name in ["student", "institution", "admin"]:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()

    # Crear usuario tipo institución
    if not User.query.get("cecyt9@ipn.mx"):
        role = Role.query.filter_by(name="institution").first()
        inst = User(email="cecyt9@ipn.mx", name="CECyT 9", role_id=role.id)
        inst.set_password("cecyt9seguro123")
        db.session.add(inst)
        db.session.add(InstitutionProfile(
            email=inst.email,
            institution_name="CECyT 9",
            contact_person="Mtro. Jorge P.",
            contact_phone="555-123-4567",
            sector="educativo",
            address="CDMX",
            description="Centro de estudios nivel medio superior del IPN."
        ))
        db.session.commit()

    print("Base de datos inicializada y poblada.")
