import os
import django
import sys
import csv
import time
from django.db import transaction
from decimal import Decimal
from datetime import datetime

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Curso, Materia, Trimestre, EvaluacionEntregable, TipoEvaluacion
from Usuarios.models import Usuario
from django.db.models import Count

def importar_evaluaciones_csv():
    """
    Importa evaluaciones desde el archivo CSV a la base de datos.
    """
    
    tiempo_inicio = time.time()
    csv_path = '../csv/evaluaciones_estudiantes.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        print(f"Iniciando importación desde {csv_path}...")
        
        # Verificar que existan tipos de evaluación
        tipos_evaluacion = list(TipoEvaluacion.objects.all())
        if not tipos_evaluacion:
            print("Creando tipos de evaluación básicos...")
            TipoEvaluacion.objects.get_or_create(id=1, defaults={"nombre": "Parcial"})
            TipoEvaluacion.objects.get_or_create(id=2, defaults={"nombre": "Práctico"})
            tipos_evaluacion = list(TipoEvaluacion.objects.all())
        
        print(f"Tipos de evaluación disponibles: {len(tipos_evaluacion)}")
        for t in tipos_evaluacion:
            print(f"  - ID {t.id}: {t.nombre}")
        
        # Pre-cargar datos en memoria para reducir consultas
        print("Cargando datos de referencia...")
        estudiantes = {usuario.codigo: usuario for usuario in Usuario.objects.filter(rol_id=2)}
        print(f"Estudiantes cargados: {len(estudiantes)}")
        
        cursos = {curso.id: curso for curso in Curso.objects.all()}
        print(f"Cursos cargados: {len(cursos)}")
        
        trimestres = {trimestre.id: trimestre for trimestre in Trimestre.objects.all()}
        print(f"Trimestres cargados: {len(trimestres)}")
        
        tipos_evaluacion = {tipo.id: tipo for tipo in TipoEvaluacion.objects.all()}
        print(f"Tipos de evaluación cargados: {len(tipos_evaluacion)}")
        
        # Crear diccionario para almacenar materias por curso y nombre
        materias = {}
        for materia in Materia.objects.all():
            if materia.curso_id not in materias:
                materias[materia.curso_id] = {}
            materias[materia.curso_id][materia.nombre] = materia
        print(f"Materias cargadas para {len(materias)} cursos")
        
        # Contar filas del CSV
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_counter = csv.reader(file)
            next(csv_counter)  # Saltamos la cabecera
            row_count = sum(1 for _ in csv_counter)
        print(f"El archivo CSV contiene {row_count} evaluaciones para importar")
        
        evaluaciones_creadas = 0
        errores = 0
        
        # Procesar el CSV
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Usar transacción para asegurar que todos los datos se guarden correctamente
            with transaction.atomic():
                print("Iniciando transacción...")
                for row in csv_reader:
                    try:
                        # Obtener el estudiante
                        estudiante = estudiantes.get(row['estudiante_codigo'])
                        if not estudiante:
                            print(f"Estudiante no encontrado: {row['estudiante_codigo']}")
                            errores += 1
                            continue
                        
                        # Obtener el curso
                        curso_id = int(row['curso_id'])
                        curso = cursos.get(curso_id)
                        if not curso:
                            print(f"Curso no encontrado: {curso_id}")
                            errores += 1
                            continue
                        
                        # Obtener la materia
                        if curso_id not in materias or row['materia'] not in materias[curso_id]:
                            # Crear la materia si no existe
                            print(f"Creando materia '{row['materia']}' para curso {curso_id}")
                            nueva_materia = Materia(
                                nombre=row['materia'],
                                curso=curso
                            )
                            nueva_materia.save()
                            if curso_id not in materias:
                                materias[curso_id] = {}
                            materias[curso_id][row['materia']] = nueva_materia
                        
                        materia = materias[curso_id][row['materia']]
                        
                        # Obtener el trimestre
                        trimestre_id = int(row['trimestre_id'])
                        trimestre = trimestres.get(trimestre_id)
                        if not trimestre:
                            print(f"Trimestre no encontrado: {trimestre_id}")
                            errores += 1
                            continue
                        
                        # Obtener tipo de evaluación
                        tipo_evaluacion_id = int(row['tipo_evaluacion_id'])
                        tipo_evaluacion = tipos_evaluacion.get(tipo_evaluacion_id)
                        if not tipo_evaluacion:
                            print(f"Tipo de evaluación no encontrado: {tipo_evaluacion_id}")
                            errores += 1
                            continue
                        
                        # Convertir fechas
                        fecha_asignacion = datetime.strptime(row['fecha_asignacion'], "%Y-%m-%d").date()
                        fecha_entrega = datetime.strptime(row['fecha_entrega'], "%Y-%m-%d").date()
                        
                        # Crear la evaluación
                        evaluacion = EvaluacionEntregable(
                            materia=materia,
                            trimestre=trimestre,
                            tipo_evaluacion=tipo_evaluacion,  # CORREGIDO: Cambiado de 'tipo' a 'tipo_evaluacion'
                            titulo=row['titulo'],
                            descripcion=row['descripcion'],
                            fecha_asignacion=fecha_asignacion,
                            fecha_entrega=fecha_entrega,
                            nota_maxima=Decimal(row['nota_maxima']),
                            nota_minima_aprobacion=Decimal(row['nota_minima_aprobacion']),
                            porcentaje_nota_final=Decimal(row['porcentaje_nota_final']),
                            permite_entrega_tardia=row['permite_entrega_tardia'].lower() == 'true',
                            penalizacion_tardio=Decimal(row['penalizacion_tardio'])
                        )
                        evaluacion.save()
                        evaluaciones_creadas += 1
                        
                        # Mostrar progreso
                        if evaluaciones_creadas % 100 == 0:
                            print(f"Progreso: {evaluaciones_creadas} evaluaciones creadas")
                        
                    except Exception as e:
                        print(f"Error al procesar fila: {str(e)}")
                        errores += 1
                
                print(f"Transacción completada: {evaluaciones_creadas} evaluaciones creadas, {errores} errores")
            
            tiempo_total = time.time() - tiempo_inicio
            
            print("\n===== RESUMEN DE IMPORTACIÓN =====")
            print(f"Total evaluaciones creadas: {evaluaciones_creadas}")
            print(f"Errores encontrados: {errores}")
            print(f"Tiempo total: {tiempo_total:.2f} segundos")
            
            # Verificar resultados
            total_evaluaciones = EvaluacionEntregable.objects.count()
            print(f"Total de evaluaciones en el sistema después de la importación: {total_evaluaciones}")
            
            # Mostrar evaluaciones por materia
            print("\nEvaluaciones por materia:")
            evaluaciones_por_materia = EvaluacionEntregable.objects.values('materia__nombre').annotate(
                total=Count('id')
            ).order_by('-total')
            
            for e in evaluaciones_por_materia[:10]:  # Mostrar las 10 materias con más evaluaciones
                print(f"  {e['materia__nombre']}: {e['total']} evaluaciones")
            
            print("=================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_evaluaciones_csv()