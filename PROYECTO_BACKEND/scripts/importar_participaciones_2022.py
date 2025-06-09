import os
import django
import sys
import csv
from django.db import transaction
from datetime import datetime
from decimal import Decimal
from django.utils import timezone

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar los modelos después de configurar Django
from Cursos.models import Materia, Curso, Trimestre, TipoEvaluacion, EvaluacionParticipacion

def importar_participaciones_csv():
    """
    Importa evaluaciones de participación desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    materia,curso_id,tipo_evaluacion_id,trimestre_id,titulo,descripcion,porcentaje_nota_final,
    fecha_registro,criterios_participacion,escala_calificacion
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/participaciones_2022.csv'
    
    # Verificar que existan los tipos de evaluación necesarios
    try:
        # Asegurar que existe el tipo de evaluación PARTICIPACION (id 3)
        tipo_eval, created = TipoEvaluacion.objects.get_or_create(
            id=3,
            defaults={
                'nombre': 'PARTICIPACION', 
                'descripcion': 'Evaluación de participación en clase'
            }
        )
        if created:
            print(f"✓ Creado tipo de evaluación: PARTICIPACION (ID: 3)")
    except Exception as e:
        print(f"Error al verificar tipo de evaluación: {str(e)}")
        return
    
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
            
            # Cache para materias, trimestres y tipos de evaluación
            materias_cache = {}
            trimestres_cache = {}
            tipos_eval_cache = {}
            
            # Usar transacción para asegurar la integridad de los datos
            with transaction.atomic():
                for row in csv_reader:
                    total += 1
                    try:
                        # Obtener datos básicos
                        nombre_materia = row['materia']
                        curso_id = int(row['curso_id'])
                        tipo_evaluacion_id = int(row['tipo_evaluacion_id'])
                        trimestre_id = int(row['trimestre_id'])
                        
                        # Buscar la materia por nombre y curso
                        materia_key = f"{nombre_materia}_{curso_id}"
                        
                        if materia_key not in materias_cache:
                            try:
                                materia = Materia.objects.get(nombre=nombre_materia, curso_id=curso_id)
                                materias_cache[materia_key] = materia
                            except Materia.DoesNotExist:
                                raise Exception(f"No existe la materia '{nombre_materia}' para el curso {curso_id}")
                        
                        materia = materias_cache[materia_key]
                        
                        # Verificar que el trimestre existe
                        if trimestre_id not in trimestres_cache:
                            try:
                                trimestre = Trimestre.objects.get(id=trimestre_id)
                                trimestres_cache[trimestre_id] = trimestre
                            except Trimestre.DoesNotExist:
                                raise Exception(f"No existe el trimestre con ID {trimestre_id}")
                        
                        trimestre = trimestres_cache[trimestre_id]
                        
                        # Verificar que el tipo de evaluación existe
                        if tipo_evaluacion_id not in tipos_eval_cache:
                            try:
                                tipo_evaluacion = TipoEvaluacion.objects.get(id=tipo_evaluacion_id)
                                tipos_eval_cache[tipo_evaluacion_id] = tipo_evaluacion
                            except TipoEvaluacion.DoesNotExist:
                                raise Exception(f"No existe el tipo de evaluación con ID {tipo_evaluacion_id}")
                        
                        tipo_evaluacion = tipos_eval_cache[tipo_evaluacion_id]
                        
                        # Convertir fecha
                        fecha_registro = datetime.strptime(row['fecha_registro'], '%Y-%m-%d').date()
                        
                        # Convertir valores numéricos
                        porcentaje_nota_final = Decimal(row['porcentaje_nota_final'])
                        
                        # IMPORTANTE: Usamos EvaluacionParticipacion en lugar de EvaluacionEntregable
                        evaluacion, created = EvaluacionParticipacion.objects.get_or_create(
                            titulo=row['titulo'],
                            materia=materia,
                            trimestre=trimestre,
                            defaults={
                                'descripcion': row['descripcion'],
                                'tipo_evaluacion': tipo_evaluacion,
                                'fecha_registro': fecha_registro,
                                'criterios_participacion': row['criterios_participacion'],
                                'escala_calificacion': row['escala_calificacion'],
                                'porcentaje_nota_final': porcentaje_nota_final,
                                'activo': True,
                                'publicado': True
                            }
                        )
                        
                        # Si la evaluación ya existía, actualizar sus datos
                        if not created:
                            evaluacion.descripcion = row['descripcion']
                            evaluacion.tipo_evaluacion = tipo_evaluacion
                            evaluacion.fecha_registro = fecha_registro
                            evaluacion.criterios_participacion = row['criterios_participacion']
                            evaluacion.escala_calificacion = row['escala_calificacion']
                            evaluacion.porcentaje_nota_final = porcentaje_nota_final
                            evaluacion.save()
                        
                        if created:
                            creados += 1
                            print(f"✓ Creada participación: {row['titulo']} - {materia.nombre}")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizada participación: {row['titulo']} - {materia.nombre}")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE PARTICIPACIONES 2022 =====")
            print(f"Total de registros procesados: {total}")
            print(f"Participaciones creadas: {creados}")
            print(f"Participaciones actualizadas: {actualizados}")
            print(f"Errores: {errores}")
            print("=================================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_participaciones_csv()