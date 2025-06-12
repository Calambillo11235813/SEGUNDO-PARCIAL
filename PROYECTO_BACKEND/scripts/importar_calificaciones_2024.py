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
from Cursos.models import Materia, Trimestre, TipoEvaluacion, EvaluacionEntregable, Calificacion
from Usuarios.models import Usuario

def importar_calificaciones_2024_ULTRA_RAPIDO():
    """Versión ULTRA RÁPIDA para calificaciones 2024 - Optimizada para máximo rendimiento"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - CALIFICACIONES 2024")
    print("📚 Basado en optimizaciones exitosas de scripts anteriores")
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo no encontrado: {csv_path}")
        return False
    
    # Contadores
    total = 0
    creados = 0
    actualizados = 0
    errores = 0
    
    # Pre-cargar ContentType
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    print(f"🔧 ContentType ID: {entregable_ct.id}")
    
    # Cache para optimización ultra rápida
    estudiantes_cache = {}
    materias_cache = {}
    evaluaciones_cache = {}
    
    print("📊 Pre-cargando datos en cache...")
    
    # Pre-cargar estudiantes con select_related optimizado
    for usuario in Usuario.objects.filter(rol_id=2).only('id', 'codigo', 'nombre', 'apellido'):
        estudiantes_cache[str(usuario.codigo)] = usuario
    
    # Pre-cargar materias
    for materia in Materia.objects.all().only('id', 'nombre', 'curso_id'):
        materia_key = f"{materia.nombre}_{materia.curso_id}"
        materias_cache[materia_key] = materia
    
    # Pre-cargar evaluaciones entregables 2024 (trimestres 10, 11, 12)
    for evaluacion in EvaluacionEntregable.objects.filter(
        trimestre_id__in=[10, 11, 12]
    ).select_related('materia').only('id', 'titulo', 'trimestre_id', 'tipo_evaluacion_id', 'materia__id', 'materia__nombre'):
        eval_key = f"{evaluacion.titulo}_{evaluacion.trimestre_id}_{evaluacion.tipo_evaluacion_id}_{evaluacion.materia.id}"
        evaluaciones_cache[eval_key] = evaluacion
    
    print(f"✅ Cache cargado:")
    print(f"   👥 {len(estudiantes_cache)} estudiantes")
    print(f"   📚 {len(materias_cache)} materias")  
    print(f"   📝 {len(evaluaciones_cache)} evaluaciones")
    
    # Leer CSV de forma ultra eficiente
    print("📖 Leyendo CSV...")
    try:
        # Leer solo las columnas estrictamente necesarias
        columnas_necesarias = [
            'estudiante_codigo', 'materia', 'curso_id', 'titulo_evaluacion',
            'tipo_evaluacion_id', 'trimestre_id', 'nota', 'fecha_calificacion',
            'entrega_tardia', 'penalizacion_aplicada', 'finalizada'
        ]
        
        df = pd.read_csv(csv_path, usecols=columnas_necesarias, dtype={
            'estudiante_codigo': 'str',
            'curso_id': 'int32',
            'tipo_evaluacion_id': 'int32', 
            'trimestre_id': 'int32',
            'nota': 'float64',
            'entrega_tardia': 'bool',
            'penalizacion_aplicada': 'float64',
            'finalizada': 'bool'
        })
        
        total = len(df)
        print(f"✅ {total:,} registros leídos")
        
        # Filtrar solo trimestres 2024 en caso de que el CSV tenga datos mixtos
        df_2024 = df[df['trimestre_id'].isin([10, 11, 12])]
        if len(df_2024) != total:
            print(f"📊 Filtrado a registros 2024: {len(df_2024):,} de {total:,}")
            df = df_2024
            total = len(df)
        
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return False
    
    # Procesamiento ultra rápido con bulk operations
    print("⚡ Procesando en modo ultra rápido...")
    
    calificaciones_para_crear = []
    calificaciones_para_actualizar = []
    lote_size = 3000  # Lotes más grandes para calificaciones (más campos)
    
    with transaction.atomic():
        for index, row in df.iterrows():
            total_procesado = index + 1
            
            try:
                # Mostrar progreso cada 10000 registros (menos frecuente para mayor velocidad)
                if total_procesado % 10000 == 0:
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
                
                # Buscar evaluación en cache con clave más específica
                eval_key = f"{row['titulo_evaluacion']}_{row['trimestre_id']}_{row['tipo_evaluacion_id']}_{materia.id}"
                evaluacion = evaluaciones_cache.get(eval_key)
                if not evaluacion:
                    errores += 1
                    continue
                
                # Convertir fecha de forma eficiente
                try:
                    fecha_naive = datetime.strptime(row['fecha_calificacion'], '%Y-%m-%d %H:%M:%S')
                    fecha_calificacion = timezone.make_aware(fecha_naive)
                except:
                    fecha_calificacion = timezone.now()
                
                # ✅ Preparar datos para el modelo (sin nota_final)
                defaults = {
                    'nota': Decimal(str(row['nota'])),
                    'fecha_entrega': fecha_calificacion,
                    'entrega_tardia': bool(row['entrega_tardia']),
                    'penalizacion_aplicada': Decimal(str(row['penalizacion_aplicada'])),
                    'finalizada': bool(row['finalizada']),
                    'fecha_calificacion': fecha_calificacion,
                    'observaciones': f"Importado CSV 2024 - {row['titulo_evaluacion']}",
                    'retroalimentacion': None,
                    'calificado_por': None
                }
                
                # Verificar existencia de forma más eficiente
                calificacion_existente = Calificacion.objects.filter(
                    content_type=entregable_ct,
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
                        content_type=entregable_ct,
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
                        ['nota', 'fecha_entrega', 'entrega_tardia', 'penalizacion_aplicada', 
                         'finalizada', 'fecha_calificacion', 'observaciones']
                    )
                    calificaciones_para_actualizar = []
                
            except Exception as e:
                errores += 1
                if errores <= 3:  # Menos mensajes de error para mayor velocidad
                    print(f"❌ Error fila {total_procesado}: {str(e)}")
        
        # Procesar lotes finales
        if calificaciones_para_crear:
            Calificacion.objects.bulk_create(calificaciones_para_crear, ignore_conflicts=True)
        
        if calificaciones_para_actualizar:
            Calificacion.objects.bulk_update(
                calificaciones_para_actualizar,
                ['nota', 'fecha_entrega', 'entrega_tardia', 'penalizacion_aplicada', 
                 'finalizada', 'fecha_calificacion', 'observaciones']
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
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        
        # Contar calificaciones por trimestre 2024
        print("🔍 Contando calificaciones por trimestre 2024...")
        
        for trimestre_id in [10, 11, 12]:
            # Obtener IDs de evaluaciones del trimestre específico
            evaluaciones_ids = list(
                EvaluacionEntregable.objects.filter(trimestre_id=trimestre_id)
                .values_list('id', flat=True)
            )
            
            # Contar calificaciones que referencian esas evaluaciones
            count = Calificacion.objects.filter(
                content_type=entregable_ct,
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
            EvaluacionEntregable.objects.filter(trimestre_id__in=[10, 11, 12])
            .values_list('id', flat=True)
        )
        
        total_2024 = Calificacion.objects.filter(
            content_type=entregable_ct,
            object_id__in=todas_evaluaciones_2024_ids
        ).count()
        
        print(f"\n🎯 Total calificaciones 2024: {total_2024:,}")
        
        # Estadísticas adicionales
        print(f"\n📊 ESTADÍSTICAS ADICIONALES 2024:")
        total_calificaciones = Calificacion.objects.filter(content_type=entregable_ct).count()
        total_estudiantes_con_calificaciones = Calificacion.objects.filter(
            content_type=entregable_ct
        ).values('estudiante').distinct().count()
        
        print(f"   📈 Total calificaciones entregables: {total_calificaciones:,}")
        print(f"   👥 Estudiantes con calificaciones: {total_estudiantes_con_calificaciones}")
        
        # Verificar evaluaciones disponibles
        evaluaciones_2024 = EvaluacionEntregable.objects.filter(trimestre_id__in=[10, 11, 12]).count()
        print(f"   📝 Evaluaciones entregables 2024: {evaluaciones_2024}")
        
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
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        print(f"✅ ContentType EvaluacionEntregable: ID {entregable_ct.id}")
        
        # Verificar que existen evaluaciones 2024
        evaluaciones_count_2024 = EvaluacionEntregable.objects.filter(trimestre_id__in=[10, 11, 12]).count()
        print(f"✅ Total evaluaciones entregables 2024: {evaluaciones_count_2024}")
        
        # Verificar estudiantes
        estudiantes_count = Usuario.objects.filter(rol_id=2).count()
        print(f"✅ Total estudiantes (rol_id=2): {estudiantes_count}")
        
        # Verificar calificaciones existentes 2024
        todas_evaluaciones_2024_ids = list(
            EvaluacionEntregable.objects.filter(trimestre_id__in=[10, 11, 12])
            .values_list('id', flat=True)
        )
        
        calificaciones_count_2024 = Calificacion.objects.filter(
            content_type=entregable_ct,
            object_id__in=todas_evaluaciones_2024_ids
        ).count()
        print(f"✅ Calificaciones entregables 2024 existentes: {calificaciones_count_2024}")
        
        # Verificar archivo CSV
        csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
        if os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            print(f"✅ Archivo CSV 2024 encontrado: {file_size:,} bytes")
            
            # Leer muestra del CSV
            try:
                df_sample = pd.read_csv(csv_path, nrows=5)
                print(f"✅ Estructura CSV verificada: {len(df_sample.columns)} columnas")
                print(f"   📊 Muestra de trimestres en CSV: {sorted(df_sample['trimestre_id'].unique())}")
                print(f"   📋 Tipos de evaluación en muestra: {sorted(df_sample['tipo_evaluacion_id'].unique())}")
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
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
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
        print(f"   🎯 Tipos de evaluación: {sorted(df['tipo_evaluacion_id'].unique())}")
        
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
        
        # Distribución por tipo de evaluación
        print(f"\n🎯 DISTRIBUCIÓN POR TIPO DE EVALUACIÓN:")
        tipo_stats = df.groupby('tipo_evaluacion_id').agg({
            'estudiante_codigo': 'count',
            'nota': 'mean'
        }).round(2)
        
        for tipo_id, stats in tipo_stats.iterrows():
            print(f"   📝 Tipo {tipo_id}: {int(stats['estudiante_codigo']):,} calificaciones, promedio: {stats['nota']:.2f}")
        
        # Estadísticas de notas
        print(f"\n📊 ESTADÍSTICAS DE NOTAS 2024:")
        print(f"   📈 Nota promedio: {df['nota'].mean():.2f}")
        print(f"   📊 Nota máxima: {df['nota'].max():.2f}")
        print(f"   📊 Nota mínima: {df['nota'].min():.2f}")
        print(f"   📈 Desviación estándar: {df['nota'].std():.2f}")
        
        # Estadísticas de entregas tardías
        entregas_tardias = df['entrega_tardia'].sum()
        porcentaje_tardias = (entregas_tardias / len(df)) * 100
        print(f"   ⏰ Entregas tardías: {entregas_tardias:,} ({porcentaje_tardias:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error analizando CSV: {e}")

def importar_calificaciones_csv(actualizar_existentes=True, test_mode=False):
    """Función de compatibilidad con versión anterior"""
    print("🔄 Redirigiendo a la versión ultra rápida...")
    return importar_calificaciones_2024_ULTRA_RAPIDO()

if __name__ == '__main__':
    print("🎓 IMPORTADOR ULTRA RÁPIDO - CALIFICACIONES ENTREGABLES 2024")
    print("⚡ Versión optimizada para máximo rendimiento")
    print("🔧 Adaptado para evaluaciones entregables trimestres 10, 11, 12")
    print()
    
    # Diagnosticar estructura primero
    if not diagnosticar_estructura_base_datos_2024():
        print("\n❌ Los requisitos no están cumplidos para 2024. Verifica la estructura.")
        sys.exit(1)
    
    # Analizar datos del CSV
    analizar_datos_csv_2024()
    
    # Verificar estado actual
    verificar_estado_importacion_2024()
    
    print("\n" + "="*60)
    print("🚀 OPCIONES DE IMPORTACIÓN:")
    print("1. 🏃‍♂️ Importación ULTRA RÁPIDA (recomendado)")
    print("2. 📊 Solo verificar datos (sin importar)")
    print("0. ❌ Cancelar")
    
    opcion = input("\nSeleccione una opción (1/2/0): ").strip()
    
    if opcion == "1":
        respuesta = input("¿Confirma ejecutar importación ULTRA RÁPIDA para 2024? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            success = importar_calificaciones_2024_ULTRA_RAPIDO()
            if success:
                print("\n🎊 ¡Importación ULTRA RÁPIDA 2024 completada exitosamente!")
                verificar_estado_importacion_2024()
            else:
                print("\n💥 La importación 2024 falló")
        else:
            print("❌ Importación cancelada")
    elif opcion == "2":
        print("📊 Los datos del CSV ya fueron analizados arriba")
    else:
        print("❌ Operación cancelada")