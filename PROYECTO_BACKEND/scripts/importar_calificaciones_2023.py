import os
import sys
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import time
from django.utils import timezone

# Primero configuramos el entorno Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# Ahora inicializamos Django
try:
    import django
    django.setup()
    import pandas as pd # type: ignore
except Exception as e:
    print(f"❌ Error inicializando Django o cargando dependencias: {e}")
    sys.exit(1)

# Solo después de inicializar Django importamos los módulos de Django
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Calificacion, EvaluacionEntregable, Materia, Trimestre
from Usuarios.models import Usuario

def diagnosticar_estructura_base_datos_2023():
    """Diagnóstico para verificar la estructura necesaria para importaciones 2023"""
    print("\n🔧 DIAGNÓSTICO DE ESTRUCTURA 2023:")
    print("=" * 50)
    
    # Verificar ContentType
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        print(f"✅ ContentType EvaluacionEntregable: ID {entregable_ct.id}")
    except Exception as e:
        print(f"❌ Error obteniendo ContentType: {e}")
        return False
    
    # Verificar evaluaciones 2023
    try:
        total_evaluaciones = EvaluacionEntregable.objects.filter(
            trimestre__id__in=[7, 8, 9]
        ).count()
        print(f"✅ Total evaluaciones entregables 2023: {total_evaluaciones}")
        if total_evaluaciones == 0:
            print("❌ ¡No hay evaluaciones entregables para 2023!")
            return False
    except Exception as e:
        print(f"❌ Error contando evaluaciones: {e}")
        return False
    
    # Verificar estudiantes
    try:
        total_estudiantes = Usuario.objects.filter(rol__id=2).count()
        print(f"✅ Total estudiantes (rol_id=2): {total_estudiantes}")
        if total_estudiantes == 0:
            print("❌ ¡No hay estudiantes!")
            return False
    except Exception as e:
        print(f"❌ Error contando estudiantes: {e}")
        return False
    
    # Verificar calificaciones existentes
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        calificaciones_2023 = Calificacion.objects.filter(
            content_type=entregable_ct,
            object_id__in=EvaluacionEntregable.objects.filter(
                trimestre__id__in=[7, 8, 9]
            ).values_list('id', flat=True)
        ).count()
        print(f"✅ Calificaciones entregables 2023 existentes: {calificaciones_2023}")
    except Exception as e:
        print(f"❌ Error contando calificaciones: {e}")
    
    # Verificar archivo CSV
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Tamaño del archivo
    csv_size = os.path.getsize(csv_path)
    print(f"✅ Archivo CSV 2023 encontrado: {csv_size:,} bytes")
    
    # Verificar estructura del CSV
    try:
        # Leer solo las primeras filas para análisis
        df_sample = pd.read_csv(csv_path, nrows=5)
        columnas = df_sample.columns.tolist()
        print(f"✅ Estructura CSV verificada: {len(columnas)} columnas")
        print(f"   📊 Muestra de trimestres en CSV: {sorted(df_sample['trimestre_id'].unique())}")
        print(f"   📋 Tipos de evaluación en muestra: {sorted(df_sample['tipo_evaluacion_id'].unique())}")
        
        # Verificar valores booleanos
        if 'entrega_tardia' in df_sample.columns and 'finalizada' in df_sample.columns:
            print(f"   ✅ Formato de campos booleanos verificado")
        else:
            print(f"   ⚠️ Faltan campos booleanos en el CSV")
    except Exception as e:
        print(f"❌ Error verificando estructura CSV: {e}")
        return False
        
    return True

def analizar_datos_csv_2023():
    """Analiza la estructura y contenido del archivo CSV de calificaciones 2023"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    print("\n📊 ANÁLISIS DE DATOS CSV 2023:")
    print("=" * 50)
    
    try:
        # Leer el CSV sin conversiones específicas
        df = pd.read_csv(csv_path)
        
        # Análisis general
        print("📈 ESTADÍSTICAS GENERALES:")
        print(f"   📊 Total registros: {len(df):,}")
        print(f"   👥 Estudiantes únicos: {df['estudiante_codigo'].nunique():,}")
        print(f"   📚 Materias únicas: {df['materia'].nunique():,}")
        print(f"   📝 Evaluaciones únicas: {df['titulo_evaluacion'].nunique():,}")
        print(f"   🎯 Tipos de evaluación: {sorted(df['tipo_evaluacion_id'].unique())}")
        
        # Análisis por trimestre
        print("\n📅 DISTRIBUCIÓN POR TRIMESTRE 2023:")
        for trimestre in sorted(df['trimestre_id'].unique()):
            trim_df = df[df['trimestre_id'] == trimestre]
            print(f"   📚 Trimestre {trimestre}: {len(trim_df):,} calificaciones, promedio: {pd.to_numeric(trim_df['nota']).mean():.2f}")
        
        # Análisis por tipo de evaluación
        print("\n🎯 DISTRIBUCIÓN POR TIPO DE EVALUACIÓN:")
        for tipo in sorted(df['tipo_evaluacion_id'].unique()):
            tipo_df = df[df['tipo_evaluacion_id'] == tipo]
            print(f"   📝 Tipo {tipo}: {len(tipo_df):,} calificaciones, promedio: {pd.to_numeric(tipo_df['nota']).mean():.2f}")
        
        # Estadísticas de notas
        print("\n📊 ESTADÍSTICAS DE NOTAS 2023:")
        df['nota_numeric'] = pd.to_numeric(df['nota'])
        print(f"   📈 Nota promedio: {df['nota_numeric'].mean():.2f}")
        print(f"   📊 Nota máxima: {df['nota_numeric'].max():.2f}")
        print(f"   📊 Nota mínima: {df['nota_numeric'].min():.2f}")
        print(f"   📈 Desviación estándar: {df['nota_numeric'].std():.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Error analizando CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estado_actual_2023():
    """Verifica el estado actual de calificaciones 2023 en la BD"""
    print("\n📊 VERIFICACIÓN DEL ESTADO ACTUAL 2023:")
    print("=" * 50)
    
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        print("🔍 Contando calificaciones por trimestre 2023...")
        
        # Contar por trimestre
        for trimestre_id in [7, 8, 9]:
            try:
                count = Calificacion.objects.filter(
                    content_type=entregable_ct,
                    object_id__in=EvaluacionEntregable.objects.filter(
                        trimestre__id=trimestre_id
                    ).values_list('id', flat=True)
                ).count()
                print(f"   📚 Trimestre {trimestre_id}: {count:,} calificaciones")
            except Exception as e:
                print(f"   ❌ Error contando trimestre {trimestre_id}: {e}")
        
        # Total general
        try:
            total_2023 = Calificacion.objects.filter(
                content_type=entregable_ct,
                object_id__in=EvaluacionEntregable.objects.filter(
                    trimestre__id__in=[7, 8, 9]
                ).values_list('id', flat=True)
            ).count()
            print(f"\n🎯 Total calificaciones 2023: {total_2023:,}")
        except Exception as e:
            print(f"❌ Error contando total 2023: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando estado actual: {e}")
        return False

def importar_calificaciones_2023_ULTRA_RAPIDO():
    """Versión ULTRA RÁPIDA para calificaciones 2023 - Optimizada para máximo rendimiento"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - CALIFICACIONES 2023")
    print("📚 Basado en optimizaciones exitosas de scripts anteriores")
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Contadores
    total = 0
    creados = 0
    actualizados = 0
    errores = 0
    
    # Pre-cargar ContentType
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    print(f"🔧 ContentType ID: {entregable_ct.id}")
    
    # Obtener datos en memoria para mejor rendimiento
    print("📊 Pre-cargando datos en cache...")
    estudiantes_cache = {e.codigo: e for e in Usuario.objects.filter(rol__id=2)}
    materias_cache = {}
    for m in Materia.objects.all():
        materias_cache[f"{m.nombre}_{m.curso_id}"] = m
    
    # Pre-cargar todas las evaluaciones entregables de 2023
    evaluaciones_cache = {}
    for eval in EvaluacionEntregable.objects.filter(trimestre__id__in=[7, 8, 9]):
        clave = f"{eval.titulo}_{eval.trimestre.id}_{eval.materia.id}"
        evaluaciones_cache[clave] = eval
    
    print(f"✅ Cache cargado:")
    print(f"   👥 {len(estudiantes_cache)} estudiantes")
    print(f"   📚 {len(materias_cache)} materias")
    print(f"   📝 {len(evaluaciones_cache)} evaluaciones")
    
    # Usar el enfoque tradicional con csv para mayor estabilidad
    print("📖 Leyendo CSV...")
    try:
        calificaciones_a_crear = []
        errores_list = []
        total_rows = 0
        batch_size = 5000
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Procesar en lotes
            current_batch = []
            
            for row in reader:
                total_rows += 1
                
                try:
                    # Buscar estudiante
                    codigo_estudiante = row['estudiante_codigo']
                    estudiante = estudiantes_cache.get(codigo_estudiante)
                    if not estudiante:
                        errores_list.append(f"Estudiante no encontrado: {codigo_estudiante}")
                        continue
                    
                    # Buscar materia
                    materia_nombre = row['materia']
                    curso_id = int(row['curso_id'])
                    materia_key = f"{materia_nombre}_{curso_id}"
                    materia = materias_cache.get(materia_key)
                    if not materia:
                        errores_list.append(f"Materia no encontrada: {materia_key}")
                        continue
                    
                    # Buscar evaluación
                    titulo_evaluacion = row['titulo_evaluacion']
                    trimestre_id = int(row['trimestre_id'])
                    eval_key = f"{titulo_evaluacion}_{trimestre_id}_{materia.id}"
                    evaluacion = evaluaciones_cache.get(eval_key)
                    
                    if not evaluacion:
                        errores_list.append(f"Evaluación no encontrada: {eval_key}")
                        continue
                    
                    # Convertir valores
                    try:
                        nota = Decimal(str(row['nota']))
                        # Ignorar nota_final del CSV, se calculará automáticamente
                        penalizacion = Decimal(str(row['penalizacion_aplicada'])) if 'penalizacion_aplicada' in row else Decimal('0')
                    except (ValueError, TypeError, InvalidOperation):
                        errores_list.append(f"Error convirtiendo valores numéricos: {row}")
                        continue
                    
                    # Convertir valores booleanos
                    entrega_tardia = False
                    if 'entrega_tardia' in row:
                        if isinstance(row['entrega_tardia'], str):
                            entrega_tardia = row['entrega_tardia'].lower() == 'true' or row['entrega_tardia'] == 'SI'
                        else:
                            entrega_tardia = bool(row['entrega_tardia'])
                    
                    finalizada = True
                    if 'finalizada' in row:
                        if isinstance(row['finalizada'], str):
                            finalizada = row['finalizada'].lower() == 'true' or row['finalizada'] == 'SI'
                        else:
                            finalizada = bool(row['finalizada'])
                    
                    # Fecha de calificación
                    fecha_calificacion = None
                    if 'fecha_calificacion' in row and row['fecha_calificacion']:
                        try:
                            fecha_naive = datetime.strptime(row['fecha_calificacion'], '%Y-%m-%d %H:%M:%S')
                            fecha_calificacion = timezone.make_aware(fecha_naive)
                        except ValueError:
                            fecha_calificacion = timezone.now()
                    
                    # Crear objeto para inserción masiva
                    calificacion = Calificacion(
                        content_type=entregable_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        nota=nota,
                        entrega_tardia=entrega_tardia,
                        penalizacion_aplicada=penalizacion,
                        finalizada=finalizada,
                        fecha_calificacion=fecha_calificacion,
                        observaciones=f"Calificación importada del CSV 2023 - fila {total_rows}"
                    )
                    
                    current_batch.append(calificacion)
                    
                    # Cuando alcanzamos el tamaño del lote, guardamos y reiniciamos
                    if len(current_batch) >= batch_size:
                        calificaciones_a_crear.extend(current_batch)
                        print(f"⏳ Procesadas {total_rows:,} filas ({len(calificaciones_a_crear):,} válidas)")
                        current_batch = []
                
                except Exception as e:
                    errores += 1
                    errores_list.append(f"Error procesando fila {total_rows}: {str(e)}")
                    if errores <= 5:  # Mostrar solo los primeros 5 errores
                        print(f"❌ Error: {str(e)}")
            
            # Agregar último lote
            if current_batch:
                calificaciones_a_crear.extend(current_batch)
        
        # Insertar en la base de datos
        print(f"💾 Guardando {len(calificaciones_a_crear):,} calificaciones en la base de datos...")
        total = len(calificaciones_a_crear)
        
        # Insertar en lotes con transacciones
        with transaction.atomic():
            Calificacion.objects.bulk_create(calificaciones_a_crear, batch_size=1000)
            creados = len(calificaciones_a_crear)
        
        # Resumen de errores
        errores = len(errores_list)
        if errores > 0:
            print(f"\n⚠️ Se encontraron {errores:,} errores:")
            for i, error in enumerate(errores_list[:10]):  # Mostrar solo los primeros 10
                print(f"   {i+1}. {error}")
            if errores > 10:
                print(f"   ... y {errores-10} errores más")
    
    except Exception as e:
        print(f"❌ Error general en la importación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Informar resultados
    fin = time.time()
    tiempo_total = fin - inicio
    registros_por_segundo = total / tiempo_total if tiempo_total > 0 else 0
    
    print("\n✅ IMPORTACIÓN COMPLETADA")
    print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
    print(f"📊 Velocidad: {registros_por_segundo:.2f} registros/segundo")
    print(f"📝 Calificaciones creadas: {creados:,}")
    print(f"❌ Errores: {errores:,}")
    
    return True

if __name__ == '__main__':
    # Ofrecer opciones al usuario para ejecutar el script
    print("🎓 IMPORTADOR ULTRA RÁPIDO - CALIFICACIONES 2023")
    print("⚡ Versión optimizada para máximo rendimiento")
    print("🔧 Adaptado para evaluaciones entregables trimestres 7, 8, 9")
    print()
    
    # Diagnosticar estructura primero
    if not diagnosticar_estructura_base_datos_2023():
        print("\n❌ Los requisitos no están cumplidos para 2023. Por favor verifica la estructura.")
        sys.exit(1)
    
    # Analizar datos del CSV
    if not analizar_datos_csv_2023():
        print("\n⚠️ Hay problemas en el análisis del CSV. ¿Desea continuar?")
        continuar = input("¿Continuar a pesar de los problemas? (s/n): ").lower() == 's'
        if not continuar:
            sys.exit(1)
    
    # Verificar estado actual
    verificar_estado_actual_2023()
    
    print("\n" + "=" * 60)
    print("🚀 OPCIONES DE IMPORTACIÓN:")
    print("1. 🏃‍♂️ Importación ULTRA RÁPIDA (recomendado)")
    print("2. 📊 Solo verificar datos (sin importar)")
    print("0. ❌ Cancelar")
    
    opcion = input("\nSeleccione una opción (1/2/0): ")
    
    if opcion == '1':
        confirmacion = input("¿Confirma ejecutar importación ULTRA RÁPIDA para 2023? (s/n): ")
        if confirmacion.lower() == 's':
            exito = importar_calificaciones_2023_ULTRA_RAPIDO()
            if exito:
                print("\n🎉 Importación 2023 completada con éxito!")
            else:
                print("\n💥 La importación 2023 falló")
        else:
            print("\n❌ Importación cancelada por el usuario")
    elif opcion == '2':
        print("\n📊 Verificación completada. No se realizaron cambios en la base de datos.")
    else:
        print("\n❌ Operación cancelada")