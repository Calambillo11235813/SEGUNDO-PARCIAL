import os
import django
import sys
import csv
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Curso, Materia

def importar_materias_por_curso_csv():
    """
    Importa materias por curso desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    nombre,curso_id
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/materias_por_curso.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Contador para estadísticas
            total = 0
            creados = 0
            actualizados = 0
            errores = 0
            
            # Usar transacción para asegurar que todos los datos se guarden correctamente
            with transaction.atomic():
                for row in csv_reader:
                    total += 1
                    try:
                        # Verificar que el curso existe
                        curso_id = int(row['curso_id'])
                        try:
                            curso = Curso.objects.get(id=curso_id)
                        except Curso.DoesNotExist:
                            raise Exception(f"El curso con ID {curso_id} no existe.")
                        
                        # Buscar o crear la materia
                        materia, created = Materia.objects.get_or_create(
                            nombre=row['nombre'],
                            curso=curso,
                            defaults={
                                'profesor': None  # Inicialmente sin profesor asignado
                            }
                        )
                        
                        if created:
                            creados += 1
                            print(f"✓ Creada materia: {row['nombre']} - Curso: {curso}")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizada materia: {row['nombre']} - Curso: {curso}")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE MATERIAS =====")
            print(f"Total de registros procesados: {total}")
            print(f"Materias creadas: {creados}")
            print(f"Materias actualizadas: {actualizados}")
            print(f"Errores: {errores}")
            print("===========================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_materias_por_curso_csv()