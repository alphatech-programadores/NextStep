from app import create_app
from extensions import db, migrate
from models import user, student_profile, institution_profile, application, vacant
from dotenv import load_dotenv
load_dotenv()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


app = create_app()

migrate.init_app(app, db)

import click
from flask.cli import with_appcontext

@app.cli.command("clean-students")
@with_appcontext
def clean_students():
    """Elimina todos los usuarios de tipo student y sus perfiles."""
    from models.user import User
    from models.student_profile import StudentProfile
    from extensions import db

    students = User.query.join(StudentProfile, StudentProfile.email == User.email).all()

    for student in students:
        db.session.delete(student)

    db.session.commit()
    click.echo("✅ Se eliminaron todos los usuarios tipo student.")
