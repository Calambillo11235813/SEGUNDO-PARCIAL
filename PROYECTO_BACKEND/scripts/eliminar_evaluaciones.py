import os
import django
import sys
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import EvaluacionEntregable

def eliminar_evaluaciones():
    """
    Elimina todas las evaluaciones entregables importadas desde el CSV.
    """
    try:
        with transaction.atomic():
            # Contar evaluaciones antes de eliminar
            total_antes = EvaluacionEntregable.objects.count()
            
            # Eliminar todas las evaluaciones
            EvaluacionEntregable.objects.all().delete()
            
            # Contar evaluaciones después de eliminar
            total_despues = EvaluacionEntregable.objects.count()
            
            print("\n===== RESUMEN DE ELIMINACIÓN =====")
            print(f"Evaluaciones antes: {total_antes}")
            print(f"Evaluaciones después: {total_despues}")
            print(f"Total eliminadas: {total_antes - total_despues}")
            print("==================================")
            
    except Exception as e:
        print(f"Error al eliminar evaluaciones: {str(e)}")

if __name__ == '__main__':
    # Confirmar antes de eliminar
    confirmacion = input("¿Estás seguro que deseas eliminar TODAS las evaluaciones? (s/n): ")
    if confirmacion.lower() == 's':
        eliminar_evaluaciones()
    else:
        print("Operación cancelada.")