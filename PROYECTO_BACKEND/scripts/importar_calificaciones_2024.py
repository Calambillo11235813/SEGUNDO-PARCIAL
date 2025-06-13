import os
import sys
import csv
import time
import django
from datetime import datetime
from decimal import Decimal, InvalidOperation  # <- Aquí está el cambio
from django.db.models import F, ExpressionWrapper, DecimalField
from django.utils import timezone

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

try:
    django.setup()
    import pandas as pd # type: ignore
except Exception as e:
    print(f"❌ Error inicializando Django o cargando dependencias: {e}")
    sys.exit(1)

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Materia, Trimestre, TipoEvaluacion, EvaluacionEntregable, Calificacion
from Usuarios.models import Usuario

def diagnosticar_estructura_base_datos_2024():
    """Diagnóstico para verificar la estructura necesaria para importaciones 2024"""
    print("\n🔧 DIAGNÓSTICO DE ESTRUCTURA 2024:")
    print("=" * 50)
    
    # Verificar ContentType
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        print(f"✅ ContentType EvaluacionEntregable: ID {entregable_ct.id}")
    except Exception as e:
        print(f"❌ Error obteniendo ContentType: {e}")
        return False
    
    # Verificar evaluaciones 2024
    try:
        total_evaluaciones = EvaluacionEntregable.objects.filter(
            trimestre__id__in=[10, 11, 12]
        ).count()
        print(f"✅ Total evaluaciones entregables 2024: {total_evaluaciones}")
        if total_evaluaciones == 0:
            print("❌ ¡No hay evaluaciones entregables para 2024!")
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
        calificaciones_2024 = Calificacion.objects.filter(
            content_type=entregable_ct,
            evaluacion__trimestre__id__in=[10, 11, 12]
        ).count()
        print(f"✅ Calificaciones entregables 2024 existentes: {calificaciones_2024}")
    except Exception as e:
        print(f"❌ Error contando calificaciones: {e}")
    
    # Verificar archivo CSV
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Tamaño del archivo
    csv_size = os.path.getsize(csv_path)
    print(f"✅ Archivo CSV 2024 encontrado: {csv_size:,} bytes")
    
    # Verificar estructura del CSV
    try:
        # Leer solo las primeras filas para análisis
        df_sample = pd.read_csv(csv_path, nrows=5)
        columnas = df_sample.columns.tolist()
        print(f"✅ Estructura CSV verificada: {len(columnas)} columnas")
        print(f"   📊 Muestra de trimestres en CSV: {sorted(df_sample['trimestre_id'].unique())}")
        print(f"   📋 Tipos de evaluación en muestra: {sorted(df_sample['tipo_evaluacion_id'].unique())}")
        
        # Verificar estructura de los datos de entrega_tardia y finalizada
        entrega_valores = df_sample['entrega_tardia'].unique()
        finalizada_valores = df_sample['finalizada'].unique()
        if 'SI' in entrega_valores or 'NO' in entrega_valores:
            print(f"   ⚠️ Campo entrega_tardia usa valores 'SI'/'NO'. Se convertirán durante la importación.")
        
        if 'SI' in finalizada_valores or 'NO' in finalizada_valores:
            print(f"   ⚠️ Campo finalizada usa valores 'SI'/'NO'. Se convertirán durante la importación.")
    except Exception as e:
        print(f"❌ Error verificando estructura CSV: {e}")
        return False
        
    return True

def analizar_datos_csv_2024():
    """Analiza la estructura y contenido del archivo CSV de calificaciones 2024"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    print("\n📊 ANÁLISIS DE DATOS CSV 2024:")
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
        print("\n📅 DISTRIBUCIÓN POR TRIMESTRE 2024:")
        for trimestre in sorted(df['trimestre_id'].unique()):
            trim_df = df[df['trimestre_id'] == trimestre]
            print(f"   📚 Trimestre {trimestre}: {len(trim_df):,} calificaciones, promedio: {pd.to_numeric(trim_df['nota']).mean():.2f}")
        
        # Análisis por tipo de evaluación
        print("\n🎯 DISTRIBUCIÓN POR TIPO DE EVALUACIÓN:")
        for tipo in sorted(df['tipo_evaluacion_id'].unique()):
            tipo_df = df[df['tipo_evaluacion_id'] == tipo]
            print(f"   📝 Tipo {tipo}: {len(tipo_df):,} calificaciones, promedio: {pd.to_numeric(tipo_df['nota']).mean():.2f}")
        
        # Estadísticas de notas
        print("\n📊 ESTADÍSTICAS DE NOTAS 2024:")
        df['nota_numeric'] = pd.to_numeric(df['nota'])
        print(f"   📈 Nota promedio: {df['nota_numeric'].mean():.2f}")
        print(f"   📊 Nota máxima: {df['nota_numeric'].max():.2f}")
        print(f"   📊 Nota mínima: {df['nota_numeric'].min():.2f}")
        print(f"   📈 Desviación estándar: {df['nota_numeric'].std():.2f}")
        
        # Verificar valores de entrega_tardia y finalizada
        print("\n📝 CAMPOS BOOLEANOS:")
        print(f"   ⏰ Valores de entrega_tardia: {sorted(df['entrega_tardia'].unique())}")
        print(f"   ✅ Valores de finalizada: {sorted(df['finalizada'].unique())}")
        
        return True
    except Exception as e:
        print(f"❌ Error analizando CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estado_actual_2024():
    """Verifica el estado actual de calificaciones 2024 en la BD"""
    print("\n📊 VERIFICACIÓN DEL ESTADO ACTUAL 2024:")
    print("=" * 50)
    
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        print("🔍 Contando calificaciones por trimestre 2024...")
        
        # Contar por trimestre
        for trimestre_id in [10, 11, 12]:
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
            total_2024 = Calificacion.objects.filter(
                content_type=entregable_ct,
                object_id__in=EvaluacionEntregable.objects.filter(
                    trimestre__id__in=[10, 11, 12]
                ).values_list('id', flat=True)
            ).count()
            print(f"\n🎯 Total calificaciones 2024: {total_2024:,}")
        except Exception as e:
            print(f"❌ Error contando total 2024: {e}")
        
        # Estadísticas adicionales
        try:
            print("\n📊 ESTADÍSTICAS ADICIONALES 2024:")
            calificaciones_2024 = Calificacion.objects.filter(
                content_type=entregable_ct,
                object_id__in=EvaluacionEntregable.objects.filter(
                    trimestre__id__in=[10, 11, 12]
                ).values_list('id', flat=True)
            )
            
            print(f"   📈 Total calificaciones entregables: {calificaciones_2024.count():,}")
            print(f"   👥 Estudiantes con calificaciones: {calificaciones_2024.values('estudiante').distinct().count():,}")
            print(f"   📝 Evaluaciones entregables 2024: {EvaluacionEntregable.objects.filter(trimestre__id__in=[10, 11, 12]).count():,}")
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas adicionales: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando estado actual: {e}")
        return False

def importar_calificaciones_2024_ULTRA_RAPIDO():
    """Versión corregida para importación de calificaciones 2024"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - CALIFICACIONES 2024 (VERSIÓN CORREGIDA)")
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Contadores
    total = 0
    creados = 0
    errores = 0
    
    # Pre-cargar ContentType
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    print(f"🔧 ContentType ID: {entregable_ct.id}")
    
    # Pre-cargar datos en memoria
    print("📊 Pre-cargando datos en cache...")
    estudiantes_cache = {e.codigo: e for e in Usuario.objects.filter(rol__id=2)}
    
    # Pre-cargar evaluaciones 2024 con mejor clave
    evaluaciones_cache = {}
    for eval in EvaluacionEntregable.objects.filter(trimestre__id__in=[10, 11, 12]):
        # Normalizar clave
        clave = f"{eval.materia.nombre.strip().upper()}_{eval.titulo.strip().upper()}_{eval.trimestre.id}_{eval.tipo_evaluacion.id}"
        evaluaciones_cache[clave] = eval
        
        # También mantener una referencia por ID de material y tipo
        alt_clave = f"{eval.materia.id}_{eval.titulo.strip().upper()}_{eval.trimestre.id}_{eval.tipo_evaluacion.id}"
        evaluaciones_cache[alt_clave] = eval

    print(f"✅ Cache cargado:")
    print(f"   👥 {len(estudiantes_cache)} estudiantes")
    print(f"   📝 {len(evaluaciones_cache)} evaluaciones")
    
    try:
        calificaciones_a_crear = []
        errores_list = []
        total_rows = 0
        batch_size = 1000  # Reducir tamaño de lote
        
        print("📖 Procesando CSV...")
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                total_rows += 1
                
                try:
                    # Buscar estudiante
                    estudiante = estudiantes_cache.get(row['estudiante_codigo'])
                    if not estudiante:
                        errores_list.append(f"Fila {total_rows}: Estudiante no encontrado: {row['estudiante_codigo']}")
                        continue
                    
                    # Buscar evaluación con clave mejorada
                    clave_evaluacion = f"{row['materia'].strip().upper()}_{row['titulo_evaluacion'].strip().upper()}_{row['trimestre_id']}_{row['tipo_evaluacion_id']}"
                    evaluacion = evaluaciones_cache.get(clave_evaluacion)
                    
                    if not evaluacion:
                        errores_list.append(f"Fila {total_rows}: Evaluación no encontrada: {clave_evaluacion}")
                        continue
                    
                    # Convertir valores booleanos
                    entrega_tardia = str(row['entrega_tardia']).upper() == 'SI'
                    finalizada = str(row['finalizada']).upper() == 'SI'
                    
                    # Convertir valores numéricos con validación
                    try:
                        nota = Decimal(str(row['nota']).replace(',', '.'))
                        penalizacion = Decimal(str(row['penalizacion_aplicada']).replace(',', '.'))
                        
                        # Validar rangos
                        if nota < 0 or nota > 100:
                            errores_list.append(f"Fila {total_rows}: Nota fuera de rango: {nota}")
                            continue
                            
                        if penalizacion < 0 or penalizacion > 100:
                            errores_list.append(f"Fila {total_rows}: Penalización fuera de rango: {penalizacion}")
                            continue
                            
                    except (ValueError, TypeError, InvalidOperation) as e:
                        errores_list.append(f"Fila {total_rows}: Error convirtiendo números: {str(e)}")
                        continue
                    
                    # Convertir fecha
                    fecha_calificacion = None
                    if row.get('fecha_calificacion'):
                        try:
                            fecha_calificacion = timezone.make_aware(
                                datetime.strptime(row['fecha_calificacion'], "%Y-%m-%d %H:%M:%S")
                            )
                        except ValueError:
                            try:
                                fecha_calificacion = timezone.make_aware(
                                    datetime.strptime(row['fecha_calificacion'], "%Y-%m-%d")
                                )
                            except ValueError:
                                errores_list.append(f"Fila {total_rows}: Formato de fecha inválido: {row['fecha_calificacion']}")
                    
                    # Crear objeto Calificacion
                    calificacion = Calificacion(
                        content_type=entregable_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        nota=nota,
                        entrega_tardia=entrega_tardia,
                        penalizacion_aplicada=penalizacion,
                        finalizada=finalizada,
                        fecha_calificacion=fecha_calificacion
                    )
                    
                    calificaciones_a_crear.append(calificacion)
                    
                    # Procesar en lotes
                    if len(calificaciones_a_crear) >= batch_size:
                        print(f"💾 Guardando lote de {len(calificaciones_a_crear)} calificaciones...")
                        
                        with transaction.atomic():
                            Calificacion.objects.bulk_create(
                                calificaciones_a_crear, 
                                batch_size=500,
                                ignore_conflicts=True  # Evitar duplicados
                            )
                        
                        creados += len(calificaciones_a_crear)
                        calificaciones_a_crear = []
                        
                        print(f"✅ Procesadas {total_rows:,} filas, creadas {creados:,} calificaciones")
                
                except Exception as e:
                    errores += 1
                    errores_list.append(f"Fila {total_rows}: Error general: {str(e)}")
                    if errores <= 5:
                        print(f"❌ Error en fila {total_rows}: {str(e)}")
        
        # Guardar último lote
        if calificaciones_a_crear:
            print(f"💾 Guardando último lote de {len(calificaciones_a_crear)} calificaciones...")
            with transaction.atomic():
                Calificacion.objects.bulk_create(
                    calificaciones_a_crear, 
                    batch_size=500,
                    ignore_conflicts=True
                )
            creados += len(calificaciones_a_crear)
        
        # Verificar resultado final
        total_en_bd = Calificacion.objects.filter(
            content_type=entregable_ct,
            object_id__in=EvaluacionEntregable.objects.filter(
                trimestre__id__in=[10, 11, 12]
            ).values_list('id', flat=True)
        ).count()
        
        fin = time.time()
        tiempo_total = fin - inicio
        
        print("\n" + "="*60)
        print("✅ IMPORTACIÓN COMPLETADA")
        print("="*60)
        print(f"📊 Filas procesadas: {total_rows:,}")
        print(f"✅ Calificaciones creadas: {creados:,}")
        print(f"🔍 Total en BD (verificación): {total_en_bd:,}")
        print(f"❌ Errores: {len(errores_list):,}")
        print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
        if tiempo_total > 0:
            print(f"🚀 Velocidad: {total_rows/tiempo_total:.2f} registros/segundo")
        
        if errores_list:
            print(f"\n⚠️ PRIMEROS 10 ERRORES:")
            for i, error in enumerate(errores_list[:10]):
                print(f"   {i+1}. {error}")
            if len(errores_list) > 10:
                print(f"   ... y {len(errores_list)-10} errores más")
        
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🎓 IMPORTADOR ULTRA RÁPIDO - CALIFICACIONES ENTREGABLES 2024")
    print("⚡ Versión optimizada para máximo rendimiento")
    print("🔧 Adaptado para evaluaciones entregables trimestres 10, 11, 12")
    print()
    
    # Diagnosticar estructura primero
    if not diagnosticar_estructura_base_datos_2024():
        print("\n❌ Los requisitos no están cumplidos para 2024. Por favor verifica la estructura.")
        sys.exit(1)
    
    # Analizar datos del CSV
    if not analizar_datos_csv_2024():
        print("\n⚠️ Hay problemas en el análisis del CSV. ¿Desea continuar?")
        continuar = input("¿Continuar a pesar de los problemas? (s/n): ").lower() == 's'
        if not continuar:
            sys.exit(1)
    
    # Verificar estado actual
    verificar_estado_actual_2024()
    
    print("\n" + "=" * 60)
    print("🚀 OPCIONES DE IMPORTACIÓN:")
    print("1. 🏃‍♂️ Importación ULTRA RÁPIDA (recomendado)")
    print("2. 📊 Solo verificar datos (sin importar)")
    print("0. ❌ Cancelar")
    
    opcion = input("\nSeleccione una opción (1/2/0): ")
    
    if opcion == '1':
        confirmacion = input("¿Confirma ejecutar importación ULTRA RÁPIDA para 2024? (s/n): ")
        if confirmacion.lower() == 's':
            exito = importar_calificaciones_2024_ULTRA_RAPIDO()
            if exito:
                print("\n🎉 Importación 2024 completada con éxito!")
            else:
                print("\n💥 La importación 2024 falló")
        else:
            print("\n❌ Importación cancelada por el usuario")
    elif opcion == '2':
        print("\n📊 Verificación completada. No se realizaron cambios en la base de datos.")
    else:
        print("\n❌ Operación cancelada")