import os
import django
import sys
import csv
import time
from django.db import transaction
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Curso, Materia, Trimestre, TipoEvaluacion, EvaluacionParticipacion, Calificacion
from Usuarios.models import Usuario
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

def importar_participaciones_csv():
    """
    Importa participaciones desde el archivo CSV a la base de datos.
    """
    
    tiempo_inicio = time.time()
    csv_path = '../csv/participaciones_2022_2025.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        print(f"Iniciando importación desde {csv_path}...")
        
        # Verificar que exista el tipo de evaluación para participaciones
        tipo_participacion, created = TipoEvaluacion.objects.get_or_create(
            id=3, 
            defaults={"nombre": "Participación"}
        )
        if created:
            print("Se ha creado el tipo de evaluación 'Participación' con ID 3")
        else:
            print(f"El tipo de evaluación existe: {tipo_participacion}")
        
        # Obtener ContentType para EvaluacionParticipacion
        content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Pre-cargar datos en memoria para reducir consultas
        print("Cargando datos de referencia...")
        estudiantes = {usuario.codigo: usuario for usuario in Usuario.objects.filter(rol_id=2)}
        print(f"Estudiantes cargados: {len(estudiantes)}")
        
        cursos = {curso.id: curso for curso in Curso.objects.all()}
        print(f"Cursos cargados: {len(cursos)}")
        
        trimestres = {trimestre.id: trimestre for trimestre in Trimestre.objects.all()}
        print(f"Trimestres cargados: {len(trimestres)}")
        
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
        print(f"El archivo CSV contiene {row_count} participaciones para importar")
        
        participaciones_creadas = 0
        calificaciones_creadas = 0
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
                        
                        # Convertir fecha
                        fecha_registro = datetime.strptime(row['fecha_registro'], "%Y-%m-%d").date()
                        
                        # PASO 1: Crear la evaluación de participación
                        participacion = EvaluacionParticipacion(
                            titulo=row['titulo'],
                            descripcion=row['descripcion'],
                            materia=materia,
                            trimestre=trimestre,
                            tipo_evaluacion=tipo_participacion,
                            porcentaje_nota_final=Decimal(row['porcentaje_nota_final']),
                            activo=True,
                            publicado=True,
                            fecha_registro=fecha_registro
                        )
                        participacion.save()
                        participaciones_creadas += 1
                        
                        # PASO 2: Crear la calificación asociada
                        fecha_registro_datetime = datetime.combine(fecha_registro, datetime.min.time())
                        fecha_registro_aware = timezone.make_aware(fecha_registro_datetime)
                        
                        calificacion = Calificacion(
                            content_type=content_type,
                            object_id=participacion.id,
                            estudiante=estudiante,
                            nota=Decimal(row['calificacion']),
                            fecha_entrega=fecha_registro_aware,  # Fecha con zona horaria
                            entrega_tardia=False,
                            penalizacion_aplicada=Decimal('0.00'),
                            finalizada=True,
                            fecha_calificacion=fecha_registro_aware,  # Fecha con zona horaria
                            observaciones=f"Participación en clase - {row['fecha_registro']}"
                        )
                        calificacion.save()
                        calificaciones_creadas += 1
                        
                        # Mostrar progreso
                        if participaciones_creadas % 100 == 0:
                            print(f"Progreso: {participaciones_creadas} participaciones creadas")
                        
                    except Exception as e:
                        print(f"Error al procesar fila: {str(e)}")
                        errores += 1
                
                print(f"Transacción completada: {participaciones_creadas} participaciones creadas, {calificaciones_creadas} calificaciones asociadas, {errores} errores")
            
            tiempo_total = time.time() - tiempo_inicio
            
            print("\n===== RESUMEN DE IMPORTACIÓN =====")
            print(f"Total evaluaciones creadas: {participaciones_creadas}")
            print(f"Total calificaciones creadas: {calificaciones_creadas}")
            print(f"Errores encontrados: {errores}")
            print(f"Tiempo total: {tiempo_total:.2f} segundos")
            
            # Verificar resultados
            total_participaciones = EvaluacionParticipacion.objects.count()
            print(f"Total de evaluaciones de participación en el sistema: {total_participaciones}")
            
            # Mostrar calificaciones por estudiante
            print("\nCalificaciones de participación por estudiante:")
            calificaciones_por_estudiante = Calificacion.objects.filter(
                content_type=content_type
            ).values(
                'estudiante__codigo', 
                'estudiante__nombre',
                'estudiante__apellido'
            ).annotate(
                total=Count('id')
            ).order_by('-total')
            
            for c in calificaciones_por_estudiante:
                print(f"  {c['estudiante__nombre']} {c['estudiante__apellido']} ({c['estudiante__codigo']}): {c['total']} calificaciones")
            
            print("=================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_participaciones_csv()