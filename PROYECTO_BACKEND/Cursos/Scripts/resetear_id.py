import os
import sys
import django

# se ejecuta con el siguiente comando : python Cursos\Scripts\resetear_id.py

# Agregar el directorio raíz del proyecto al path
# Subimos dos niveles: de Scripts a Cursos, y de Cursos a la raíz
proyecto_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, proyecto_dir)

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from django.db import connection
from Cursos.models import TipoEvaluacion

def reset_tipos_evaluacion_ids():
    """Resetea los IDs de TipoEvaluacion para que comiencen desde 1"""
    
    print("Respaldando tipos de evaluación existentes...")
    tipos_existentes = list(TipoEvaluacion.objects.all().values('nombre', 'descripcion', 'activo'))
    
    print(f"Se encontraron {len(tipos_existentes)} tipos de evaluación")
    
    print("Eliminando registros existentes...")
    TipoEvaluacion.objects.all().delete()
    
    print("Reseteando secuencia de IDs...")
    cursor = connection.cursor()
    
    # Determinar el motor de base de datos y ejecutar la instrucción apropiada
    if connection.vendor == 'sqlite':
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tipos_evaluacion';")
        print("Base de datos SQLite detectada, secuencia reiniciada")
    elif connection.vendor == 'postgresql':
        cursor.execute("ALTER SEQUENCE tipos_evaluacion_id_seq RESTART WITH 1;")
        print("Base de datos PostgreSQL detectada, secuencia reiniciada")
    elif connection.vendor in ('mysql', 'mariadb'):
        cursor.execute("ALTER TABLE tipos_evaluacion AUTO_INCREMENT = 1;")
        print("Base de datos MySQL/MariaDB detectada, secuencia reiniciada")
    else:
        print(f"Motor de base de datos no reconocido: {connection.vendor}")
        print("La secuencia podría no haberse reiniciado correctamente")
    
    print("Recreando tipos de evaluación con nuevos IDs...")
    for tipo in tipos_existentes:
        TipoEvaluacion.objects.create(
            nombre=tipo['nombre'],
            descripcion=tipo['descripcion'],
            activo=tipo['activo']
        )
    
    print("\nProceso completado. Nuevos tipos de evaluación:")
    for tipo in TipoEvaluacion.objects.all().order_by('id'):
        print(f"ID: {tipo.id}, Nombre: {tipo.nombre}")

if __name__ == "__main__":
    reset_tipos_evaluacion_ids()
    
