from models.vacant import Vacant

def build_vacant_query(base_filters=None, dynamic_filters=None):
    """
    Crea un query con filtros base y dinámicos.

    base_filters: dict con filters estáticos (p.ej., {'status': 'activa'})
    dynamic_filters: dict con filtros opcionales como area, modality, etc.
    """
    query = Vacant.query

    # Aplicar filtros base
    if base_filters:
        query = query.filter_by(**base_filters)

    # Aplicar filtros dinámicos
    if dynamic_filters:
        if dynamic_filters.get("area"):
            query = query.filter(Vacant.area.ilike(f"%{dynamic_filters['area']}%"))
        if dynamic_filters.get("modality"):
            query = query.filter(Vacant.modality.ilike(f"%{dynamic_filters['modality']}%"))
        if dynamic_filters.get("location"):
            query = query.filter(Vacant.location.ilike(f"%{dynamic_filters['location']}%"))
        if dynamic_filters.get("tag"):
            query = query.filter(Vacant.tags.ilike(f"%{dynamic_filters['tag']}%"))
        if dynamic_filters.get("keyword"):
            q = f"%{dynamic_filters['keyword']}%"
            query = query.filter(
                Vacant.description.ilike(q) |
                Vacant.requirements.ilike(q) |
                Vacant.area.ilike(q)
            )
        if dynamic_filters.get("latitude"):
            query = query.filter(Vacant.latitude.isnot(None))
        if dynamic_filters.get("longitude"):
            query = query.filter(Vacant.longitude.isnot(None))

    return query
