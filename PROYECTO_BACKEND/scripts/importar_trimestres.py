import os
import django
import sys
import csv
from django.db import transaction
from datetime import datetime

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar el modelo después de configurar Django
from Cursos.models import Trimestre

def importar_trimestres_csv():
    """
    Importa trimestres desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    numero,nombre,año_academico,fecha_inicio,fecha_fin,fecha_limite_evaluaciones,fecha_limite_calificaciones,nota_minima_aprobacion,porcentaje_asistencia_minima,estado
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/trimestre.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Contadores para estadísticas
            total = 0
            creados = 0
            actualizados = 0
            errores = 0
            
            # Usar transacción para asegurar la integridad de los datos
            with transaction.atomic():
                for row in csv_reader:
                    total += 1
                    try:
                        # Convertir fechas de string a objetos datetime
                        fecha_inicio = datetime.strptime(row['fecha_inicio'], '%Y-%m-%d').date()
                        fecha_fin = datetime.strptime(row['fecha_fin'], '%Y-%m-%d').date()
                        fecha_limite_evaluaciones = datetime.strptime(row['fecha_limite_evaluaciones'], '%Y-%m-%d').date()
                        fecha_limite_calificaciones = datetime.strptime(row['fecha_limite_calificaciones'], '%Y-%m-%d').date()
                        
                        # Convertir valores numéricos
                        numero = int(row['numero'])
                        año_academico = int(row['año_academico'])  # Corregido: año_academico con tilde
                        nota_minima_aprobacion = float(row['nota_minima_aprobacion'])
                        porcentaje_asistencia_minima = float(row['porcentaje_asistencia_minima'])
                        
                        # Buscar o crear el trimestre
                        trimestre, created = Trimestre.objects.get_or_create(
                            numero=numero,
                            año_academico=año_academico,  # Corregido: año_academico con tilde
                            defaults={
                                'nombre': row['nombre'],
                                'fecha_inicio': fecha_inicio,
                                'fecha_fin': fecha_fin,
                                'fecha_limite_evaluaciones': fecha_limite_evaluaciones,
                                'fecha_limite_calificaciones': fecha_limite_calificaciones,
                                'nota_minima_aprobacion': nota_minima_aprobacion,
                                'porcentaje_asistencia_minima': porcentaje_asistencia_minima,
                                'estado': row['estado']
                            }
                        )
                        
                        # Si el trimestre ya existía, actualizar sus datos
                        if not created:
                            trimestre.nombre = row['nombre']
                            trimestre.fecha_inicio = fecha_inicio
                            trimestre.fecha_fin = fecha_fin
                            trimestre.fecha_limite_evaluaciones = fecha_limite_evaluaciones
                            trimestre.fecha_limite_calificaciones = fecha_limite_calificaciones
                            trimestre.nota_minima_aprobacion = nota_minima_aprobacion
                            trimestre.porcentaje_asistencia_minima = porcentaje_asistencia_minima
                            trimestre.estado = row['estado']
                            trimestre.save()
                        
                        if created:
                            creados += 1
                            print(f"✓ Creado trimestre: {row['nombre']} (Año: {año_academico}, Número: {numero})")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizado trimestre: {row['nombre']} (Año: {año_academico}, Número: {numero})")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE TRIMESTRES =====")
            print(f"Total de registros procesados: {total}")
            print(f"Trimestres creados: {creados}")
            print(f"Trimestres actualizados: {actualizados}")
            print(f"Errores: {errores}")
            print("===============================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_trimestres_csv()