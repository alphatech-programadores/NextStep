# routes/application.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.application import Application
from models.vacant import Vacant
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

app_bp = Blueprint("applications", __name__)

@app_bp.route("/<int:vacant_id>", methods=["POST", "OPTIONS"])
@jwt_required()
def apply_to_vacant(vacant_id):
    current_user = User.query.get(get_jwt_identity())

    if current_user.role.name != "student":
        return jsonify({"error": "Solo los estudiantes pueden postularse."}), 403

    existing = Application.query.filter_by(student_email=current_user.email, vacant_id=vacant_id).first()
    if existing:
        return jsonify({"message": "Ya estás postulado a esta vacante."}), 409

    accepted = Application.query.filter_by(student_email=current_user.email, status="aceptado").first()
    if accepted:
        return jsonify({"error": "Ya fuiste aceptado a una vacante. No puedes postularte a otra."}), 403

    application = Application(
        student_email=current_user.email,
        vacant_id=vacant_id,
        status="pendiente"
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Postulación enviada correctamente."}), 201


@app_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_applications():
    current_user = User.query.get(get_jwt_identity())
    apps = Application.query.filter_by(student_email=current_user.email).all()

    return jsonify([
        {
            "id": app.id,
            "vacant_id": app.vacant_id,
            "status": app.status,
            "fecha": app.created_at.isoformat()
        }
        for app in apps
    ])

@app_bp.route("/vacant/<int:vacant_id>", methods=["GET"])
@jwt_required()
def get_applications_for_vacant(vacant_id):
    current_user = User.query.get(get_jwt_identity())
    vacant = Vacant.query.get_or_404(vacant_id)

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para ver estas postulaciones."}), 403

    apps = Application.query.filter_by(vacant_id=vacant_id).all()

    return jsonify([
        {
            "id": app.id,
            "student_email": app.student_email,
            "status": app.status,
            "fecha": app.created_at.isoformat()
        }
        for app in apps
    ])


@app_bp.route("/<int:application_id>", methods=["PUT"])
@jwt_required()
def update_application_status(application_id):
    current_user = User.query.get(get_jwt_identity())
    app = Application.query.get_or_404(application_id)
    vacant = Vacant.query.get(app.vacant_id)

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para actualizar esta postulación."}), 403

    data = request.get_json()
    new_status = data.get("status", "").lower()

    if new_status not in ["pendiente", "aceptado", "rechazado"]:
        return jsonify({"error": "Estado inválido."}), 400

    app.status = new_status
    db.session.commit()
    return jsonify({"message": "Estado actualizado correctamente."}), 200

