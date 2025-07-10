# repositories/vacant_repository.py
from datetime import datetime, date
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from extensions import db
from models.vacant import Vacant
from models.institution_profile import InstitutionProfile

class VacantRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_by_id(self, vacant_id: int) -> Vacant | None:
        return self.db_session.query(Vacant).get(vacant_id)

    def create_vacant(self, **kwargs) -> Vacant:
        vacant = Vacant(**kwargs)
        self.db_session.add(vacant)
        return vacant

    def update_vacant(self, vacant: Vacant, data: dict) -> Vacant:
        for key, value in data.items():
            if value is not None:
                setattr(vacant, key, value)
        vacant.last_modified = datetime.utcnow()
        self.db_session.add(vacant)
        return vacant

    def delete_vacant(self, vacant: Vacant):
        self.db_session.delete(vacant)

    def get_paginated_vacants_with_filters(self, filters: dict, page: int, per_page: int):
        query = self.db_session.query(Vacant).options(
            joinedload(Vacant.institution_profile)
        ).filter(Vacant.status == "activa", Vacant.is_draft == False)

        if filters.get("area"):
            query = query.filter(Vacant.area == filters["area"])
        if filters.get("modality"):
            query = query.filter(Vacant.modality == filters["modality"])
        if filters.get("location"):
            query = query.filter(Vacant.location == filters["location"])
        if filters.get("tag"):
            query = query.filter(Vacant.tags.ilike(f"%{filters['tag']}%"))
        if filters.get("keyword"):
            search_term = f"%{filters['keyword']}%"
            query = query.filter(
                or_(
                    Vacant.area.ilike(search_term),
                    Vacant.description.ilike(search_term),
                    Vacant.requirements.ilike(search_term),
                    Vacant.tags.ilike(search_term)
                )
            )

        query = query.order_by(Vacant.last_modified.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_institution_vacants(self, institution_email: str) -> list[Vacant]:
        return self.db_session.query(Vacant).filter_by(institution_email=institution_email).all()

    # --- MODIFICADO: Añadir filtro para NULLs y vacíos ---
    def get_unique_areas(self) -> list[str]:
        areas = self.db_session.query(Vacant.area)\
                      .filter(
                          Vacant.status == "activa",
                          Vacant.is_draft == False,
                          Vacant.area.isnot(None),    # Excluir NULL
                          Vacant.area != ''           # Excluir cadenas vacías
                      )\
                      .distinct().order_by(Vacant.area.asc()).all()
        return [area[0] for area in areas if area[0]]

    # --- MODIFICADO: Añadir filtro para NULLs y vacíos ---
    def get_unique_modalities(self) -> list[str]:
        modalities = self.db_session.query(Vacant.modality)\
                           .filter(
                               Vacant.status == "activa",
                               Vacant.is_draft == False,
                               Vacant.modality.isnot(None), # Excluir NULL
                               Vacant.modality != ''        # Excluir cadenas vacías
                           )\
                           .distinct().order_by(Vacant.modality.asc()).all()
        return [modality[0] for modality in modalities if modality[0]]

    # --- MÉTODO get_unique_hours (ya modificado en la última iteración) ---
    def get_unique_hours(self) -> list[str]:
        hours = self.db_session.query(Vacant.hours)\
                           .filter(
                               Vacant.status == "activa",
                               Vacant.is_draft == False,
                               Vacant.hours.isnot(None),
                               Vacant.hours != ''
                           )\
                           .distinct().order_by(Vacant.hours.asc()).all()
        return [hour[0] for hour in hours if hour[0]]

    # --- MODIFICADO: Añadir filtro para NULLs y vacíos ---
    def get_unique_locations(self) -> list[str]:
        locations = self.db_session.query(Vacant.location)\
                           .filter(
                               Vacant.status == "activa",
                               Vacant.is_draft == False,
                               Vacant.location.isnot(None), # Excluir NULL
                               Vacant.location != ''        # Excluir cadenas vacías
                           )\
                           .distinct().order_by(Vacant.location.asc()).all()
        return [location[0] for location in locations if location[0]]

    # --- MODIFICADO: Hacer get_unique_tags más robusto para tags no string ---
    def get_unique_tags(self) -> list[str]:
        all_tags_raw = self.db_session.query(Vacant.tags)\
                                 .filter(
                                     Vacant.status == "activa",
                                     Vacant.is_draft == False,
                                     Vacant.tags.isnot(None),  # Excluir NULL
                                     Vacant.tags != ''         # Excluir cadenas vacías
                                 )\
                                 .distinct().all()
        unique_tags = set()
        for tags_str_tuple in all_tags_raw:
            tags_str = tags_str_tuple[0]
            if isinstance(tags_str, str): # Asegurar que es una cadena antes de split
                for tag in tags_str.split(','):
                    cleaned_tag = tag.strip()
                    if cleaned_tag:
                        unique_tags.add(cleaned_tag)
        return sorted(list(unique_tags))
    # -----------------------------------------------------------------------

    def get_active_vacants_with_coordinates(self) -> list[Vacant]:
        return self.db_session.query(Vacant).filter(
            Vacant.status == "activa", 
            Vacant.is_draft == False,
            Vacant.latitude.isnot(None), 
            Vacant.longitude.isnot(None)
        ).all()