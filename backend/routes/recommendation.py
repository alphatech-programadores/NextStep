# en routes/recommendation.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.student_profile import StudentProfile
from models.vacant import Vacant
from recommender import match_score

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def recommend_vacants():
    email = get_jwt_identity()
    profile = StudentProfile.query.get(email)

    if not profile or not profile.skills:
        return jsonify([])

    vacants = Vacant.query.filter_by(status="activa", is_draft=False).all()

    results = []
    for v in vacants:
        score = match_score(profile.skills, v.requirements)
        if score > 0.5:
            results.append({
                "id": v.id,
                "area": v.area,
                "description": v.description,
                "modality": v.modality,
                "location": v.location,
                "match_score": score
            })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(results)
