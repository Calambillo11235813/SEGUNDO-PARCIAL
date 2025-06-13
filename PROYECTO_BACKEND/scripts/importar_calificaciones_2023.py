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
from Cursos.models import Calificacion, EvaluacionEntregable, EvaluacionParticipacion, Materia, Trimestre, TipoEvaluacion
from Usuarios.models import Usuario

def diagnosticar_estructura_base_datos_2023():
    """Diagnóstico para verificar la estructura necesaria para importaciones 2023"""
    print("\n🔧 DIAGNÓSTICO DE ESTRUCTURA 2023:")
    print("=" * 50)
    
    # Verificar ContentTypes
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        print(f"✅ ContentType EvaluacionEntregable: ID {entregable_ct.id}")
        print(f"✅ ContentType EvaluacionParticipacion: ID {participacion_ct.id}")
    except Exception as e:
        print(f"❌ Error obteniendo ContentTypes: {e}")
        return False
    
    # Verificar evaluaciones 2023
    try:
        total_entregables = EvaluacionEntregable.objects.filter(
            trimestre__id__in=[7, 8, 9]
        ).count()
        total_participacion = EvaluacionParticipacion.objects.filter(
            trimestre__id__in=[7, 8, 9]
        ).count()
        print(f"✅ Total evaluaciones entregables 2023: {total_entregables}")
        print(f"✅ Total evaluaciones participación 2023: {total_participacion}")
        
        # Mostrar algunas evaluaciones de ejemplo
        if total_entregables > 0:
            print("📝 Ejemplos de evaluaciones entregables 2023:")
            for eval in EvaluacionEntregable.objects.filter(trimestre__id__in=[7, 8, 9])[:3]:
                print(f"   - ID {eval.id}: {eval.titulo} (Materia: {eval.materia.nombre}, Trimestre: {eval.trimestre.id})")
        
        if total_participacion > 0:
            print("🗣️ Ejemplos de evaluaciones participación 2023:")
            for eval in EvaluacionParticipacion.objects.filter(trimestre__id__in=[7, 8, 9])[:3]:
                print(f"   - ID {eval.id}: {eval.titulo} (Materia: {eval.materia.nombre}, Trimestre: {eval.trimestre.id})")
        
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
    
    # Verificar archivo CSV
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Tamaño del archivo
    csv_size = os.path.getsize(csv_path)
    print(f"✅ Archivo CSV 2023 encontrado: {csv_size:,} bytes")
    
    return True

def analizar_estructura_csv_2023():
    """Analiza la estructura exacta del CSV de calificaciones 2023"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    print("\n📊 ANÁLISIS ESTRUCTURA CSV 2023:")
    print("=" * 50)
    
    try:
        # Leer solo las primeras filas para análisis
        df_sample = pd.read_csv(csv_path, nrows=10)
        
        print("📋 COLUMNAS ENCONTRADAS:")
        for i, col in enumerate(df_sample.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n📊 Total columnas: {len(df_sample.columns)}")
        
        # Verificar campos críticos de la nueva estructura (SIN calificado_por_codigo)
        campos_esperados = [
            'estudiante_codigo', 'nota', 'fecha_entrega', 'entrega_tardia', 
            'penalizacion_aplicada', 'observaciones', 'retroalimentacion', 
            'finalizada', 'fecha_calificacion',  # Removido calificado_por_codigo
            'materia', 'curso_id', 'titulo_evaluacion', 'tipo_evaluacion_id', 'trimestre_id'
        ]
        
        print("\n🔍 VERIFICACIÓN DE CAMPOS ESPERADOS:")
        campos_faltantes = []
        for campo in campos_esperados:
            if campo in df_sample.columns:
                print(f"   ✅ {campo}")
            else:
                print(f"   ❌ {campo} - FALTANTE")
                campos_faltantes.append(campo)
        
        # Campos opcionales que se ignorarán
        campos_ignorados = ['calificado_por_codigo']
        print("\n🚫 CAMPOS QUE SE IGNORARÁN:")
        for campo in campos_ignorados:
            if campo in df_sample.columns:
                print(f"   ⏭️ {campo} - SERÁ IGNORADO (sin profesores asignados)")
        
        # Verificar valores únicos en campos importantes
        print("\n📈 VALORES ÚNICOS:")
        if 'trimestre_id' in df_sample.columns:
            print(f"   📚 Trimestres: {sorted(df_sample['trimestre_id'].unique())}")
        if 'tipo_evaluacion_id' in df_sample.columns:
            print(f"   🎯 Tipos evaluación: {sorted(df_sample['tipo_evaluacion_id'].unique())}")
        if 'estudiante_codigo' in df_sample.columns:
            print(f"   👥 Estudiantes (muestra): {len(df_sample['estudiante_codigo'].unique())}")
        if 'materia' in df_sample.columns:
            print(f"   📖 Materias: {df_sample['materia'].unique()}")
        
        # Verificar formato de valores booleanos
        print("\n🔗 FORMATO DE VALORES BOOLEANOS:")
        if 'entrega_tardia' in df_sample.columns:
            print(f"   entrega_tardia: {df_sample['entrega_tardia'].unique()}")
        if 'finalizada' in df_sample.columns:
            print(f"   finalizada: {df_sample['finalizada'].unique()}")
        
        return len(campos_faltantes) == 0
        
    except Exception as e:
        print(f"❌ Error analizando estructura CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estado_actual_2023():
    """Verifica el estado actual de calificaciones 2023 en la BD"""
    print("\n📊 VERIFICACIÓN DEL ESTADO ACTUAL 2023:")
    print("=" * 50)
    
    try:
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Contar calificaciones existentes por tipo
        for trimestre_id in [7, 8, 9]:
            try:
                # Entregables
                entregables_ids = list(EvaluacionEntregable.objects.filter(
                    trimestre__id=trimestre_id
                ).values_list('id', flat=True))
                
                count_entregables = 0
                if entregables_ids:
                    count_entregables = Calificacion.objects.filter(
                        content_type=entregable_ct,
                        object_id__in=entregables_ids
                    ).count()
                
                # Participación
                participacion_ids = list(EvaluacionParticipacion.objects.filter(
                    trimestre__id=trimestre_id
                ).values_list('id', flat=True))
                
                count_participacion = 0
                if participacion_ids:
                    count_participacion = Calificacion.objects.filter(
                        content_type=participacion_ct,
                        object_id__in=participacion_ids
                    ).count()
                
                print(f"   📚 Trimestre {trimestre_id}:")
                print(f"     📝 Entregables: {count_entregables:,}")
                print(f"     🗣️ Participación: {count_participacion:,}")
                
            except Exception as e:
                print(f"   ❌ Error trimestre {trimestre_id}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando estado actual: {e}")
        return False

def convertir_booleano_2023(valor):
    """Convierte valores booleanos específicos del CSV 2023"""
    if pd.isna(valor) or valor == '':
        return False
    
    if isinstance(valor, bool):
        return valor
    
    if isinstance(valor, str):
        valor_lower = valor.lower().strip()
        return valor_lower in ['true', '1', 'si', 'sí', 'yes', 'verdadero']
    
    if isinstance(valor, (int, float)):
        return bool(valor)
    
    return False

def buscar_o_crear_evaluacion(materia_nombre, curso_id, titulo_evaluacion, tipo_evaluacion_id, trimestre_id):
    """Busca una evaluación existente o la crea si no existe"""
    try:
        # Primero buscar la materia
        materia = Materia.objects.filter(
            nombre=materia_nombre,
            curso_id=curso_id
        ).first()
        
        if not materia:
            print(f"⚠️ Materia no encontrada: {materia_nombre} (curso {curso_id})")
            return None, None
        
        # Determinar el tipo de evaluación
        tipo_evaluacion = TipoEvaluacion.objects.filter(id=tipo_evaluacion_id).first()
        if not tipo_evaluacion:
            print(f"⚠️ Tipo de evaluación no encontrado: {tipo_evaluacion_id}")
            return None, None
        
        # Determinar trimestre
        trimestre = Trimestre.objects.filter(id=trimestre_id).first()
        if not trimestre:
            print(f"⚠️ Trimestre no encontrado: {trimestre_id}")
            return None, None
        
        # Determinar si es entregable o participación basado en el tipo
        # Asumiendo: tipo_evaluacion_id=1 es PARCIAL (entregable), tipo_evaluacion_id=2 es PRÁCTICO (entregable)
        
        if tipo_evaluacion_id in [1, 2]:  # PARCIAL y PRÁCTICO son entregables
            # Buscar evaluación entregable existente
            evaluacion = EvaluacionEntregable.objects.filter(
                materia=materia,
                titulo=titulo_evaluacion,
                trimestre=trimestre,
                tipo_evaluacion=tipo_evaluacion
            ).first()
            
            if not evaluacion:
                # Crear nueva evaluación entregable
                evaluacion = EvaluacionEntregable.objects.create(
                    titulo=titulo_evaluacion,
                    materia=materia,
                    trimestre=trimestre,
                    tipo_evaluacion=tipo_evaluacion,
                    descripcion=f"{titulo_evaluacion} - {materia.nombre}",
                    fecha_asignacion=timezone.now().date(),
                    fecha_entrega=timezone.now().date(),
                    nota_maxima=Decimal('100.0'),
                    nota_minima_aprobacion=Decimal('51.0'),
                    porcentaje_nota_final=Decimal('20.0'),
                    permite_entrega_tardia=True,
                    penalizacion_tardio=Decimal('10.0'),
                    publicado=True,
                    activo=True
                )
                print(f"✅ Creada evaluación entregable: {titulo_evaluacion} (ID: {evaluacion.id})")
            
            content_type = ContentType.objects.get_for_model(EvaluacionEntregable)
            return evaluacion, content_type
            
        else:  # Otros tipos son participación
            # Buscar evaluación participación existente
            evaluacion = EvaluacionParticipacion.objects.filter(
                materia=materia,
                titulo=titulo_evaluacion,
                trimestre=trimestre,
                tipo_evaluacion=tipo_evaluacion
            ).first()
            
            if not evaluacion:
                # Crear nueva evaluación participación
                evaluacion = EvaluacionParticipacion.objects.create(
                    titulo=titulo_evaluacion,
                    materia=materia,
                    trimestre=trimestre,
                    tipo_evaluacion=tipo_evaluacion,
                    descripcion=f"{titulo_evaluacion} - {materia.nombre}",
                    fecha=timezone.now().date(),
                    nota_maxima=Decimal('100.0'),
                    nota_minima_aprobacion=Decimal('51.0'),
                    porcentaje_nota_final=Decimal('10.0'),
                    publicado=True,
                    activo=True
                )
                print(f"✅ Creada evaluación participación: {titulo_evaluacion} (ID: {evaluacion.id})")
            
            content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
            return evaluacion, content_type
            
    except Exception as e:
        print(f"❌ Error buscando/creando evaluación: {e}")
        return None, None

def importar_calificaciones_2023_CORREGIDO():
    """Versión corregida que IGNORA completamente la columna calificado_por_codigo"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2023.csv')
    
    inicio = time.time()
    print("🚀 IMPORTACIÓN CORREGIDA - CALIFICACIONES 2023")
    print("📂 Archivo: calificaciones_2023.csv (estructura simplificada)")
    print("🚫 IGNORANDO columna 'calificado_por_codigo' (sin profesores asignados)")
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    # Contadores
    total_procesadas = 0
    creadas = 0
    errores = 0
    errores_detalle = []
    evaluaciones_creadas = 0
    duplicadas_omitidas = 0
    
    # Cache de datos
    print("📊 Pre-cargando datos en cache...")
    
    # Cache de estudiantes por código
    estudiantes_cache = {}
    for estudiante in Usuario.objects.filter(rol__id=2):
        estudiantes_cache[str(estudiante.codigo)] = estudiante
    
    # Cache de evaluaciones (se llenará dinámicamente)
    evaluaciones_cache = {}
    
    print(f"✅ Cache inicial cargado:")
    print(f"   👥 {len(estudiantes_cache)} estudiantes")
    print(f"   🚫 Campo 'calificado_por_codigo' será IGNORADO")
    
    # Procesar CSV
    print("📖 Procesando archivo CSV...")
    
    try:
        calificaciones_a_crear = []
        batch_size = 1000
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                total_procesadas += 1
                
                if total_procesadas % 5000 == 0:
                    print(f"⏳ Procesadas {total_procesadas:,} filas...")
                
                try:
                    # 1. Extraer información de la evaluación del CSV
                    materia_nombre = row['materia'].strip()
                    curso_id = int(row['curso_id'])
                    titulo_evaluacion = row['titulo_evaluacion'].strip()
                    tipo_evaluacion_id = int(row['tipo_evaluacion_id'])
                    trimestre_id = int(row['trimestre_id'])
                    
                    # 2. Crear clave única para la evaluación
                    eval_key = f"{materia_nombre}_{curso_id}_{titulo_evaluacion}_{tipo_evaluacion_id}_{trimestre_id}"
                    
                    # 3. Buscar en cache o crear evaluación
                    if eval_key not in evaluaciones_cache:
                        evaluacion, content_type = buscar_o_crear_evaluacion(
                            materia_nombre, curso_id, titulo_evaluacion, 
                            tipo_evaluacion_id, trimestre_id
                        )
                        
                        if evaluacion and content_type:
                            evaluaciones_cache[eval_key] = (evaluacion, content_type)
                            evaluaciones_creadas += 1
                        else:
                            errores += 1
                            errores_detalle.append(f"Fila {total_procesadas}: No se pudo crear/encontrar evaluación - {eval_key}")
                            continue
                    
                    evaluacion, content_type = evaluaciones_cache[eval_key]
                    
                    # 4. Buscar estudiante
                    codigo_estudiante = str(row['estudiante_codigo']).strip()
                    estudiante = estudiantes_cache.get(codigo_estudiante)
                    
                    if not estudiante:
                        errores += 1
                        errores_detalle.append(f"Fila {total_procesadas}: Estudiante no encontrado - {codigo_estudiante}")
                        continue
                    
                    # 5. Verificar si ya existe esta calificación (SIN usar .exists() para evitar el error)
                    try:
                        calificacion_existente = Calificacion.objects.filter(
                            content_type=content_type,
                            object_id=evaluacion.id,
                            estudiante=estudiante
                        ).first()
                        
                        if calificacion_existente:
                            # Saltar si ya existe
                            duplicadas_omitidas += 1
                            continue
                    except Exception as e:
                        # Si hay error en la consulta, continuar sin verificar duplicados
                        print(f"⚠️ Error verificando duplicado (se continuará): {e}")
                    
                    # 6. IGNORAR completamente calificado_por_codigo
                    # calificado_por siempre será None
                    calificado_por = None
                    
                    # 7. Convertir valores numéricos
                    try:
                        nota = Decimal(str(row['nota']).strip())
                        penalizacion = Decimal(str(row.get('penalizacion_aplicada', '0')).strip())
                    except (ValueError, InvalidOperation) as e:
                        errores += 1
                        errores_detalle.append(f"Fila {total_procesadas}: Error convirtiendo valores numéricos - {e}")
                        continue
                    
                    # 8. Convertir valores booleanos
                    entrega_tardia = convertir_booleano_2023(row.get('entrega_tardia', False))
                    finalizada = convertir_booleano_2023(row.get('finalizada', True))
                    
                    # 9. Convertir fechas
                    fecha_entrega = None
                    if 'fecha_entrega' in row and row['fecha_entrega']:
                        try:
                            fecha_str = str(row['fecha_entrega']).strip()
                            fecha_naive = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                            fecha_entrega = timezone.make_aware(fecha_naive)
                        except ValueError:
                            fecha_entrega = timezone.now()
                    
                    fecha_calificacion = None
                    if 'fecha_calificacion' in row and row['fecha_calificacion']:
                        try:
                            fecha_str = str(row['fecha_calificacion']).strip()
                            fecha_naive = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                            fecha_calificacion = timezone.make_aware(fecha_naive)
                        except ValueError:
                            fecha_calificacion = timezone.now()
                    
                    # 10. Crear objeto Calificacion (SIN calificado_por)
                    calificacion = Calificacion(
                        content_type=content_type,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        nota=nota,
                        fecha_entrega=fecha_entrega,
                        entrega_tardia=entrega_tardia,
                        penalizacion_aplicada=penalizacion,
                        observaciones=row.get('observaciones', ''),
                        retroalimentacion=row.get('retroalimentacion', ''),
                        finalizada=finalizada,
                        calificado_por=None,  # Siempre None
                        fecha_calificacion=fecha_calificacion
                    )
                    
                    calificaciones_a_crear.append(calificacion)
                    
                    # Guardar en lotes
                    if len(calificaciones_a_crear) >= batch_size:
                        try:
                            with transaction.atomic():
                                Calificacion.objects.bulk_create(calificaciones_a_crear, ignore_conflicts=True)
                            creadas += len(calificaciones_a_crear)
                            print(f"💾 Guardadas {creadas:,} calificaciones...")
                            calificaciones_a_crear = []
                        except Exception as e:
                            print(f"❌ Error guardando lote: {e}")
                            # Intentar guardar uno por uno para identificar problemas
                            for cal in calificaciones_a_crear:
                                try:
                                    cal.save()
                                    creadas += 1
                                except Exception as e2:
                                    errores += 1
                                    errores_detalle.append(f"Error guardando calificación individual: {e2}")
                            calificaciones_a_crear = []
                
                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"Fila {total_procesadas}: Error general - {str(e)}")
                    if len(errores_detalle) <= 10:  # Mostrar solo los primeros 10 errores
                        print(f"❌ Error fila {total_procesadas}: {str(e)}")
        
        # Guardar último lote
        if calificaciones_a_crear:
            try:
                with transaction.atomic():
                    Calificacion.objects.bulk_create(calificaciones_a_crear, ignore_conflicts=True)
                creadas += len(calificaciones_a_crear)
            except Exception as e:
                print(f"❌ Error guardando último lote: {e}")
                # Intentar guardar uno por uno
                for cal in calificaciones_a_crear:
                    try:
                        cal.save()
                        creadas += 1
                    except Exception as e2:
                        errores += 1
                        errores_detalle.append(f"Error guardando calificación final: {e2}")
        
        # Resumen final
        fin = time.time()
        tiempo_total = fin - inicio
        
        print("\n✅ IMPORTACIÓN COMPLETADA")
        print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
        print(f"📊 Filas procesadas: {total_procesadas:,}")
        print(f"✅ Calificaciones creadas: {creadas:,}")
        print(f"📝 Evaluaciones creadas: {evaluaciones_creadas:,}")
        print(f"🔄 Duplicadas omitidas: {duplicadas_omitidas:,}")
        print(f"❌ Errores: {errores:,}")
        print(f"🚫 Campo 'calificado_por_codigo' fue IGNORADO completamente")
        
        if errores > 0:
            print(f"\n⚠️ PRIMEROS 10 ERRORES:")
            for i, error in enumerate(errores_detalle[:10], 1):
                print(f"   {i}. {error}")
            if len(errores_detalle) > 10:
                print(f"   ... y {len(errores_detalle)-10} errores más")
        
        return errores < total_procesadas * 0.1  # Considerar exitoso si menos del 10% tiene errores
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🎓 IMPORTADOR CORREGIDO - CALIFICACIONES 2023")
    print("⚡ Versión compatible con estructura CSV simplificada")
    print("🔧 Crea evaluaciones dinámicamente si no existen")
    print("🚫 IGNORA completamente el campo 'calificado_por_codigo'")
    print()
    
    # Diagnosticar estructura
    if not diagnosticar_estructura_base_datos_2023():
        print("\n❌ Los requisitos no están cumplidos. Verifica la estructura de la BD.")
        sys.exit(1)
    
    # Analizar estructura del CSV
    if not analizar_estructura_csv_2023():
        print("\n⚠️ Hay problemas en la estructura del CSV.")
        continuar = input("¿Desea continuar a pesar de los problemas? (s/n): ").lower() == 's'
        if not continuar:
            sys.exit(1)
    
    # Verificar estado actual
    verificar_estado_actual_2023()
    
    print("\n" + "=" * 60)
    confirmacion = input("¿Confirma ejecutar la importación corregida 2023? (s/n): ")
    if confirmacion.lower() == 's':
        exito = importar_calificaciones_2023_CORREGIDO()
        if exito:
            print("\n🎉 ¡Importación 2023 completada exitosamente!")
            verificar_estado_actual_2023()  # Verificar estado final
        else:
            print("\n💥 La importación falló o tuvo muchos errores")
    else:
        print("\n❌ Importación cancelada")