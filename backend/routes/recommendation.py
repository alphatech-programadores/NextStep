# en routes/recommendation.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.student_profile import StudentProfile
from models.vacant import Vacant
from recommender import match_score

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/api/recommendations", methods=["GET"], strict_slashes=False)
@jwt_required()
def recommend_vacants():
    email = get_jwt_identity()
    print(f"DEBUG: Solicitud de recomendaciones para el email: {email}") # DEBUG
    
    profile = StudentProfile.query.filter_by(email=email).first()

    if not profile:
        print(f"DEBUG: Perfil de estudiante no encontrado para {email}") # DEBUG
        return jsonify({"error": "Perfil de estudiante no encontrado"}, 404)

    if not profile.skills:
        print(f"DEBUG: Habilidades del estudiante vacías para {email}") # DEBUG
        return jsonify({"message": "No se encontraron vacantes recomendadas. Asegúrate de tener tu perfil de estudiante completo con habilidades."}, 200)

    print(f"DEBUG: Habilidades del estudiante {email}: {profile.skills}") # DEBUG

    vacants = Vacant.query.filter_by(status="activa", is_draft=False).all()
    if not vacants:
        print("DEBUG: No se encontraron vacantes activas.") # DEBUG
        return jsonify({"message": "No se encontraron vacantes activas para recomendar."}, 200)

    print(f"DEBUG: Se encontraron {len(vacants)} vacantes activas.") # DEBUG

    results = []
    # Umbral de compatibilidad, TEMPORALMENTE ajustado a 0.0 para depuración
    compatibility_threshold = 0.0 # <--- CAMBIO AQUÍ: Umbral a 0.0 para ver todas las puntuaciones

    for v in vacants:
        score = match_score(profile.skills, v.requirements)
        print(f"DEBUG: Vacante ID: {v.id}, Área: {v.area}, Score: {score:.4f}") # DEBUG
        if score >= compatibility_threshold: # Usar el umbral ajustable
            results.append({
                "id": v.id,
                "area": v.area,
                "description": v.description,
                "modality": v.modality,
                "location": v.location,
                "match_score": score
            })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    print(f"DEBUG: Total de vacantes recomendadas (score >= {compatibility_threshold}): {len(results)}") # DEBUG
    return jsonify(results)
