from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db
from models.student_profile import StudentProfile
from models.vacant import Vacant
from models.application import Application
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.metrics.pairwise import cosine_similarity
from utils import session_validated
#import nltk
#nltk.download('punkt')


vacants_bp = Blueprint("vacants", __name__)

# Crear vacante
@vacants_bp.route("/", methods=["POST"])
@jwt_required()
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

# ...
@vacants_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def list_vacants():
    identity = get_jwt_identity()
    user = User.query.get(identity) if identity else None

    query = Vacant.query.filter_by(status="activa", is_draft=False)

    # Si es estudiante y ya fue aceptado en una vacante, no mostrarle más
    if user and user.role.name == "student":
        accepted = Application.query.filter_by(student_email=user.email, status="aceptado").first()
        if accepted:
            return jsonify([])

    vacants = query.all()

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
        for v in vacants
    ])


# Listar vacantes de la institución consultante.
@vacants_bp.route("/my", methods=["GET"])
@jwt_required()
def list_my_vacants():
    current_user = User.query.get(get_jwt_identity())

    if current_user.role.name != "institution":
        return jsonify({"error": "Solo las instituciones pueden ver sus vacantes."}), 403

    vacants = Vacant.query.filter_by(institution_email=current_user.email).all()

    result = []

    for v in vacants:
        count = Application.query.filter_by(vacant_id=v.id).count()
        accepted = Application.query.filter_by(vacant_id=v.id, status="aceptado").first()

        if v.is_draft:
            status_summary = "borrador"
        elif accepted:
            status_summary = "cerrada"
        elif count > 0:
            status_summary = "activa_con_postulaciones"
        else:
            status_summary = "activa_sin_postulaciones"

        result.append({
            "id": v.id,
            "area": v.area,
            "description": v.description,
            "hours": v.hours,
            "modality": v.modality,
            "location": v.location,
            "tags": v.tags,
            "status": v.status,
            "is_draft": v.is_draft,
            "last_modified": v.last_modified.isoformat() if v.last_modified else None,
            "applications_count": count,
            "status_summary": status_summary
        })

    return jsonify(result)



# Actualizar una vacante
@vacants_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
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



# Activar o desactivar vacante
@vacants_bp.route("/<int:id>/status", methods=["PATCH"])
@jwt_required()
def toggle_vacant_status(id):
    vacant = Vacant.query.get_or_404(id)
    current_user = User.query.get(get_jwt_identity())

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para modificar esta vacante."}), 403

    new_status = request.get_json().get("status")

    if new_status not in ["activa", "inactiva"]:
        return jsonify({"error": "Estado inválido (usa 'activa' o 'inactiva')"}), 400

    vacant.status = new_status
    db.session.commit()

    return jsonify({"message": f"Vacante marcada como '{new_status}'."})

# Publicar borrador
@vacants_bp.route("/<int:id>/publish", methods=["PATCH"])
@jwt_required()
def publish_vacant(id):
    vacant = Vacant.query.get_or_404(id)
    current_user = User.query.get(get_jwt_identity())

    if vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para publicar esta vacante."}), 403

    if not vacant.is_draft:
        return jsonify({"message": "Esta vacante ya está publicada."}), 200

    vacant.is_draft = False
    db.session.commit()

    return jsonify({"message": "Vacante publicada correctamente."})

@vacants_bp.route("/<int:id>/applications/sorted", methods=["GET"])
@jwt_required()
def sorted_applications(id):
    vacant = Vacant.query.get_or_404(id)
    current_user = User.query.get(get_jwt_identity())

    if current_user.role.name != "institution" or vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes acceso a estas postulaciones."}), 403

    sort_by = request.args.get("sort_by", "date")

    query = Application.query.filter_by(vacant_id=id)

    if sort_by == "average":
        query = query.join(StudentProfile, StudentProfile.email == Application.student_email)\
                     .order_by(StudentProfile.average.desc().nullslast())
    elif sort_by == "career":
        query = query.join(StudentProfile, StudentProfile.email == Application.student_email)\
                     .order_by(StudentProfile.career.asc())
    else:  # default: by submission date (assumes Application has `created_at`)
        query = query.order_by(Application.created_at.desc())

    applications = query.all()

    return jsonify([
        {
            "student_email": app.student_email,
            "status": app.status,
            "submitted": app.created_at.isoformat() if app.created_at else None
        } for app in applications
    ])

@vacants_bp.route("/<int:application_id>/decision", methods=["PATCH"])
@jwt_required()
def decide_application(application_id):
    current_user = User.query.get(get_jwt_identity())
    app = Application.query.get_or_404(application_id)

    vacant = Vacant.query.get_or_404(app.vacant_id)
    if current_user.role.name != "institution" or vacant.institution_email != current_user.email:
        return jsonify({"error": "No tienes permiso para tomar esta decisión."}), 403

    data = request.get_json()
    decision = data.get("decision")
    feedback = data.get("feedback", "")

    if decision not in ["aceptado", "rechazado"]:
        return jsonify({"error": "La decisión debe ser 'aceptado' o 'rechazado'."}), 400

    app.status = decision
    if decision == "rechazado":
        app.feedback = feedback  # nuevo campo opcional

    db.session.commit()
    return jsonify({"message": f"Postulación marcada como '{decision}' correctamente."})

# en routes/vacants.py

@vacants_bp.route("/map", methods=["GET"])
@jwt_required(optional=True)
def vacants_for_map():
    vacants = Vacant.query.filter(
        Vacant.status == "activa",
        Vacant.is_draft == False,
        Vacant.latitude.isnot(None),
        Vacant.longitude.isnot(None)
    ).all()

    return jsonify([
        {
            "id": v.id,
            "area": v.area,
            "description": v.description,
            "modality": v.modality,
            "location": v.location,
            "latitude": v.latitude,
            "longitude": v.longitude
        }
        for v in vacants
    ])
