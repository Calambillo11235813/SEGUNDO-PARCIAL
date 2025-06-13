import os
import django
import sys
import csv
import time
from django.db import transaction
from datetime import datetime

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Curso, Materia, Trimestre, Asistencia
from Usuarios.models import Usuario
from django.db.models import Count

def importar_asistencias_csv():
    """
    Importa asistencias desde el archivo CSV a la base de datos.
    """
    
    tiempo_inicio = time.time()
    csv_path = '../csv/asistencias_multianuales.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        print(f"Iniciando importación desde {csv_path}...")
        
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
        print(f"El archivo CSV contiene {row_count} asistencias para importar")
        
        asistencias_creadas = 0
        errores = 0
        
        # Procesar el CSV
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Usar transacción para asegurar que todos los datos se guarden correctamente
            with transaction.atomic():
                print("Iniciando transacción...")
                counter = 0
                for row in csv_reader:
                    try:
                        # Mostrar progreso
                        counter += 1
                        if counter % 1000 == 0:
                            print(f"Procesando fila {counter}/{row_count} ({counter/row_count*100:.1f}%)")
                        
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
                            nueva_materia = Materia(
                                nombre=row['materia'],
                                curso=curso
                            )
                            nueva_materia.save()
                            if curso_id not in materias:
                                materias[curso_id] = {}
                            materias[curso_id][row['materia']] = nueva_materia
                            print(f"Creada materia '{row['materia']}' para curso {curso_id}")
                        
                        materia = materias[curso_id][row['materia']]
                        
                        # Obtener el trimestre
                        trimestre_id = int(row['trimestre_id'])
                        trimestre = trimestres.get(trimestre_id)
                        if not trimestre:
                            print(f"Trimestre no encontrado: {trimestre_id}")
                            errores += 1
                            continue
                        
                        # Convertir fecha
                        fecha = datetime.strptime(row['fecha'], "%Y-%m-%d").date()
                        
                        # Convertir valores booleanos
                        presente = row['presente'].lower() == 'true'
                        justificada = row['justificada'].lower() == 'true'
                        
                        # Crear la asistencia
                        asistencia = Asistencia(
                            estudiante=estudiante,
                            materia=materia,
                            trimestre=trimestre,
                            fecha=fecha,
                            presente=presente,
                            justificada=justificada
                        )
                        
                        # Verificar si ya existe para evitar duplicados
                        if not Asistencia.objects.filter(
                            estudiante=estudiante,
                            materia=materia,
                            fecha=fecha
                        ).exists():
                            asistencia.save()
                            asistencias_creadas += 1
                        
                    except Exception as e:
                        print(f"Error al procesar fila: {str(e)}")
                        errores += 1
                
                print(f"Transacción completada: {asistencias_creadas} asistencias creadas, {errores} errores")
            
            tiempo_total = time.time() - tiempo_inicio
            
            print("\n===== RESUMEN DE IMPORTACIÓN =====")
            print(f"Total asistencias creadas: {asistencias_creadas}")
            print(f"Errores encontrados: {errores}")
            print(f"Tiempo total: {tiempo_total:.2f} segundos")
            
            # Verificar resultados
            total_asistencias = Asistencia.objects.count()
            print(f"Total de asistencias en el sistema después de la importación: {total_asistencias}")
            
            # Mostrar asistencias por estudiante
            print("\nAsistencias por estudiante:")
            asistencias_por_estudiante = Asistencia.objects.values(
                'estudiante__codigo', 
                'estudiante__nombre',
                'estudiante__apellido'
            ).annotate(
                total=Count('id')
            ).order_by('-total')
            
            for a in asistencias_por_estudiante:
                print(f"  {a['estudiante__nombre']} {a['estudiante__apellido']} ({a['estudiante__codigo']}): {a['total']} asistencias")
            
            # Mostrar porcentaje de asistencia por estudiante
            print("\nPorcentaje de asistencia por estudiante:")
            for estudiante_codigo in ['2221', '2253']:
                estudiante = Usuario.objects.get(codigo=estudiante_codigo)
                total_asistencias = Asistencia.objects.filter(estudiante=estudiante).count()
                presentes = Asistencia.objects.filter(estudiante=estudiante, presente=True).count()
                
                if total_asistencias > 0:
                    porcentaje = presentes / total_asistencias * 100
                    print(f"  {estudiante.nombre} {estudiante.apellido}: {porcentaje:.1f}% ({presentes}/{total_asistencias})")
            
            print("=================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_asistencias_csv()