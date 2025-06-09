import os
import django
import sys
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar los modelos después de configurar Django
from Cursos.models import EvaluacionParticipacion, Calificacion
from django.contrib.contenttypes.models import ContentType

def eliminar_participaciones():
    """
    Elimina todas las evaluaciones de participación del año 2022 importadas desde el CSV.
    También elimina las calificaciones asociadas a estas participaciones.
    """
    try:
        with transaction.atomic():
            # Obtener el ContentType para EvaluacionParticipacion
            participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
            
            # Filtrar evaluaciones del año 2022 (trimestres 4, 5 y 6)
            participaciones = EvaluacionParticipacion.objects.filter(
                trimestre_id__in=[4, 5, 6]  # Trimestres correspondientes a 2022
            )
            
            # Contar antes de eliminar
            total_participaciones = participaciones.count()
            
            # Buscar calificaciones asociadas a estas participaciones
            ids_participaciones = list(participaciones.values_list('id', flat=True))
            calificaciones = Calificacion.objects.filter(
                content_type=participacion_ct,
                object_id__in=ids_participaciones
            )
            total_calificaciones = calificaciones.count()
            
            # Eliminar primero las calificaciones (para evitar errores de integridad referencial)
            if total_calificaciones > 0:
                calificaciones.delete()
                print(f"✓ Se han eliminado {total_calificaciones} calificaciones de participación")
            
            # Eliminar las participaciones
            if total_participaciones > 0:
                participaciones.delete()
                print(f"✓ Se han eliminado {total_participaciones} evaluaciones de participación")
            
            # Contar participaciones después de eliminar para verificar
            participaciones_restantes = EvaluacionParticipacion.objects.filter(
                trimestre_id__in=[4, 5, 6]
            ).count()
            
            print("\n===== RESUMEN DE ELIMINACIÓN =====")
            print(f"Participaciones antes: {total_participaciones}")
            print(f"Participaciones después: {participaciones_restantes}")
            print(f"Total eliminadas: {total_participaciones - participaciones_restantes}")
            print(f"Calificaciones eliminadas: {total_calificaciones}")
            print("==================================")
            
    except Exception as e:
        print(f"Error al eliminar participaciones: {str(e)}")

if __name__ == '__main__':
    # Confirmar antes de eliminar
    print("⚠️ ADVERTENCIA: Esta operación eliminará todas las participaciones de 2022 y sus calificaciones asociadas.")
    print("⚠️ Esta acción NO SE PUEDE DESHACER.")
    
    confirmacion = input("¿Estás seguro que deseas eliminar TODAS las participaciones de 2022? (s/n): ")
    if confirmacion.lower() == 's':
        eliminar_participaciones()
    else:
        print("Operación cancelada.")