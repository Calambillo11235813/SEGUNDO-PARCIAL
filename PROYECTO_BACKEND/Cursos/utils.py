from django.contrib.contenttypes.models import ContentType
from .models import EvaluacionEntregable, EvaluacionParticipacion

def get_evaluacion_by_id(eval_id, select_related=None):
    """Busca una evaluación por ID en ambas tablas de evaluaciones."""
    try:
        # Primero intentamos con evaluaciones entregables
        query = EvaluacionEntregable.objects
        if select_related:
            query = query.select_related(*select_related)
        return query.get(id=eval_id)
    except EvaluacionEntregable.DoesNotExist:
        try:
            # Si no encontramos, buscamos en participaciones
            query = EvaluacionParticipacion.objects
            if select_related:
                query = query.select_related(*select_related)
            return query.get(id=eval_id)
        except EvaluacionParticipacion.DoesNotExist:
            return None

def get_evaluaciones_count(filtro=None):
    """Obtiene el conteo total de evaluaciones aplicando un filtro opcional."""
    entregables_query = EvaluacionEntregable.objects
    participacion_query = EvaluacionParticipacion.objects
    
    if filtro:
        entregables_query = entregables_query.filter(**filtro)
        participacion_query = participacion_query.filter(**filtro)
    
    return entregables_query.count() + participacion_query.count()

def get_evaluaciones_activas(filtro=None):
    """Obtiene todas las evaluaciones activas con filtro opcional."""
    base_filter = {'activo': True}
    if filtro:
        base_filter.update(filtro)
    
    entregables = list(EvaluacionEntregable.objects.filter(**base_filter))
    participaciones = list(EvaluacionParticipacion.objects.filter(**base_filter))
    
    return entregables + participaciones