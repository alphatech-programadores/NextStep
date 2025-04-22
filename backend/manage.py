from app import create_app
from extensions import db, migrate
from models import user, student_profile, institution_profile, application, vacant

app = create_app()

migrate.init_app(app, db)
