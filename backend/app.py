# backend/app.py

#System
import os
from flask import Flask, jsonify, current_app, send_from_directory
from config import Config
from flask_cors import CORS
from extensions import db, jwt, mail, migrate
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
# import recommender

# Routes
from routes.institution_profile_routes import inst_profile_bp
from routes.auth import auth_bp
from routes.vacants import vacants_bp
from routes.application import app_bp
from routes.profile import profile_bp
from routes.notifications import notification_bp
from routes.saved_vacancies_routes import saved_vacancies_bp 
# Por implementar
# from routes.recommendation import recommend_bp 


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads') 
    upload_folder_path = app.config['UPLOAD_FOLDER']

    # Asegurarse de que los directorios de subida existen
    os.makedirs(os.path.join(upload_folder_path, 'cvs'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder_path, 'profile_pics'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder_path, 'logos'), exist_ok=True)



    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all() # Esto creará las tablas si no existen

    app.register_blueprint(vacants_bp, url_prefix="/api/vacants")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(app_bp, url_prefix="/api/apply")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(inst_profile_bp) 
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")
    app.register_blueprint(saved_vacancies_bp)
    # Por implementar
    # app.register_blueprint(recommender, url_prefix="/api/recommendations")
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        response = send_from_directory(upload_folder_path, filename)
        return response

    @app.route("/")
    def home():
        return jsonify({"msg": "NextStep API funcionando 👌"})

    CORS(app, supports_credentials=True, resources = {r"/api/*": { "origins": "*" } } )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)