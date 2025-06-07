import os
import django
import sys

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Calificacion, EvaluacionEntregable, EvaluacionParticipacion

def migrate_calificaciones():
    """Migra las calificaciones al nuevo sistema de relaciones genéricas"""
    
    # Obtener los tipos de contenido
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    
    # Contar calificaciones a migrar
    total_calificaciones = Calificacion.objects.count()
    print(f"Total de calificaciones a migrar: {total_calificaciones}")
    
    # Verificar si hay datos en los nuevos modelos
    total_entregables = EvaluacionEntregable.objects.count()
    total_participacion = EvaluacionParticipacion.objects.count()
    print(f"Evaluaciones entregables existentes: {total_entregables}")
    print(f"Evaluaciones de participación existentes: {total_participacion}")
    
    # Actualizar calificaciones existentes
    with transaction.atomic():
        # Ejemplo: Si todas tus evaluaciones actuales deberían ser de tipo entregable
        Calificacion.objects.update(content_type=entregable_ct)
        
        # Si tienes el ID original de evaluación, podrías mapearlo al nuevo modelo
        # Por ejemplo:
        # for calificacion in Calificacion.objects.all():
        #     if calificacion.original_evaluacion_id:
        #         calificacion.object_id = calificacion.original_evaluacion_id
        #         calificacion.save()
    
    print("Migración de calificaciones completada")

if __name__ == '__main__':
    migrate_calificaciones()