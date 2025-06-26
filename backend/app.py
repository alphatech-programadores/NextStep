from flask import Flask, jsonify
from config import Config
from flask_cors import CORS
from extensions import db, jwt, mail, migrate
from routes.auth import auth_bp
from routes.vacants import vacants_bp
from routes.application import app_bp
from routes.profile import profile_bp
from routes.recommendation import recommend_bp
from datetime import timedelta
import triggers.user_trigger
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt.init_app(app)
    app.config.from_object(Config)
    

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(vacants_bp, url_prefix="/api/vacants")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(app_bp, url_prefix="/api/apply")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(recommend_bp, url_prefix="/api/recommendations")

    @app.route("/")
    def home():
        return jsonify({"msg": "NextStep API funcionando 👌"})
    
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    return app

if __name__ == "__main__":
    app = create_app()

    from models.user import User, Role
    from models.vacant import Vacant
    from models.application import Application
    from models.student_profile import StudentProfile
    from models.institution_profile import InstitutionProfile

    with app.app_context():
        db.create_all()

    app.run(debug=True)
