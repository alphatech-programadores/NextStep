from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db
from models.student_profile import StudentProfile
from models.institution_profile import InstitutionProfile
from models.vacant import Vacant
from sqlalchemy.orm import joinedload
from models.application import Application
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, Role
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.metrics.pairwise import cosine_similarity
from utils import session_validated
#import nltk
#nltk.download('punkt')


vacants_bp = Blueprint("vacants", __name__)

@vacants_bp.route("/filters/areas", methods=["GET"])
def get_unique_areas():
    # Obtiene todos los valores distintos y activos de 'area'
    # Utiliza .distinct() y .all() con la columna para obtener una lista de tuplas, luego aplanarlas
    areas = db.session.query(Vacant.area)\
                      .filter(Vacant.status == "activa", Vacant.is_draft == False)\
                      .distinct().order_by(Vacant.area.asc()).all()
    # Mapea de lista de tuplas a lista de strings
    return jsonify([area[0] for area in areas if area[0]]), 200 # Filtra None/vacíos

@vacants_bp.route("/filters/modalities", methods=["GET"])
def get_unique_modalities():
    modalities = db.session.query(Vacant.modality)\
                           .filter(Vacant.status == "activa", Vacant.is_draft == False)\
                           .distinct().order_by(Vacant.modality.asc()).all()
    return jsonify([modality[0] for modality in modalities if modality[0]]), 200

@vacants_bp.route("/filters/locations", methods=["GET"])
def get_unique_locations():
    locations = db.session.query(Vacant.location)\
                           .filter(Vacant.status == "activa", Vacant.is_draft == False)\
                           .distinct().order_by(Vacant.location.asc()).all()
    return jsonify([location[0] for location in locations if location[0]]), 200

@vacants_bp.route("/filters/tags", methods=["GET"])
def get_unique_tags():
    # Obtener todos los tags de todas las vacantes activas como un solo conjunto
    all_tags_raw = db.session.query(Vacant.tags)\
                             .filter(Vacant.status == "activa", Vacant.is_draft == False)\
                             .distinct().all()
    
    unique_tags = set()
    for tags_str_tuple in all_tags_raw:
        tags_str = tags_str_tuple[0] # Es una tupla de un solo elemento (el string de tags)
        if tags_str: # Asegurarse de que no sea None o vacío
            # Dividir por coma y limpiar espacios, luego añadir al conjunto
            for tag in tags_str.split(','):
                cleaned_tag = tag.strip()
                if cleaned_tag: # Asegurarse de que el tag no esté vacío después de limpiar
                    unique_tags.add(cleaned_tag)
    
    # Convertir el conjunto a una lista ordenada para la respuesta
    return jsonify(sorted(list(unique_tags))), 200

@vacants_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def list_and_search_vacants(): # Renombrado para claridad
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first() if identity else None # Usar email como PK

    # Parámetros de búsqueda y paginación
    area_filter = request.args.get("area", "").strip()
    modality_filter = request.args.get("modality", "").strip()
    location_filter = request.args.get("location", "").strip()
    tag_filter = request.args.get("tag", "").strip()
    keyword_filter = request.args.get("q", "").strip() # Usar 'q' para keyword
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Vacant.query.filter_by(status="activa", is_draft=False)

    # Si es estudiante y ya fue aceptado en una vacante, no mostrarle más
    if user and user.role.name == "student":
        # Asegúrate de que el campo 'status' en Application puede ser 'aceptado'
        accepted = Application.query.filter_by(student_email=user.email, status="aceptado").first()
        if accepted:
            return jsonify({"vacancies": [], "total_pages": 0, "current_page": 0, "total_items": 0}), 200 # Devuelve una respuesta paginada vacía

    # Aplicar filtros
    if area_filter:
        query = query.filter(Vacant.area.ilike(f"%{area_filter}%"))
    if modality_filter:
        query = query.filter(Vacant.modality.ilike(f"%{modality_filter}%"))
    if location_filter:
        query = query.filter(Vacant.location.ilike(f"%{location_filter}%"))
    if tag_filter:
        query = query.filter(Vacant.tags.ilike(f"%{tag_filter}%"))
    if keyword_filter:
        query = query.filter(
            (Vacant.description.ilike(f"%{keyword_filter}%")) |
            (Vacant.requirements.ilike(f"%{keyword_filter}%")) |
            (Vacant.area.ilike(f"%{keyword_filter}%"))
        )

    # Ordenar por fecha de última modificación (más reciente primero)
    query = query.order_by(Vacant.last_modified.desc())

    # Paginación
    paginated_vacants = query.paginate(page=page, per_page=per_page, error_out=False)

    vacants_list = []
    for vacant in paginated_vacants.items:
        # Obtener el nombre de la institución desde InstitutionProfile
        institution_profile = InstitutionProfile.query.filter_by(email=vacant.institution_email).first()
        company_name = institution_profile.institution_name if institution_profile else "Desconocido"

        vacants_list.append({
            "id": vacant.id,
            "title": vacant.area, # Usar 'area' como título principal en el frontend
            "description": vacant.description,
            "requirements": vacant.requirements,
            "responsibilities": vacant.requirements, # Tu modelo no tiene responsibilities, usar requirements
            "location": vacant.location,
            "modality": vacant.modality,
            "type": vacant.area, # Usar 'area' como tipo de vacante
            "salary_range": vacant.hours, # Usar 'hours' como rango salarial/horas
            "posted_date": vacant.start_date.strftime("%Y-%m-%d") if vacant.start_date else None, # Usar start_date como posted_date
            "application_deadline": vacant.end_date.strftime("%Y-%m-%d") if vacant.end_date else None, # Usar end_date como deadline
            "company_name": company_name,
            "institution_email": vacant.institution_email,
            "tags": vacant.tags.split(',') if vacant.tags else [] # Convertir tags a lista
        })

    return jsonify({
        "vacancies": vacants_list, # Cambiado a 'vacancies' para consistencia con frontend
        "total_pages": paginated_vacants.pages,
        "current_page": paginated_vacants.page,
        "total_items": paginated_vacants.total
    }), 200


# Endpoint para obtener detalles de una sola vacante (si no lo tienes ya)
@vacants_bp.route("/<int:vacant_id>", methods=["GET"])
def get_vacant_details(vacant_id):
    vacant = Vacant.query.get(vacant_id)
    if not vacant or vacant.status != 'activa' or vacant.is_draft:
        return jsonify({"error": "Vacante no encontrada o inactiva."}), 404

    institution_profile = InstitutionProfile.query.filter_by(email=vacant.institution_email).first()
    company_name = institution_profile.institution_name if institution_profile else "Desconocido"

    return jsonify({
        "id": vacant.id,
        "title": vacant.area,
        "description": vacant.description,
        "requirements": vacant.requirements,
        "responsibilities": vacant.requirements, # Usar requirements si no tienes responsibilities
        "location": vacant.location,
        "modality": vacant.modality,
        "type": vacant.area,
        "salary_range": vacant.hours,
        "posted_date": vacant.start_date.strftime("%Y-%m-%d") if vacant.start_date else None,
        "application_deadline": vacant.end_date.strftime("%Y-%m-%d") if vacant.end_date else None,
        "company_name": company_name,
        "institution_email": vacant.institution_email,
        "tags": vacant.tags.split(',') if vacant.tags else []
    }), 200


# Endpoint para postular a una vacante
@vacants_bp.route("/<int:vacant_id>/apply", methods=["POST"])
@jwt_required()
def apply_to_vacant(vacant_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user or user.role.name != 'student':
        return jsonify({"error": "Acceso denegado. Solo estudiantes pueden postular."}), 403

    vacant = Vacant.query.get(vacant_id)
    if not vacant or vacant.status != 'activa' or vacant.is_draft:
        return jsonify({"error": "Vacante no encontrada o inactiva."}), 404

    # Verificar si el estudiante ya aplicó a esta vacante
    existing_application = Application.query.filter_by(
        student_email=user.email,
        vacant_id=vacant.id
    ).first()

    if existing_application:
        return jsonify({"message": "Ya has postulado a esta vacante."}), 409

    # Tu modelo Application no tiene 'cover_letter', así que no lo esperamos del request
    # data = request.get_json()
    # cover_letter = data.get("cover_letter", "").strip()

    new_application = Application(
        student_email=user.email,
        vacant_id=vacant.id,
        created_at=datetime.utcnow(),
        status="pendiente",
        # No se asigna cover_letter si no existe en el modelo
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": "Postulación enviada exitosamente!", "application_id": new_application.id}), 201

# Endpoint para verificar el estado de la aplicación de un estudiante a una vacante
@vacants_bp.route("/check_status/<int:vacant_id>", methods=["GET"])
@jwt_required()
def check_application_status(vacant_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user or user.role.name != 'student':
        return jsonify({"error": "Acceso denegado."}), 403

    application = Application.query.filter_by(
        student_email=user.email,
        vacant_id=vacant_id
    ).first()

    return jsonify({"has_applied": application is not None}), 200

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

# --- REEMPLAZA TU RUTA DE POSTULANTES CON ESTA VERSIÓN ---

@vacants_bp.route("/<int:id>/applications", methods=["GET"])
@jwt_required()
def get_applications_for_vacant(id):
    # Primero, verificamos que la institución tenga permiso para ver esta vacante
    current_user_email = get_jwt_identity()
    vacant = Vacant.query.get_or_404(id)
    if vacant.institution_email != current_user_email:
        return jsonify({"error": "No tienes permiso para ver estas postulaciones."}), 403

    # Usamos joinedload para cargar eficientemente los datos relacionados del estudiante
    # Esto hace un JOIN en la base de datos para evitar múltiples consultas
    applications = Application.query.options(
        joinedload(Application.student).joinedload(User.student_profile)
    ).filter_by(vacant_id=id).order_by(Application.created_at.desc()).all()

    result = []
    for app in applications:
        # Nos aseguramos de que el estudiante y su perfil existan
        if app.student and app.student.student_profile:
            student_user = app.student
            student_profile = app.student.student_profile

            # Construimos el objeto anidado 'student'
            student_data = {
                "name": student_user.name,
                "email": student_user.email,
                "career": student_profile.career,
                "semester": student_profile.semestre,
                "skills": student_profile.skills.split(',') if student_profile.skills else [],
                "cv_url": student_profile.cv_path # Asumiendo que cv_path contiene la URL
            }
            
            # Construimos el objeto de postulación final
            result.append({
                "application_id": app.id,
                "status": app.status,
                "submitted_at": app.created_at.isoformat() if app.created_at else None,
                "student": student_data # <-- Aquí está el objeto anidado
            })

    return jsonify(result), 200

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
