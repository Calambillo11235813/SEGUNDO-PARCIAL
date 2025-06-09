import os
import django
import sys
import csv
from django.db import transaction
from datetime import datetime
from decimal import Decimal

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar los modelos después de configurar Django
from Cursos.models import Materia, Curso, Trimestre, TipoEvaluacion, EvaluacionEntregable

def importar_evaluaciones_csv():
    """
    Importa evaluaciones y prácticos desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    materia,curso_id,tipo_evaluacion_id,trimestre_id,titulo,descripcion,fecha_asignacion,fecha_entrega,nota_maxima,nota_minima_aprobacion,porcentaje_nota_final,permite_entrega_tardia,penalizacion_tardio
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/evaluaciones_practicos_2022.csv'
    
    # Verificar que existan los tipos de evaluación necesarios
    try:
        # Asegurar que existen los tipos de evaluación básicos (id 1: Parcial, id 2: Práctico)
        for tipo_id, nombre in [(1, 'EXAMEN'), (2, 'TRABAJO')]:
            tipo_eval, created = TipoEvaluacion.objects.get_or_create(
                id=tipo_id,
                defaults={
                    'nombre': nombre, 
                    'descripcion': f'Evaluación tipo {nombre}'
                }
            )
            if created:
                print(f"✓ Creado tipo de evaluación: {nombre} (ID: {tipo_id})")
    except Exception as e:
        print(f"Error al verificar tipos de evaluación: {str(e)}")
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
            
            # Cache para materias por nombre y curso
            materias_cache = {}
            
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
                        try:
                            trimestre = Trimestre.objects.get(id=trimestre_id)
                        except Trimestre.DoesNotExist:
                            raise Exception(f"No existe el trimestre con ID {trimestre_id}")
                        
                        # Verificar que el tipo de evaluación existe
                        try:
                            tipo_evaluacion = TipoEvaluacion.objects.get(id=tipo_evaluacion_id)
                        except TipoEvaluacion.DoesNotExist:
                            raise Exception(f"No existe el tipo de evaluación con ID {tipo_evaluacion_id}")
                        
                        # Convertir fechas
                        fecha_asignacion = datetime.strptime(row['fecha_asignacion'], '%Y-%m-%d').date()
                        fecha_entrega = datetime.strptime(row['fecha_entrega'], '%Y-%m-%d').date()
                        
                        # Convertir valores numéricos
                        nota_maxima = Decimal(row['nota_maxima'])
                        nota_minima_aprobacion = Decimal(row['nota_minima_aprobacion'])
                        porcentaje_nota_final = Decimal(row['porcentaje_nota_final'])
                        penalizacion_tardio = Decimal(row['penalizacion_tardio'])
                        
                        # Convertir valores booleanos
                        permite_entrega_tardia = row['permite_entrega_tardia'].lower() == 'true'
                        
                        # Buscar o crear la evaluación
                        # Ahora usamos EvaluacionEntregable en lugar de Evaluacion
                        evaluacion, created = EvaluacionEntregable.objects.get_or_create(
                            titulo=row['titulo'],
                            materia=materia,
                            trimestre=trimestre,
                            defaults={
                                'descripcion': row['descripcion'],
                                'tipo_evaluacion': tipo_evaluacion,
                                'fecha_asignacion': fecha_asignacion,
                                'fecha_entrega': fecha_entrega,
                                'nota_maxima': nota_maxima,
                                'nota_minima_aprobacion': nota_minima_aprobacion,
                                'porcentaje_nota_final': porcentaje_nota_final,
                                'permite_entrega_tardia': permite_entrega_tardia,
                                'penalizacion_tardio': penalizacion_tardio,
                                'publicado': True,
                                'activo': True
                            }
                        )
                        
                        # Si la evaluación ya existía, actualizar sus datos
                        if not created:
                            evaluacion.descripcion = row['descripcion']
                            evaluacion.tipo_evaluacion = tipo_evaluacion
                            evaluacion.fecha_asignacion = fecha_asignacion
                            evaluacion.fecha_entrega = fecha_entrega
                            evaluacion.nota_maxima = nota_maxima
                            evaluacion.nota_minima_aprobacion = nota_minima_aprobacion
                            evaluacion.porcentaje_nota_final = porcentaje_nota_final
                            evaluacion.permite_entrega_tardia = permite_entrega_tardia
                            evaluacion.penalizacion_tardio = penalizacion_tardio
                            evaluacion.save()
                        
                        if created:
                            creados += 1
                            print(f"✓ Creada evaluación: {row['titulo']} - {materia.nombre}")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizada evaluación: {row['titulo']} - {materia.nombre}")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE EVALUACIONES 2022 =====")
            print(f"Total de registros procesados: {total}")
            print(f"Evaluaciones creadas: {creados}")
            print(f"Evaluaciones actualizadas: {actualizados}")
            print(f"Errores: {errores}")
            print("=================================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_evaluaciones_csv()