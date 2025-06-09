import os
import sys
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import time
from django.utils import timezone

# Primero configuramos el entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# Ahora inicializamos Django
import django
django.setup()

# Solo después de inicializar Django importamos los módulos de Django
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Calificacion, EvaluacionParticipacion, Materia, Trimestre
from Usuarios.models import Usuario

def importar_calificaciones_participaciones_csv(actualizar_existentes=True, test_mode=False):
    """
    Importa calificaciones de participaciones desde el archivo CSV a la base de datos.
    
    Parámetros:
    - actualizar_existentes: Si es True, actualiza las calificaciones existentes; si es False, las omite.
    - test_mode: Si es True, valida los datos pero no realiza cambios en la base de datos.
    """
    
    # Definir campos requeridos para validación
    required_fields = [
        'estudiante_codigo', 'estudiante_nombre', 'estudiante_apellido', 
        'materia', 'curso_id', 'titulo_evaluacion', 'tipo_evaluacion_id', 
        'trimestre_id', 'nota', 'nota_final', 'escala_calificacion',
        'porcentaje_nota_final', 'fecha_calificacion'
    ]
    
    # Usar ruta absoluta para asegurar acceso al archivo
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv', 'calificaciones_participaciones_2022.csv')
    
    # Verificar que el archivo existe
    if not os.path.isfile(csv_path):
        print(f"Error: El archivo {csv_path} no existe.")
        return
    
    # Mostrar modo de ejecución
    if test_mode:
        print("⚠️ Ejecutando en modo prueba - no se realizarán cambios en la base de datos")
    
    # Obtener el ContentType para EvaluacionParticipacion
    participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
    
    # Contadores para estadísticas
    total = 0
    creados = 0
    actualizados = 0
    errores = 0
    no_encontrados = 0
    omitidos = 0
    
    # Cache para estudiantes, materias y evaluaciones
    estudiantes_cache = {}
    materias_cache = {}
    evaluaciones_cache = {}
    
    # Iniciar tiempo de ejecución
    tiempo_inicio = time.time()
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Usar transacción para garantizar la integridad de los datos
        with transaction.atomic():
            for row in csv_reader:
                total += 1
                try:
                    # Al inicio del procesamiento de cada fila
                    if not all(required_field in row for required_field in required_fields):
                        print(f"✗ Fila {total} con campos requeridos faltantes")
                        errores += 1
                        continue
                    
                    # Obtener datos del estudiante
                    codigo_estudiante = row['estudiante_codigo']
                    if codigo_estudiante not in estudiantes_cache:
                        try:
                            estudiante = Usuario.objects.get(codigo=codigo_estudiante)
                            estudiantes_cache[codigo_estudiante] = estudiante
                        except Usuario.DoesNotExist:
                            print(f"✗ No se encontró el estudiante con código {codigo_estudiante}")
                            no_encontrados += 1
                            continue
                    
                    estudiante = estudiantes_cache[codigo_estudiante]
                    
                    # Buscar la materia por nombre y curso_id
                    materia_nombre = row['materia']
                    curso_id = int(row['curso_id'])
                    materia_key = f"{materia_nombre}_{curso_id}"
                    
                    if materia_key not in materias_cache:
                        try:
                            materia = Materia.objects.get(nombre=materia_nombre, curso_id=curso_id)
                            materias_cache[materia_key] = materia
                        except Materia.DoesNotExist:
                            print(f"✗ No se encontró la materia '{materia_nombre}' para el curso {curso_id}")
                            no_encontrados += 1
                            continue
                    
                    materia = materias_cache[materia_key]
                    
                    # Buscar la evaluación por título, tipo y trimestre
                    titulo_evaluacion = row['titulo_evaluacion']
                    trimestre_id = int(row['trimestre_id'])
                    tipo_evaluacion_id = int(row['tipo_evaluacion_id'])
                    
                    eval_key = f"{titulo_evaluacion}_{trimestre_id}_{materia.id}"
                    
                    if eval_key not in evaluaciones_cache:
                        try:
                            evaluacion = EvaluacionParticipacion.objects.get(
                                titulo=titulo_evaluacion,
                                materia=materia,
                                trimestre_id=trimestre_id,
                                tipo_evaluacion_id=tipo_evaluacion_id
                            )
                            evaluaciones_cache[eval_key] = evaluacion
                        except EvaluacionParticipacion.DoesNotExist:
                            print(f"✗ No se encontró la evaluación '{titulo_evaluacion}' para la materia '{materia_nombre}', trimestre {trimestre_id}")
                            no_encontrados += 1
                            continue  # Continuamos con el siguiente registro
                    
                    evaluacion = evaluaciones_cache[eval_key]
                    
                    # Convertir valores
                    try:
                        nota = Decimal(row['nota'])
                    except InvalidOperation:
                        print(f"✗ Valor de nota inválido: {row['nota']}")
                        errores += 1
                        continue
                    
                    # Leer nota_final pero no la usaremos directamente en la creación
                    nota_final_csv = Decimal(row['nota_final'])

                    # Convertir fechas a formato aware (con zona horaria)
                    fecha_naive = datetime.strptime(row['fecha_calificacion'], '%Y-%m-%d %H:%M:%S')
                    fecha_calificacion = timezone.make_aware(fecha_naive)

                    finalizada = True
                    if 'finalizada' in row:
                        finalizada = row['finalizada'].lower() == 'true'
                    
                    # Antes de crear o actualizar una calificación
                    calificacion_existente = Calificacion.objects.filter(
                        content_type=participacion_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante
                    ).exists()
                    
                    if calificacion_existente and not actualizar_existentes:
                        print(f"⚠ Omitiendo calificación existente: {estudiante.get_full_name()} - {evaluacion.titulo}")
                        omitidos += 1
                        continue
                    
                    # En modo prueba, no creamos/actualizamos realmente
                    if test_mode:
                        tiempo_actual = time.time() - tiempo_inicio
                        if calificacion_existente:
                            actualizados += 1
                            print(f"⚠️ [MODO PRUEBA] [{tiempo_actual:.2f}s] Se actualizaría: {estudiante.codigo} - {estudiante.get_full_name()} - {evaluacion.titulo}")
                        else:
                            creados += 1
                            print(f"⚠️ [MODO PRUEBA] [{tiempo_actual:.2f}s] Se crearía: {estudiante.codigo} - {estudiante.get_full_name()} - {evaluacion.titulo}")
                        continue
                    
                    # Buscar o crear la calificación
                    calificacion, created = Calificacion.objects.update_or_create(
                        content_type=participacion_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        defaults={
                            'nota': nota,
                            'fecha_entrega': fecha_calificacion,
                            'entrega_tardia': False,  # Para participaciones no aplica entrega tardía
                            'penalizacion_aplicada': Decimal('0.0'),  # Sin penalización
                            'finalizada': finalizada,
                            'fecha_calificacion': fecha_calificacion,
                            'observaciones': f"Calificación de participación importada del CSV 2022 {total}",
                            'retroalimentacion': None,
                            'calificado_por': None
                        }
                    )
                    
                    tiempo_actual = time.time() - tiempo_inicio
                    if created:
                        creados += 1
                        print(f"✓ [{tiempo_actual:.2f}s] Creada calificación: {estudiante.codigo} - {estudiante.get_full_name()} - {evaluacion.titulo}")
                    else:
                        actualizados += 1
                        print(f"↻ [{tiempo_actual:.2f}s] Actualizada calificación: {estudiante.codigo} - {estudiante.get_full_name()} - {evaluacion.titulo}")
                
                except Exception as e:
                    errores += 1
                    print(f"✗ Error al procesar la fila {total}: {str(e)}")
                    print(f"  Datos: {row}")
            
            # Si estamos en modo prueba, revertimos la transacción
            if test_mode:
                transaction.set_rollback(True)
                print("\n⚠️ MODO PRUEBA - Todas las transacciones han sido revertidas")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE CALIFICACIONES DE PARTICIPACIÓN 2022 =====")
            print(f"Total de registros procesados: {total}")
            print(f"Calificaciones creadas: {creados}")
            print(f"Calificaciones actualizadas: {actualizados}")
            print(f"Registros no encontrados: {no_encontrados}")
            print(f"Errores: {errores}")
            print(f"Calificaciones omitidas: {omitidos}")
            print("=================================================")

if __name__ == '__main__':
    # Ofrecer opciones al usuario para ejecutar el script
    print("Importación de calificaciones de participación 2022")
    print("==================================================")
    print("1. Ejecutar importación normal (actualizar existentes)")
    print("2. Ejecutar importación sin actualizar existentes")
    print("3. Ejecutar en modo prueba (sin guardar cambios)")
    print("0. Salir")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == "1":
        importar_calificaciones_participaciones_csv(actualizar_existentes=True)
    elif opcion == "2":
        importar_calificaciones_participaciones_csv(actualizar_existentes=False)
    elif opcion == "3":
        importar_calificaciones_participaciones_csv(test_mode=True)
    else:
        print("Saliendo sin realizar cambios.")