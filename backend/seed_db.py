# seed_db.py
from app import create_app 
from extensions import db   
from models.application import Application
from models.user import Role, User
from models.student_profile import StudentProfile 
from models.vacant import Vacant
from models.institution_profile import InstitutionProfile
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

# Datos de prueba
# Asegúrate de que los emails y nombres/company_names sean únicos si los usas como PK/FK
STUDENT_USERS_DATA = [
    {"email": "estudiante1@example.com", "name": "Ana García", "password": "password123", "career": "Ingeniería en Software", "semestre": 5, "average": 9.2, "phone": "5512345678", "address": "Calle Falsa 123", "availability": "Tiempo Completo", "skills": "React, JavaScript, Node.js, SQL", "portfolio_url": "https://anagarcia.dev", "cv_path": "/cvs/ana_garcia_cv.pdf"},
    {"email": "estudiante2@example.com", "name": "Luis Pérez", "password": "password123", "career": "Ciencias de Datos", "semestre": 7, "average": 8.8, "phone": "5587654321", "address": "Av. Siempreviva 742", "availability": "Medio Tiempo", "skills": "Python, Pandas, Machine Learning, SQL", "portfolio_url": "https://luisperez.com", "cv_path": "/cvs/luis_perez_cv.pdf"},
    {"email": "estudiante3@example.com", "name": "Sofía Rodríguez", "password": "password123", "career": "Diseño Gráfico", "semestre": 3, "average": 9.5, "phone": "5511223344", "address": "Blvd. del Sol 50", "availability": "Presencial", "skills": "Figma, Photoshop, Illustrator, UI/UX", "portfolio_url": "https://sofiar.art", "cv_path": "/cvs/sofia_rodriguez_cv.pdf"},
]

INSTITUTION_USERS_DATA = [
    {"email": "institucion1@example.com", "institution_name": "Tech Solutions S.A.", "contact_person": "Carlos Gomez", "contact_phone": "5510002000", "sector": "Tecnología", "address": "Vasco de Quiroga 2000", "description": "Líderes en desarrollo de software y soluciones IT.", "password": "password123"},
    {"email": "institucion2@example.com", "institution_name": "Data Insights Corp.", "contact_person": "Maria Lopez", "contact_phone": "5530004000", "sector": "Consultoría", "address": "Av. Insurgentes Sur 1500", "description": "Consultoría especializada en Big Data y analítica avanzada.", "password": "password123"},
    {"email": "institucion3@example.com", "institution_name": "Creative Agency", "contact_person": "Roberto Sanchez", "contact_phone": "5550006000", "sector": "Publicidad", "address": "Roma Norte 10", "description": "Agencia de publicidad innovadora con enfoque en branding digital.", "password": "password123"},
]

VACANTS_DATA = [
    {
        "area": "Desarrollo Frontend",
        "description": "Buscamos un desarrollador frontend apasionado por crear interfaces de usuario intuitivas y atractivas para nuestras aplicaciones web.",
        "hours": "Tiempo completo (40 hrs/semana)",
        "modality": "Híbrido", # presencial, híbrido, remoto
        "requirements": "Experiencia con React.js, JavaScript (ES6+), HTML5, CSS3 (Sass/Less). Conocimientos de Git. Experiencia con herramientas de diseño (Figma/Sketch) es un plus.",
        "location": "Ciudad de México",
        "tags": "React,JavaScript,Frontend,Web,Híbrido",
        "start_date_days": -10, # Empezó hace 10 días
        "end_date_days": 30, # Termina en 30 días
        "institution_email": "institucion1@example.com"
    },
    {
        "area": "Análisis de Datos",
        "description": "Oportunidad para un analista de datos junior con interés en el análisis de grandes volúmenes de información para insights de negocio.",
        "hours": "Tiempo completo (40 hrs/semana)",
        "modality": "Presencial",
        "requirements": "Dominio de SQL, Python (Pandas, NumPy), Excel. Conocimientos básicos de estadística y visualización de datos (Tableau/Power BI).",
        "location": "Ciudad de México",
        "tags": "Python,SQL,Data Analysis,BI,Presencial",
        "start_date_days": -5,
        "end_date_days": 45,
        "institution_email": "institucion2@example.com"
    },
    {
        "area": "Diseño UI/UX",
        "description": "Únete a nuestro equipo creativo para diseñar experiencias de usuario excepcionales y interfaces intuitivas para nuestras plataformas digitales.",
        "hours": "Medio tiempo (20 hrs/semana)",
        "modality": "Remoto",
        "requirements": "Manejo experto de Figma o Adobe XD. Conocimientos sólidos de principios de UI/UX, investigación de usuarios, wireframing y prototipado.",
        "location": "Remoto",
        "tags": "UI/UX,Figma,Design,Remoto,Part-time",
        "start_date_days": -20,
        "end_date_days": 20,
        "institution_email": "institucion3@example.com"
    },
    {
        "area": "Marketing Digital",
        "description": "Apoya en la creación, implementación y gestión de campañas de marketing digital para nuestras diversas marcas.",
        "hours": "Tiempo completo (40 hrs/semana)",
        "modality": "Híbrido",
        "requirements": "Conocimientos de SEO, SEM, redes sociales, Google Analytics. Habilidades de redacción y creatividad.",
        "location": "Guadalajara",
        "tags": "Marketing,Digital,SEO,SEM,Híbrido",
        "start_date_days": -7,
        "end_date_days": 25,
        "institution_email": "institucion1@example.com"
    },
    {
        "area": "Desarrollo Backend",
        "description": "Buscamos un desarrollador backend experimentado en Python para construir y mantener APIs robustas y escalables.",
        "hours": "Tiempo completo (40 hrs/semana)",
        "modality": "Remoto",
        "requirements": "Experiencia con Python, Flask o Django, bases de datos relacionales (PostgreSQL), desarrollo de REST APIs. Conocimientos de Docker y cloud computing son un plus.",
        "location": "Remoto",
        "tags": "Python,Backend,API,Flask,Remoto",
        "start_date_days": -15,
        "end_date_days": 60,
        "institution_email": "institucion2@example.com"
    },
]

def seed_data():
    with app.app_context():
        db.drop_all() # ¡CUIDADO! Esto borrará todos los datos existentes
        db.create_all()

        print("Base de datos limpia y recreada.")

        # Crear roles si no existen
        student_role = Role.query.filter_by(name="student").first()
        if not student_role:
            student_role = Role(name="student")
            db.session.add(student_role)

        institution_role = Role.query.filter_by(name="institution").first()
        if not institution_role:
            institution_role = Role(name="institution")
            db.session.add(institution_role)
        
        db.session.commit()
        print("Roles 'student' e 'institution' asegurados.")

        # Crear usuarios y sus perfiles
        users = {} # Para almacenar usuarios por email para referencia
        
        # Estudiantes
        for s_data in STUDENT_USERS_DATA:
            hashed_password = generate_password_hash(s_data["password"])
            user = User(
                email=s_data["email"],
                password_hash=hashed_password,
                name=s_data["name"],
                role=student_role, # Asigna el objeto Role
                is_confirmed=True # Confirmados por defecto para pruebas
            )
            db.session.add(user)
            users[s_data["email"]] = user # Guardar en diccionario para referencia

            student_profile = StudentProfile(
                email=s_data["email"],
                career=s_data["career"],
                semestre=s_data["semestre"],
                average=s_data["average"],
                phone=s_data["phone"],
                address=s_data["address"],
                availability=s_data["availability"],
                skills=s_data["skills"],
                portfolio_url=s_data["portfolio_url"],
                cv_path=s_data["cv_path"]
            )
            db.session.add(student_profile)
        print(f"Creados {len(STUDENT_USERS_DATA)} usuarios estudiantes y sus perfiles.")

        # Instituciones
        for i_data in INSTITUTION_USERS_DATA:
            hashed_password = generate_password_hash(i_data["password"])
            user = User(
                email=i_data["email"],
                password_hash=hashed_password,
                name=i_data["institution_name"], # Usar institution_name como 'name' del User
                role=institution_role, # Asigna el objeto Role
                is_confirmed=True # Confirmados por defecto para pruebas
            )
            db.session.add(user)
            users[i_data["email"]] = user # Guardar en diccionario para referencia

            institution_profile = InstitutionProfile(
                email=i_data["email"],
                institution_name=i_data["institution_name"],
                contact_person=i_data["contact_person"],
                contact_phone=i_data["contact_phone"],
                sector=i_data["sector"],
                address=i_data["address"],
                description=i_data["description"]
            )
            db.session.add(institution_profile)
        print(f"Creados {len(INSTITUTION_USERS_DATA)} usuarios instituciones y sus perfiles.")

        db.session.commit() # Guardar usuarios y perfiles para poder referenciarlos por email

        # Crear vacantes
        vacants = []
        for v_data in VACANTS_DATA:
            institution_user = users.get(v_data["institution_email"])
            if institution_user and institution_user.role.name == "institution":
                start_date = datetime.utcnow() + timedelta(days=v_data["start_date_days"])
                end_date = datetime.utcnow() + timedelta(days=v_data["end_date_days"])
                
                vacant = Vacant(
                    area=v_data["area"],
                    description=v_data["description"],
                    hours=v_data["hours"],
                    modality=v_data["modality"],
                    requirements=v_data["requirements"],
                    status="activa", # Por defecto activa
                    start_date=start_date.date(), # Solo la fecha
                    end_date=end_date.date(), # Solo la fecha
                    location=v_data["location"],
                    tags=v_data["tags"],
                    is_draft=False,
                    last_modified=datetime.utcnow(),
                    institution_email=v_data["institution_email"]
                )
                db.session.add(vacant)
                vacants.append(vacant)
            else:
                print(f"Advertencia: Institución '{v_data['institution_email']}' no encontrada o no es una institución. Vacante '{v_data['area']}' no creada.")
        print(f"Creadas {len(vacants)} vacantes.")

        db.session.commit() # Guardar vacantes

        # Crear algunas postulaciones de ejemplo (opcional)
        # Asegúrate de que los emails de estudiantes y IDs de vacantes existan
        student1_email = STUDENT_USERS_DATA[0]["email"]
        student2_email = STUDENT_USERS_DATA[1]["email"]
        
        if student1_email in users and vacants:
            app1 = Application(
                student_email=student1_email,
                vacant_id=vacants[0].id, # Postular a la primera vacante creada
                status="pendiente",
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(app1)
            print("Creada postulación de estudiante1 a vacante1.")

        if student2_email in users and len(vacants) > 1:
            app2 = Application(
                student_email=student2_email,
                vacant_id=vacants[1].id, # Postular a la segunda vacante creada
                status="revisada",
                created_at=datetime.utcnow() - timedelta(days=7)
            )
            db.session.add(app2)
            print("Creada postulación de estudiante2 a vacante2.")
        
        db.session.commit()

        print("¡Base de datos poblada exitosamente!")

if __name__ == '__main__':
    seed_data()
