import os
import django
import sys
import csv
from datetime import datetime
from django.db import transaction
from collections import defaultdict
import time

# Configuración Django (igual que antes)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Materia, Trimestre, Curso, Asistencia
from Usuarios.models import Usuario

def importar_asistencias_segundo_trimestre_optimizado():
    """
    Versión optimizada con prints mínimos para máximo rendimiento
    """
    csv_path = os.path.join(project_root, 'csv', 'segundo_trimestre_2024.csv')
    
    if not os.path.isfile(csv_path):
        print(f"❌ Error: El archivo {csv_path} no existe.")
        return

    inicio_tiempo = time.time()
    print("🚀 Iniciando importación optimizada del Segundo Trimestre 2024...")
    
    total = 0
    creados = 0
    errores = 0
    curso_actual = None
    registros_por_curso = defaultdict(int)

    # Caches optimizados
    estudiantes_cache = {}
    materias_cache = {}
    trimestres_cache = {}
    cursos_cache = {}

    # Pre-cargar trimestre para evitar consultas repetidas
    try:
        trimestre = Trimestre.objects.get(id=11)
        trimestres_cache[11] = trimestre
        print(f"✅ Trimestre cargado: {trimestre.nombre}")
    except Trimestre.DoesNotExist:
        print("❌ Trimestre ID 11 no encontrado")
        return

    try:
        # Contar registros solo una vez
        with open(csv_path, mode='r', encoding='utf-8') as file:
            total_registros = sum(1 for line in file) - 1
        
        print(f"📊 Total registros: {total_registros:,}")
        print("⏳ Procesando datos... (modo silencioso para velocidad)")
        print()

        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            with transaction.atomic():
                for row in csv_reader:
                    total += 1
                    try:
                        estudiante_codigo = row['estudiante_codigo']
                        materia_nombre = row['materia']
                        curso_id = int(row['curso_id'])
                        trimestre_id = int(row['trimestre_id'])
                        fecha = datetime.strptime(row['fecha'], '%Y-%m-%d').date()
                        presente = row['presente'].strip().lower() == 'true'
                        justificada = row['justificada'].strip().lower() == 'true'

                        # 📊 Print SOLO cuando cambia el curso (máximo ~10 prints)
                        if curso_actual != curso_id:
                            if curso_actual is not None:
                                # Solo mostrar resumen del curso anterior
                                tiempo_transcurrido = time.time() - inicio_tiempo
                                print(f"✅ Curso {curso_actual}: {registros_por_curso[curso_actual]:,} registros ({tiempo_transcurrido:.1f}s)")
                            
                            curso_actual = curso_id
                            
                            # Cargar info del curso solo una vez
                            if curso_id not in cursos_cache:
                                try:
                                    curso = Curso.objects.get(id=curso_id)
                                    cursos_cache[curso_id] = curso
                                except Curso.DoesNotExist:
                                    cursos_cache[curso_id] = None

                        # Optimizar búsquedas con cache
                        if estudiante_codigo not in estudiantes_cache:
                            try:
                                estudiante = Usuario.objects.get(codigo=estudiante_codigo)
                                estudiantes_cache[estudiante_codigo] = estudiante
                            except Usuario.DoesNotExist:
                                errores += 1
                                continue
                        estudiante = estudiantes_cache[estudiante_codigo]

                        materia_key = f"{materia_nombre}_{curso_id}"
                        if materia_key not in materias_cache:
                            try:
                                materia = Materia.objects.get(nombre=materia_nombre, curso_id=curso_id)
                                materias_cache[materia_key] = materia
                            except Materia.DoesNotExist:
                                errores += 1
                                continue
                        materia = materias_cache[materia_key]

                        # Usar trimestre pre-cargado
                        trimestre = trimestres_cache[11]

                        # Crear asistencia directamente (sin verificar duplicados para velocidad)
                        Asistencia.objects.create(
                            estudiante=estudiante,
                            materia=materia,
                            trimestre=trimestre,
                            fecha=fecha,
                            presente=presente,
                            justificada=justificada
                        )
                        
                        creados += 1
                        registros_por_curso[curso_id] += 1
                        
                        # 📊 Print progreso solo cada 5000 registros (máximo 10-20 prints)
                        if total % 5000 == 0:
                            porcentaje = (total / total_registros) * 100
                            tiempo_transcurrido = time.time() - inicio_tiempo
                            velocidad = total / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
                            print(f"📊 {total:,}/{total_registros:,} ({porcentaje:.1f}%) | {velocidad:.0f} reg/seg | {tiempo_transcurrido:.1f}s")
                    
                    except Exception as e:
                        errores += 1
                        # Solo print errores cada 100 errores para evitar spam
                        if errores % 100 == 1:
                            print(f"⚠️  Error en fila {total}: {str(e)}")

        # Resumen final
        tiempo_total = time.time() - inicio_tiempo
        velocidad_promedio = total / tiempo_total if tiempo_total > 0 else 0
        
        print()
        print("=" * 60)
        print("📋 RESUMEN FINAL - SEGUNDO TRIMESTRE 2024")
        print("=" * 60)
        print(f"📊 Registros procesados: {total:,}")
        print(f"✅ Asistencias creadas: {creados:,}")
        print(f"❌ Errores: {errores:,}")
        print(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos")
        print(f"🚀 Velocidad promedio: {velocidad_promedio:.0f} registros/segundo")
        print(f"📈 Tasa de éxito: {(creados/total)*100:.1f}%")
        
        print(f"\n🏫 RESUMEN POR CURSO:")
        for curso_id in sorted(registros_por_curso.keys()):
            print(f"   Curso {curso_id}: {registros_por_curso[curso_id]:,} registros")
        
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error general: {str(e)}")

# Versión con MÍNIMOS prints para máxima velocidad
def importar_modo_rapido():
    """Versión ultra-rápida con prints mínimos"""
    csv_path = os.path.join(project_root, 'csv', 'segundo_trimestre_2024.csv')
    
    inicio = time.time()
    print("🚀 Modo ultra-rápido iniciado...")
    
    total = 0
    creados = 0
    
    # Pre-cargar TODO en memoria para máxima velocidad
    print("📊 Pre-cargando datos...")
    estudiantes_dict = {u.codigo: u for u in Usuario.objects.filter(rol__nombre='Estudiante')}
    materias_dict = {f"{m.nombre}_{m.curso_id}": m for m in Materia.objects.all()}
    trimestre = Trimestre.objects.get(id=11)
    
    asistencias_bulk = []
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            total += 1
            try:
                estudiante = estudiantes_dict.get(row['estudiante_codigo'])
                materia = materias_dict.get(f"{row['materia']}_{row['curso_id']}")
                
                if estudiante and materia:
                    asistencias_bulk.append(Asistencia(
                        estudiante=estudiante,
                        materia=materia,
                        trimestre=trimestre,
                        fecha=datetime.strptime(row['fecha'], '%Y-%m-%d').date(),
                        presente=row['presente'].strip().lower() == 'true',
                        justificada=row['justificada'].strip().lower() == 'true'
                    ))
                    creados += 1
                    
                    # Insertar en lotes de 1000 para optimizar
                    if len(asistencias_bulk) >= 1000:
                        Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
                        asistencias_bulk = []
                        
            except Exception:
                pass  # Silenciar errores para máxima velocidad
    
    # Insertar registros restantes
    if asistencias_bulk:
        Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
    
    tiempo_total = time.time() - inicio
    print(f"✅ Completado: {creados:,}/{total:,} en {tiempo_total:.2f}s ({creados/tiempo_total:.0f} reg/seg)")

if __name__ == '__main__':
    print("Selecciona el modo de importación:")
    print("1. Normal (con progreso detallado)")
    print("2. Optimizado (progreso mínimo)")
    print("3. Ultra-rápido (sin progreso)")
    
    opcion = input("Opción (1-3): ").strip()
    
    if opcion == "1":
        # Tu función original
        pass
    elif opcion == "2":
        importar_asistencias_segundo_trimestre_optimizado()
    elif opcion == "3":
        importar_modo_rapido()
    else:
        print("❌ Opción inválida")