import os
import django
import sys
import pandas as pd
import time
from datetime import datetime
from decimal import Decimal
from django.utils import timezone

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

django.setup()

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Materia, Trimestre, TipoEvaluacion, EvaluacionParticipacion, Calificacion
from Usuarios.models import Usuario

def importar_calificaciones_participaciones_2024_ULTRA_RAPIDO():
    """Versión ULTRA RÁPIDA para 2024 basada en el script 2023 exitoso"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_participaciones_2024.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - CALIFICACIONES PARTICIPACIONES 2024")
    print("📚 Basado en el script 2023 exitoso - Máximo rendimiento garantizado")
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo no encontrado: {csv_path}")
        return False
    
    # Contadores
    total = 0
    creados = 0
    actualizados = 0
    errores = 0
    
    # Pre-cargar ContentType
    participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
    print(f"🔧 ContentType ID: {participacion_ct.id}")
    
    # Cache para optimización
    estudiantes_cache = {}
    materias_cache = {}
    evaluaciones_cache = {}
    
    print("📊 Pre-cargando datos en cache...")
    
    # Pre-cargar estudiantes
    for usuario in Usuario.objects.filter(rol_id=2):
        estudiantes_cache[str(usuario.codigo)] = usuario
    
    # Pre-cargar materias
    for materia in Materia.objects.all():
        materia_key = f"{materia.nombre}_{materia.curso_id}"
        materias_cache[materia_key] = materia
    
    # Pre-cargar evaluaciones de participación 2024 (trimestres 10, 11, 12)
    for evaluacion in EvaluacionParticipacion.objects.filter(trimestre_id__in=[10, 11, 12]):
        eval_key = f"{evaluacion.titulo}_{evaluacion.trimestre_id}_{evaluacion.materia.id}"
        evaluaciones_cache[eval_key] = evaluacion
    
    print(f"✅ Cache cargado:")
    print(f"   👥 {len(estudiantes_cache)} estudiantes")
    print(f"   📚 {len(materias_cache)} materias")  
    print(f"   📝 {len(evaluaciones_cache)} evaluaciones")
    
    # Leer CSV de forma eficiente
    print("📖 Leyendo CSV...")
    try:
        # Leer solo las columnas necesarias
        columnas_necesarias = [
            'estudiante_codigo', 'materia', 'curso_id', 'titulo_evaluacion',
            'tipo_evaluacion_id', 'trimestre_id', 'nota', 'fecha_calificacion', 'finalizada'
        ]
        
        df = pd.read_csv(csv_path, usecols=columnas_necesarias, dtype={
            'estudiante_codigo': 'str',
            'curso_id': 'int32',
            'tipo_evaluacion_id': 'int32', 
            'trimestre_id': 'int32',
            'nota': 'float64',
            'finalizada': 'bool'
        })
        
        total = len(df)
        print(f"✅ {total:,} registros leídos")
        
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return False
    
    # Procesamiento ultra rápido con bulk operations
    print("⚡ Procesando en modo ultra rápido...")
    
    calificaciones_para_crear = []
    calificaciones_para_actualizar = []
    lote_size = 2000  # Lotes más grandes para mayor velocidad
    
    with transaction.atomic():
        for index, row in df.iterrows():
            total_procesado = index + 1
            
            try:
                # Mostrar progreso cada 5000 registros
                if total_procesado % 5000 == 0:
                    tiempo_transcurrido = time.time() - inicio
                    velocidad = total_procesado / tiempo_transcurrido
                    print(f"⚡ {total_procesado:,}/{total:,} | {velocidad:,.0f} reg/seg | {tiempo_transcurrido:.1f}s")
                
                # Buscar estudiante en cache
                codigo_estudiante = str(row['estudiante_codigo'])
                estudiante = estudiantes_cache.get(codigo_estudiante)
                if not estudiante:
                    errores += 1
                    continue
                
                # Buscar materia en cache
                materia_key = f"{row['materia']}_{row['curso_id']}"
                materia = materias_cache.get(materia_key)
                if not materia:
                    errores += 1
                    continue
                
                # Buscar evaluación en cache
                eval_key = f"{row['titulo_evaluacion']}_{row['trimestre_id']}_{materia.id}"
                evaluacion = evaluaciones_cache.get(eval_key)
                if not evaluacion:
                    errores += 1
                    continue
                
                # Convertir fecha
                try:
                    fecha_naive = datetime.strptime(row['fecha_calificacion'], '%Y-%m-%d %H:%M:%S')
                    fecha_calificacion = timezone.make_aware(fecha_naive)
                except:
                    fecha_calificacion = timezone.now()
                
                # ✅ SOLUCIÓN CLAVE: Solo usar campos reales del modelo (sin nota_final)
                defaults = {
                    'nota': Decimal(str(row['nota'])),
                    'fecha_entrega': fecha_calificacion,
                    'entrega_tardia': False,
                    'penalizacion_aplicada': Decimal('0.0'),
                    'finalizada': bool(row['finalizada']),
                    'fecha_calificacion': fecha_calificacion,
                    'observaciones': f"Importado CSV 2024 - {row['titulo_evaluacion']}",
                    'retroalimentacion': None,
                    'calificado_por': None
                }
                
                # Verificar si existe para decidir crear o actualizar
                calificacion_existente = Calificacion.objects.filter(
                    content_type=participacion_ct,
                    object_id=evaluacion.id,
                    estudiante=estudiante
                ).first()
                
                if calificacion_existente:
                    # Actualizar existente
                    for campo, valor in defaults.items():
                        setattr(calificacion_existente, campo, valor)
                    calificaciones_para_actualizar.append(calificacion_existente)
                    actualizados += 1
                else:
                    # Crear nueva
                    nueva_calificacion = Calificacion(
                        content_type=participacion_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        **defaults
                    )
                    calificaciones_para_crear.append(nueva_calificacion)
                    creados += 1
                
                # Procesar lotes para máximo rendimiento
                if len(calificaciones_para_crear) >= lote_size:
                    Calificacion.objects.bulk_create(calificaciones_para_crear, ignore_conflicts=True)
                    calificaciones_para_crear = []
                
                if len(calificaciones_para_actualizar) >= lote_size:
                    Calificacion.objects.bulk_update(
                        calificaciones_para_actualizar,
                        ['nota', 'fecha_entrega', 'finalizada', 'fecha_calificacion', 'observaciones']
                    )
                    calificaciones_para_actualizar = []
                
            except Exception as e:
                errores += 1
                if errores <= 5:
                    print(f"❌ Error fila {total_procesado}: {str(e)}")
        
        # Procesar lotes finales
        if calificaciones_para_crear:
            Calificacion.objects.bulk_create(calificaciones_para_crear, ignore_conflicts=True)
        
        if calificaciones_para_actualizar:
            Calificacion.objects.bulk_update(
                calificaciones_para_actualizar,
                ['nota', 'fecha_entrega', 'finalizada', 'fecha_calificacion', 'observaciones']
            )
    
    tiempo_total = time.time() - inicio
    velocidad = total / tiempo_total if tiempo_total > 0 else 0
    
    print(f"\n🎉 IMPORTACIÓN ULTRA RÁPIDA COMPLETADA:")
    print(f"   📊 Total procesados: {total:,} registros")
    print(f"   ✅ Creados: {creados:,}")
    print(f"   ↻ Actualizados: {actualizados:,}")
    print(f"   ❌ Errores: {errores:,}")
    print(f"   ⏱️ Tiempo total: {tiempo_total:.2f} segundos")
    print(f"   🚀 Velocidad: {velocidad:,.0f} registros/segundo")
    print(f"   📈 Tasa éxito: {((creados + actualizados)/total)*100:.1f}%")
    
    return True

def verificar_estado_importacion_2024():
    """Verifica el estado actual de las calificaciones 2024"""
    print("\n📊 VERIFICACIÓN DEL ESTADO ACTUAL 2024:")
    print("=" * 50)
    
    try:
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Contar calificaciones por trimestre 2024
        print("🔍 Contando calificaciones por trimestre 2024...")
        
        for trimestre_id in [10, 11, 12]:
            # Obtener IDs de evaluaciones del trimestre específico
            evaluaciones_ids = list(
                EvaluacionParticipacion.objects.filter(trimestre_id=trimestre_id)
                .values_list('id', flat=True)
            )
            
            # Contar calificaciones que referencian esas evaluaciones
            count = Calificacion.objects.filter(
                content_type=participacion_ct,
                object_id__in=evaluaciones_ids
            ).count()
            
            trimestre_nombre = {
                10: "Primer Trimestre 2024",
                11: "Segundo Trimestre 2024", 
                12: "Tercer Trimestre 2024"
            }[trimestre_id]
            
            print(f"   📚 {trimestre_nombre}: {count:,} calificaciones")
        
        # Total 2024
        todas_evaluaciones_2024_ids = list(
            EvaluacionParticipacion.objects.filter(trimestre_id__in=[10, 11, 12])
            .values_list('id', flat=True)
        )
        
        total_2024 = Calificacion.objects.filter(
            content_type=participacion_ct,
            object_id__in=todas_evaluaciones_2024_ids
        ).count()
        
        print(f"\n🎯 Total calificaciones 2024: {total_2024:,}")
        
        # Estadísticas adicionales
        print(f"\n📊 ESTADÍSTICAS ADICIONALES 2024:")
        total_calificaciones = Calificacion.objects.filter(content_type=participacion_ct).count()
        total_estudiantes_con_calificaciones = Calificacion.objects.filter(
            content_type=participacion_ct
        ).values('estudiante').distinct().count()
        
        print(f"   📈 Total calificaciones de participación: {total_calificaciones:,}")
        print(f"   👥 Estudiantes con calificaciones: {total_estudiantes_con_calificaciones}")
        
        # Verificar evaluaciones disponibles
        evaluaciones_2024 = EvaluacionParticipacion.objects.filter(trimestre_id__in=[10, 11, 12]).count()
        print(f"   📝 Evaluaciones de participación 2024: {evaluaciones_2024}")
        
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        import traceback
        print(f"   🔍 Detalle del error: {traceback.format_exc()}")

def diagnosticar_estructura_base_datos_2024():
    """Función para diagnosticar la estructura de la BD para 2024"""
    print("\n🔧 DIAGNÓSTICO DE ESTRUCTURA 2024:")
    print("=" * 50)
    
    try:
        # Verificar ContentTypes
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        print(f"✅ ContentType EvaluacionParticipacion: ID {participacion_ct.id}")
        
        # Verificar que existen evaluaciones 2024
        evaluaciones_count_2024 = EvaluacionParticipacion.objects.filter(trimestre_id__in=[10, 11, 12]).count()
        print(f"✅ Total evaluaciones de participación 2024: {evaluaciones_count_2024}")
        
        # Verificar estudiantes
        estudiantes_count = Usuario.objects.filter(rol_id=2).count()
        print(f"✅ Total estudiantes (rol_id=2): {estudiantes_count}")
        
        # Verificar calificaciones existentes 2024
        todas_evaluaciones_2024_ids = list(
            EvaluacionParticipacion.objects.filter(trimestre_id__in=[10, 11, 12])
            .values_list('id', flat=True)
        )
        
        calificaciones_count_2024 = Calificacion.objects.filter(
            content_type=participacion_ct,
            object_id__in=todas_evaluaciones_2024_ids
        ).count()
        print(f"✅ Calificaciones de participación 2024 existentes: {calificaciones_count_2024}")
        
        # Verificar archivo CSV
        csv_path = os.path.join(project_root, 'csv', 'calificaciones_participaciones_2024.csv')
        if os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            print(f"✅ Archivo CSV 2024 encontrado: {file_size:,} bytes")
            
            # Leer muestra del CSV
            try:
                df_sample = pd.read_csv(csv_path, nrows=5)
                print(f"✅ Estructura CSV verificada: {len(df_sample.columns)} columnas")
                print(f"   📊 Muestra de trimestres en CSV: {sorted(df_sample['trimestre_id'].unique())}")
            except Exception as e:
                print(f"⚠️ Error leyendo muestra del CSV: {e}")
        else:
            print(f"❌ Archivo CSV 2024 no encontrado: {csv_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return False

def analizar_datos_csv_2024():
    """Analiza los datos del CSV 2024 antes de importar"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_participaciones_2024.csv')
    
    if not os.path.exists(csv_path):
        print("❌ Archivo CSV 2024 no encontrado")
        return
    
    print("\n📊 ANÁLISIS DE DATOS CSV 2024:")
    print("=" * 50)
    
    try:
        df = pd.read_csv(csv_path)
        
        print(f"📈 ESTADÍSTICAS GENERALES:")
        print(f"   📊 Total registros: {len(df):,}")
        print(f"   👥 Estudiantes únicos: {df['estudiante_codigo'].nunique():,}")
        print(f"   📚 Materias únicas: {df['materia'].nunique()}")
        print(f"   📝 Evaluaciones únicas: {df['titulo_evaluacion'].nunique()}")
        
        # Distribución por trimestre
        print(f"\n📅 DISTRIBUCIÓN POR TRIMESTRE 2024:")
        trimestre_stats = df.groupby('trimestre_id').agg({
            'estudiante_codigo': 'count',
            'nota': 'mean'
        }).round(2)
        
        for trimestre_id, stats in trimestre_stats.iterrows():
            trimestre_nombre = {
                10: "Primer Trimestre 2024", 
                11: "Segundo Trimestre 2024", 
                12: "Tercer Trimestre 2024"
            }.get(trimestre_id, f"Trimestre {trimestre_id}")
            
            print(f"   📚 {trimestre_nombre}: {int(stats['estudiante_codigo']):,} calificaciones, promedio: {stats['nota']:.2f}")
        
        # Estadísticas de notas
        print(f"\n📊 ESTADÍSTICAS DE NOTAS 2024:")
        print(f"   📈 Nota promedio: {df['nota'].mean():.2f}")
        print(f"   📊 Nota máxima: {df['nota'].max():.2f}")
        print(f"   📊 Nota mínima: {df['nota'].min():.2f}")
        print(f"   📈 Desviación estándar: {df['nota'].std():.2f}")
        
    except Exception as e:
        print(f"❌ Error analizando CSV: {e}")

if __name__ == '__main__':
    print("🎓 IMPORTADOR ULTRA RÁPIDO - CALIFICACIONES PARTICIPACIONES 2024")
    print("⚡ Versión optimizada basada en el script 2023 exitoso")
    print("🔧 Adaptado para trimestres 10, 11, 12 (año 2024)")
    print()
    
    # Diagnosticar estructura primero
    if not diagnosticar_estructura_base_datos_2024():
        print("\n❌ Los requisitos no están cumplidos para 2024. Verifica la estructura.")
        sys.exit(1)
    
    # Analizar datos del CSV
    analizar_datos_csv_2024()
    
    # Verificar estado actual
    verificar_estado_importacion_2024()
    
    respuesta = input("\n¿Ejecutar importación ULTRA RÁPIDA para 2024? (s/n): ").lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        success = importar_calificaciones_participaciones_2024_ULTRA_RAPIDO()
        if success:
            print("\n🎊 ¡Importación ULTRA RÁPIDA 2024 completada exitosamente!")
            verificar_estado_importacion_2024()
        else:
            print("\n💥 La importación 2024 falló")
    else:
        print("❌ Importación cancelada")