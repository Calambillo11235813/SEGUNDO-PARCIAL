import os
import django
import sys
import csv
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Curso, Nivel

def importar_cursos_csv():
    """
    Importa cursos desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    id,grado,paralelo,nivel
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/cursos.csv'
    
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
                # Asegurarse que existan los niveles
                for nivel_id in range(1, 3):  # Asumiendo niveles 1 y 2 (primaria y secundaria)
                    nivel, created = Nivel.objects.get_or_create(
                        id=nivel_id,
                        defaults={'nombre': f'Nivel {nivel_id}'}
                    )
                    if created:
                        print(f"✓ Creado nivel {nivel_id}: {nivel.nombre}")
                
                for row in csv_reader:
                    total += 1
                    try:
                        # Buscar nivel
                        nivel_id = int(row['nivel'])
                        try:
                            nivel = Nivel.objects.get(id=nivel_id)
                        except Nivel.DoesNotExist:
                            print(f"Error: No existe el nivel {nivel_id}, creándolo...")
                            nivel = Nivel.objects.create(id=nivel_id, nombre=f'Nivel {nivel_id}')
                        
                        # Buscar o crear el curso
                        curso, created = Curso.objects.get_or_create(
                            id=int(row['id']),
                            defaults={
                                'grado': int(row['grado']),
                                'paralelo': row['paralelo'],
                                'nivel': nivel
                            }
                        )
                        
                        # Si el curso ya existía, actualizar sus datos
                        if not created:
                            curso.grado = int(row['grado'])
                            curso.paralelo = row['paralelo']
                            curso.nivel = nivel
                            curso.save()
                        
                        if created:
                            creados += 1
                            print(f"✓ Creado curso {row['id']}: {row['grado']}° {row['paralelo']} - Nivel {nivel_id}")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizado curso {row['id']}: {row['grado']}° {row['paralelo']} - Nivel {nivel_id}")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE CURSOS =====")
            print(f"Total de registros procesados: {total}")
            print(f"Cursos creados: {creados}")
            print(f"Cursos actualizados: {actualizados}")
            print(f"Errores: {errores}")
            print("==========================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_cursos_csv()