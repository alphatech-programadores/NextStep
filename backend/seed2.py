# backend/seed_db.py

from app import create_app
from extensions import db
from models.user import User
from models.role import Role
from models.institution_profile import InstitutionProfile
from models.vacant import Vacant
from models.student_profile import StudentProfile

import random
import os

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
    instituciones_data = [
        {"name": "TechCorp Solutions", "sector": "Tecnología", "contact_person": "Carlos Ruiz", "contact_phone": "5551234567", "address": "Av. Siempre Viva 123", "description": "Líder en desarrollo de software y IA.", "website": "https://techcorp.com", "email_suffix": "techcorp.com"},
        {"name": "BioHealth Innovators", "sector": "Salud y Biotecnología", "contact_person": "María Pérez", "contact_phone": "5559876543", "address": "Calle Salud 456", "description": "Pioneros en investigación farmacéutica y biológica.", "website": "https://biohealth.com", "email_suffix": "biohealth.com"},
        {"name": "Global Marketing Agency", "sector": "Marketing Digital", "contact_person": "Juan García", "contact_phone": "5551112233", "address": "Blvd. Creativo 789", "description": "Estrategias innovadoras para el mercado digital.", "website": "https://globalmarketing.com", "email_suffix": "globalmarketing.com"},
        {"name": "EduTech Learning", "sector": "Educación y Tecnología", "contact_person": "Ana López", "contact_phone": "5554445566", "address": "Paseo del Saber 101", "description": "Plataformas educativas interactivas.", "website": "https://edutech.com", "email_suffix": "edutech.com"},
        {"name": "GreenEnergy Solutions", "sector": "Energías Renovables", "contact_person": "Pedro Martínez", "contact_phone": "5557778899", "address": "Av. Sostenible 202", "description": "Desarrollo e implementación de soluciones energéticas limpias.", "website": "https://greenenergy.com", "email_suffix": "greenenergy.com"},
    ]

    institution_profiles = []
    for i, data in enumerate(instituciones_data):
        user_email = f"institucion{i+1}@{data['email_suffix']}"
        institucion_user = User(
            email=user_email,
            name=data['name'],
            role=institution_role,
            is_confirmed=True
        )
        institucion_user.set_password("password123") # Contraseña genérica para pruebas
        profile = InstitutionProfile(
            email=institucion_user.email,
            institution_name=data['name'],
            sector=data['sector'],
            contact_person=data['contact_person'],
            contact_phone=data['contact_phone'],
            address=data['address'],
            description=data['description'],
            website=data['website']
        )
        institucion_user.institution_profile = profile
        db.session.add(institucion_user)
        institution_profiles.append(profile)
    db.session.commit()

    print("📢 Creando vacantes...")
    vacantes_data = [
        # Vacantes de Tecnología
        {"area": "Desarrollador Frontend", "description": "Construcción de interfaces de usuario con React y Next.js.", "requirements": "React, JavaScript, HTML, CSS, Next.js, Git, REST APIs", "hours": "40 horas", "modality": "Remoto", "location": "CDMX", "tags": "frontend,react,javascript", "institution_idx": 0},
        {"area": "Ingeniero Backend Python", "description": "Desarrollo de APIs RESTful y microservicios con Flask y SQLAlchemy.", "requirements": "Python, Flask, SQLAlchemy, REST APIs, Bases de datos SQL, Docker, Git", "hours": "40 horas", "modality": "Híbrido", "location": "Guadalajara", "tags": "backend,python,flask", "institution_idx": 0},
        {"area": "Científico de Datos Jr.", "description": "Análisis de datos, modelado predictivo y visualización.", "requirements": "Python, Pandas, NumPy, Scikit-learn, SQL, Estadística, Machine Learning", "hours": "35 horas", "modality": "Presencial", "location": "Monterrey", "tags": "data science,python,machine learning", "institution_idx": 0},
        {"area": "Especialista en Ciberseguridad", "description": "Monitoreo y protección de sistemas contra amenazas cibernéticas.", "requirements": "Seguridad de redes, Análisis de vulnerabilidades, ISO 27001, Ethical Hacking", "hours": "40 horas", "modality": "Presencial", "location": "CDMX", "tags": "ciberseguridad,redes", "institution_idx": 0},

        # Vacantes de Salud y Biotecnología
        {"area": "Investigador de Laboratorio", "description": "Diseño y ejecución de experimentos en biología molecular.", "requirements": "Biología molecular, PCR, Cultivo celular, Análisis de datos, Redacción científica", "hours": "40 horas", "modality": "Presencial", "location": "Querétaro", "tags": "biotecnologia,investigacion", "institution_idx": 1},
        {"area": "Químico Analítico", "description": "Análisis de muestras químicas utilizando técnicas avanzadas.", "requirements": "Química analítica, HPLC, Cromatografía, Espectroscopia, Control de calidad", "hours": "38 horas", "modality": "Presencial", "location": "Puebla", "tags": "quimica,laboratorio", "institution_idx": 1},

        # Vacantes de Marketing Digital
        {"area": "Estratega de Contenidos", "description": "Creación y gestión de contenido para campañas digitales.", "requirements": "Marketing de contenidos, SEO, Copywriting, Redes sociales, Google Analytics", "hours": "30 horas", "modality": "Remoto", "location": "CDMX", "tags": "marketing,contenido,seo", "institution_idx": 2},
        {"area": "Analista de Marketing Digital", "description": "Medición y optimización de campañas publicitarias online.", "requirements": "Google Ads, Facebook Ads, Análisis de datos, Excel, Estrategia digital", "hours": "40 horas", "modality": "Híbrido", "location": "Guadalajara", "tags": "marketing,analisis,publicidad", "institution_idx": 2},

        # Vacantes de Educación y Tecnología
        {"area": "Diseñador Instruccional", "description": "Desarrollo de materiales didácticos para plataformas e-learning.", "requirements": "Diseño instruccional, Moodle, SCORM, EdTech, Pedagogía", "hours": "30 horas", "modality": "Remoto", "location": "CDMX", "tags": "educacion,elearning", "institution_idx": 3},

        # Vacantes de Energías Renovables
        {"area": "Ingeniero Solar", "description": "Diseño e instalación de sistemas de energía solar fotovoltaica.", "requirements": "Energía solar, Fotovoltaica, AutoCAD, Gestión de proyectos, Normativa energética", "hours": "40 horas", "modality": "Presencial", "location": "Hermosillo", "tags": "energia,solar", "institution_idx": 4},
    ]

    vacants_created = []
    for data in vacantes_data:
        vacant = Vacant(
            area=data["area"],
            description=data["description"],
            requirements=data["requirements"],
            hours=data["hours"],
            modality=data["modality"],
            location=data["location"],
            tags=data["tags"],
            institution_profile=institution_profiles[data["institution_idx"]],
            status="activa",
            is_draft=False
        )
        db.session.add(vacant)
        vacants_created.append(vacant)
    db.session.commit()

    print("🎓 Creando estudiantes con habilidades variadas...")
    student_skills_pool = {
        "web_dev": ["React", "JavaScript", "HTML", "CSS", "Next.js", "Node.js", "SQL", "Git", "REST APIs", "frontend", "backend"],
        "data_science": ["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Estadística", "SQL", "Análisis de datos", "Jupyter Notebooks"],
        "bio_chem": ["Biología molecular", "Química analítica", "PCR", "Cultivo celular", "Análisis de laboratorio", "Cromatografía", "Espectroscopia"],
        "marketing": ["Marketing de contenidos", "SEO", "Copywriting", "Redes sociales", "Google Analytics", "Google Ads", "Facebook Ads", "Estrategia digital"],
        "general": ["Comunicación", "Trabajo en equipo", "Resolución de problemas", "Liderazgo", "Proactividad", "Adaptabilidad"]
    }

    careers = ["Ingeniería en Sistemas Computacionales", "Biología", "Química", "Mercadotecnia", "Diseño Gráfico", "Ingeniería Ambiental", "Ciencias de la Computación"]

    for i in range(20): # Crear 20 estudiantes para mayor diversidad
        student_email = f"estudiante{i+1}@mail.com"
        student_user = User(
            email=student_email,
            name=f"Estudiante {i+1}",
            role=student_role,
            is_confirmed=True
        )
        student_user.set_password("password123") # Contraseña genérica para pruebas

        # Asignar habilidades de forma más inteligente para crear coincidencias
        chosen_skills = []
        if i % 4 == 0: # 25% de los estudiantes con habilidades de desarrollo web
            chosen_skills.extend(random.sample(student_skills_pool["web_dev"], k=random.randint(3, 6)))
            career = "Ingeniería en Sistemas Computacionales"
        elif i % 4 == 1: # 25% de los estudiantes con habilidades de ciencia de datos
            chosen_skills.extend(random.sample(student_skills_pool["data_science"], k=random.randint(3, 6)))
            career = "Ciencias de la Computación"
        elif i % 4 == 2: # 25% de los estudiantes con habilidades de bio/química
            chosen_skills.extend(random.sample(student_skills_pool["bio_chem"], k=random.randint(3, 5)))
            career = random.choice(["Biología", "Química"])
        else: # 25% de los estudiantes con habilidades de marketing o generales
            chosen_skills.extend(random.sample(student_skills_pool["marketing"] + student_skills_pool["general"], k=random.randint(2, 5)))
            career = random.choice(["Mercadotecnia", "Diseño Gráfico"])

        # Añadir algunas habilidades generales a todos
        chosen_skills.extend(random.sample(student_skills_pool["general"], k=random.randint(1, 2)))
        chosen_skills = list(set(chosen_skills)) # Eliminar duplicados y convertir a lista
        random.shuffle(chosen_skills) # Mezclar para que no siempre salgan en el mismo orden
        skills_str = ", ".join(chosen_skills)

        student_profile = StudentProfile(
            email=student_user.email,
            career=career,
            semestre=random.randint(1, 10),
            skills=skills_str
        )
        student_user.student_profile = student_profile
        db.session.add(student_user)

    db.session.commit()
    print("✅ Base de datos inicializada con datos de prueba mejorados.")

