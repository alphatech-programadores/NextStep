# backend/app.py

import os
from flask import Flask, jsonify, current_app, send_from_directory
from config import Config
from flask_cors import CORS
from extensions import db, jwt, mail, migrate
# import recommender
from routes.institution_profile_routes import inst_profile_bp
from routes.auth import auth_bp
from routes.vacants import vacants_bp
from routes.application import app_bp # Asumo que este es el de Application
from routes.profile import profile_bp
# from routes.recommendation import recommend_bp # <-- ¡COMENTA ESTA LÍNEA!
from datetime import timedelta
from werkzeug.utils import secure_filename
import triggers.user_trigger
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config.from_object(Config)

    print(f"\n--- DEBUG_APP_CONFIG ---")
    print(f"DEBUG_APP_CONFIG: UPLOAD_FOLDER configurado a: {app.config['UPLOAD_FOLDER']}")
    print(f"DEBUG_APP_CONFIG: current_app.root_path (raíz de la app Flask) es: {app.root_path}")
    print(f"--- FIN DEBUG_APP_CONFIG ---\n")

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(vacants_bp, url_prefix="/api/vacants")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(app_bp, url_prefix="/api/apply")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(inst_profile_bp) 
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder_path = os.path.join(current_app.root_path, 'uploads')
        
        # AÑADE ESTAS LÍNEAS:
        print(f"--- DEBUG_SERVE ---")
        print(f"DEBUG_SERVE: Recibida solicitud para servir archivo: {filename}") 
        print(f"DEBUG_SERVE: Intentando servir desde directorio: {upload_folder_path}") 
        # Asegúrate de que esta línea esté, es la que sirve el archivo
        response = send_from_directory(upload_folder_path, filename)
        print(f"DEBUG_SERVE: Servidor intentó responder para {filename}. Estado: {response.status_code}")
        print(f"--- FIN DEBUG_SERVE ---") # Marcar el final del debug
        return response
    # app.register_blueprint(recommender, url_prefix="/api/recommendations") # <-- ¡COMENTA ESTA LÍNEA!



    @app.route("/")
    def home():
        return jsonify({"msg": "NextStep API funcionando 👌"})

    CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",           # Si tienes frontend local
    "http://127.0.0.1:3000",
    "http://10.0.2.2:5000",            # Tu emulador accediendo a tu host Flask
    "http://10.0.2.2:3000",            # Si tu front corre en otro puerto en emulador
    ])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)