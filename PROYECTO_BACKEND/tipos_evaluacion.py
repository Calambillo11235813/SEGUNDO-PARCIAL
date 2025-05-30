import os
import sys
import django


# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar el modelo después de configurar el entorno
from Cursos.models import TipoEvaluacion

def crear_tipos_evaluacion():
    """Crea los tipos de evaluación predefinidos en el sistema."""
    
    # Eliminar tipo EXPOSICION si existe
    TipoEvaluacion.objects.filter(nombre='EXPOSICION').delete()
    print("✓ Se eliminó el tipo 'EXPOSICION' si existía")
    
    tipos = [
        {
            'nombre': 'EXAMEN',
            'descripcion': 'Evaluaciones escritas y orales para medir conocimientos',
            'porcentaje_minimo': 20.00,
            'porcentaje_maximo': 60.00
        },
        {
            'nombre': 'PARTICIPACION',
            'descripcion': 'Participación activa durante las clases',
            'porcentaje_minimo': 5.00,
            'porcentaje_maximo': 20.00
        },
        {
            'nombre': 'TRABAJO',
            'descripcion': 'Trabajos prácticos y tareas académicas',
            'porcentaje_minimo': 10.00,
            'porcentaje_maximo': 40.00
        }
    ]
    
    for tipo_data in tipos:
        tipo, created = TipoEvaluacion.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"✓ Tipo de evaluación creado: {tipo.nombre}")
        else:
            print(f"► Tipo de evaluación ya existe: {tipo.nombre}")
    
    # Imprimir todos los tipos disponibles con sus IDs
    print("\nTipos de evaluación disponibles:")
    for tipo in TipoEvaluacion.objects.all().order_by('id'):
        print(f"ID: {tipo.id}, Nombre: {tipo.nombre}")

if __name__ == '__main__':
    print("Creando tipos de evaluación...")
    crear_tipos_evaluacion()
    print("\nProceso completado.")
    
    
    # Ejecutar el script con el siguiente comando : 
    # python tipos_evaluacion.py