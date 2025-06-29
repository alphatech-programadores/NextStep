# En backend/routes/application.py

from flask import Blueprint, jsonify, request # Asegúrate de que request esté importado
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from collections import Counter # Usaremos Counter para contar fácilmente

from models.application import Application
from models.vacant import Vacant
from models.user import User
from models.institution_profile import InstitutionProfile

app_bp = Blueprint("application", __name__, url_prefix="/api/apply")

@app_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_applications():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user or user.role.name != 'student':
        return jsonify({"error": "Acceso denegado."}), 403

    # --- LÓGICA DE ESTADÍSTICAS ---
    # 1. Obtenemos TODAS las postulaciones del usuario sin paginar para poder contarlas.
    all_user_applications = Application.query.filter_by(student_email=user.email).all()
    
    # 2. Contamos los estados usando Counter.
    status_counts = Counter(app.status for app in all_user_applications)
    
    # 3. Preparamos el objeto de estadísticas.
    stats = {
        'total': len(all_user_applications),
        'pending': status_counts.get('pendiente', 0), # Usa el nombre exacto de tus estados
        'interview': status_counts.get('entrevista', 0),
        'accepted': status_counts.get('aceptada', 0)
    }
    # --- FIN LÓGICA DE ESTADÍSTICAS ---

    # --- LÓGICA DE PAGINACIÓN (para la lista) ---
    # Ahora construimos la consulta paginada que se enviará al frontend.
    query = Application.query.options(
        joinedload(Application.vacant).joinedload(Vacant.institution_profile)
    ).filter(Application.student_email == user.email)

    status_filter = request.args.get("status", "").strip()
    if status_filter:
        query = query.filter(Application.status == status_filter)

    query = query.order_by(Application.created_at.desc())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    paginated_applications = query.paginate(page=page, per_page=per_page, error_out=False)

    applications_list = [{
        "id": app.id,
        "vacant_id": app.vacant.id,
        "vacant_title": app.vacant.area,
        "company_name": app.vacant.institution_profile.institution_name if app.vacant.institution_profile else "Desconocido",
        "application_status": app.status,
        "applied_at": app.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    } for app in paginated_applications.items]

    return jsonify({
        "stats": stats, # <-- DEVOLVEMOS LAS ESTADÍSTICAS
        "applications": applications_list,
        "total_pages": paginated_applications.pages,
        "current_page": paginated_applications.page,
        "total_items": paginated_applications.total
    }), 200
