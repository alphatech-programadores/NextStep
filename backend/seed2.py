from app import create_app
from extensions import db
from models.user import User
from models.role import Role
from models.institution_profile import InstitutionProfile
from models.vacant import Vacant
from models.student_profile import StudentProfile

import random

app = create_app()

with app.app_context():
    print("🧹 Borrando datos anteriores...")
    db.drop_all()
    db.create_all()

    print("🌱 Creando roles...")
    student_role = Role(name="student")
    institution_role = Role(name="institution")
    db.session.add_all([student_role, institution_role])
    db.session.commit()

    print("🏫 Creando instituciones...")
    institucion1 = User(
        email="institucion1@ejemplo.com",
        name="Instancia Uno",
        role=institution_role,
        is_confirmed = True)
    institucion1.set_password("test123")
    profile1 = InstitutionProfile(
        email=institucion1.email,
        institution_name="TechCorp",
        sector="Tecnología",
        contact_person="Carlos Ruiz",
        contact_phone="5551234567",
        address="Av. Siempre Viva 123",
        description="Empresa de tecnología avanzada.",
        website="https://techcorp.com"
    )
    institucion1.institution_profile = profile1

    institucion2 = User(email="institucion2@ejemplo.com", name="Instancia Dos", role=institution_role, is_confirmed = True)
    institucion2.set_password("test123")
    profile2 = InstitutionProfile(
        email=institucion2.email,
        institution_name="BioLife",
        sector="Salud",
        contact_person="María Pérez",
        contact_phone="5559876543",
        address="Calle Salud 456",
        description="Clínica especializada en biotecnología.",
        website="https://biolife.com"
    )
    institucion2.institution_profile = profile2

    db.session.add_all([institucion1, institucion2])
    db.session.commit()

    print("📢 Creando vacantes...")
    vacantes = [
        Vacant(area="Desarrollador Web", description="Desarrollar interfaces en React.", requirements="HTML, CSS, JS", hours="20 horas", modality="Remoto", location="CDMX", tags="react,frontend", institution_profile=profile1),
        Vacant(area="Asistente de Laboratorio", description="Ayuda en el área de análisis clínicos.", requirements="Química básica", hours="30 horas", modality="Presencial", location="Guadalajara", tags="química,salud", institution_profile=profile2)
    ]
    db.session.add_all(vacantes)

    print("🎓 Creando estudiantes...")
    for i in range(5):
        student = User(email=f"estudiante{i}@mail.com", name=f"Estudiante {i}", role=student_role, is_confirmed = True)
        student.set_password("test123")
        skills_list = ["trabajo en equipo", "python", "investigación"]
        skills = ", ".join(skills_list[:random.randint(1, 3)])
        student_profile = StudentProfile(
            email=student.email,
            career=random.choice(["Ingeniería", "Biología", "Sistemas"]),
            semestre=random.randint(1, 10),
                skills=skills
        )
        student.student_profile = student_profile
        db.session.add(student)

    db.session.commit()
    print("✅ Base de datos inicializada.")
