from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db
from models.vacant import Vacant
from models.application import Application
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from utils import session_validated

vacants_bp = Blueprint("vacants", __name__)

# Crear vacante
@vacants_bp.route("/", methods=["POST"])
@jwt_required()
@session_validated
def create_vacant():
    current_user = User.query.get(get_jwt_identity())

    if current_user.role.name != "institution":
        return jsonify({"error": "Solo instituciones pueden crear vacantes."}), 403

    data = request.get_json()

    try:
        start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else None
        end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else None
    except ValueError:
        return jsonify({"error": "Fechas mal formateadas. Usa YYYY-MM-DD."}), 400

    vacant = Vacant(
        area=data.get("area"),
        hours=data.get("hours"),
        modality=data.get("modality"),
        start_date=start_date,
        end_date=end_date,
        description=data.get("description"),
        requirements=data.get("requirements"),
        status=data.get("status", "activa"),

        # Nuevos campos:
        location=data.get("location", ""),
        tags=data.get("tags", ""),  # espera string tipo "Python,Remoto"
        is_draft=data.get("is_draft", False),

        institution_email=current_user.email
    )

    db.session.add(vacant)
    db.session.commit()
    return jsonify({"message": "Vacante creada exitosamente."}), 201


# Listar vacantes
@vacants_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
@session_validated
def list_vacants():
    identity = get_jwt_identity()
    user = User.query.get(identity) if identity else None

    # Estudiantes con vacante ya aceptada no pueden ver más
    if user and user.role.name == "student":
        accepted = Application.query.filter_by(student_email=user.email, status="aceptado").first()
        if accepted:
            return jsonify([])

    # Solo vacantes activas y no borrador
    vacants = Vacant.query.filter_by(status="activa", is_draft=False).all()
    filtered = []

    for v in vacants:
        accepted = Application.query.filter_by(vacant_id=v.id, status="aceptado").first()
        if not accepted:
            filtered.append(v)

    return jsonify([
        {
            "id": v.id,
            "area": v.area,
            "description": v.description,
            "hours": v.hours,
            "modality": v.modality,
            "location": v.location,
            "tags": v.tags,
            "institution_email": v.institution_email
        }
        for v in filtered
    ])

# Actualizar una vacante
@vacants_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@session_validated
def update_vacant(id):
    vacant = Vacant.query.get_or_404(id)
    current_user = User.query.get(get_jwt_identity())

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para modificar esta vacante."}), 403

    data = request.get_json()

    try:
        start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else vacant.start_date
        end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else vacant.end_date
    except ValueError:
        return jsonify({"error": "Fechas mal formateadas. Usa YYYY-MM-DD."}), 400

    # Actualización completa
    vacant.area = data.get("area", vacant.area)
    vacant.hours = data.get("hours", vacant.hours)
    vacant.description = data.get("description", vacant.description)
    vacant.modality = data.get("modality", vacant.modality)
    vacant.start_date = start_date
    vacant.end_date = end_date
    vacant.status = data.get("status", vacant.status)
    vacant.requirements = data.get("requirements", vacant.requirements)

    # Nuevos campos:
    vacant.location = data.get("location", vacant.location)
    vacant.tags = data.get("tags", vacant.tags)
    vacant.is_draft = data.get("is_draft", vacant.is_draft)

    db.session.commit()
    return jsonify({"message": "Vacante actualizada correctamente."})



# Eliminar vacante
@vacants_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@session_validated
def delete_vacant(id):
    vacant = Vacant.query.get_or_404(id)
    current_user = User.query.get(get_jwt_identity())

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para eliminar esta vacante."}), 403

    db.session.delete(vacant)
    db.session.commit()
    return jsonify({"message": "Vacante eliminada."})

# Buscar vacante
@vacants_bp.route("/search", methods=["GET"])
def search_vacants():
    area = request.args.get("area")
    modality = request.args.get("modality")
    location = request.args.get("location")
    tag = request.args.get("tag")
    keyword = request.args.get("q")

    query = Vacant.query.filter_by(status="activa", is_draft=False)

    if area:
        query = query.filter(Vacant.area.ilike(f"%{area}%"))
    if modality:
        query = query.filter(Vacant.modality.ilike(f"%{modality}%"))
    if location:
        query = query.filter(Vacant.location.ilike(f"%{location}%"))
    if tag:
        query = query.filter(Vacant.tags.ilike(f"%{tag}%"))
    if keyword:
        query = query.filter(
            Vacant.description.ilike(f"%{keyword}%") |
            Vacant.requirements.ilike(f"%{keyword}%") |
            Vacant.area.ilike(f"%{keyword}%")
        )

    results = query.all()

    return jsonify([
        {
            "id": v.id,
            "area": v.area,
            "description": v.description,
            "hours": v.hours,
            "modality": v.modality,
            "location": v.location,
            "tags": v.tags,
            "institution_email": v.institution_email
        }
        for v in results
    ])
