import os
import sys
import csv
import time
import django
from datetime import datetime
from decimal import Decimal, InvalidOperation
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
from Cursos.models import Calificacion, EvaluacionEntregable, EvaluacionParticipacion, Materia, Trimestre, TipoEvaluacion
from Usuarios.models import Usuario

def convertir_booleano_2024(valor):
    """Convierte valores booleanos específicos del CSV 2024"""
    if pd.isna(valor) or valor == '':
        return False
    
    if isinstance(valor, bool):
        return valor
    
    if isinstance(valor, str):
        valor_clean = valor.strip().upper()
        return valor_clean in ['TRUE', '1', 'SI', 'SÍ', 'YES', 'VERDADERO', 'T']
    
    if isinstance(valor, (int, float)):
        return bool(valor)
    
    return False

def diagnosticar_estructura_csv_2024():
    """Diagnóstico específico del CSV 2024 - ESTRUCTURA REAL"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    print("\n🔍 DIAGNÓSTICO CSV 2024:")
    print("=" * 50)
    
    try:
        # Leer muestra para análisis
        df_sample = pd.read_csv(csv_path, nrows=10)
        
        print("📋 COLUMNAS ENCONTRADAS:")
        for i, col in enumerate(df_sample.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n📊 Total columnas: {len(df_sample.columns)}")
        
        # Campos esperados según la estructura REAL del CSV 2024 (SIN content_type_id/object_id)
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
        
        # Campo que se IGNORARÁ
        campos_ignorados = ['calificado_por_codigo']
        print("\n🚫 CAMPOS QUE SE IGNORARÁN:")
        for campo in campos_ignorados:
            if campo in df_sample.columns:
                print(f"   ⏭️ {campo} - SERÁ IGNORADO (sin profesores asignados)")
        
        # Verificar valores únicos importantes
        print(f"\n📋 ANÁLISIS DE DATOS:")
        if 'trimestre_id' in df_sample.columns:
            print(f"   📚 Trimestres: {sorted(df_sample['trimestre_id'].unique())}")
        if 'tipo_evaluacion_id' in df_sample.columns:
            print(f"   🎯 Tipos evaluación: {sorted(df_sample['tipo_evaluacion_id'].unique())}")
        if 'estudiante_codigo' in df_sample.columns:
            print(f"   👥 Estudiantes (muestra): {len(df_sample['estudiante_codigo'].unique())}")
        if 'materia' in df_sample.columns:
            print(f"   📖 Materias: {df_sample['materia'].unique()}")
        if 'entrega_tardia' in df_sample.columns:
            print(f"   ⏰ Entrega tardía: {df_sample['entrega_tardia'].unique()}")
        if 'finalizada' in df_sample.columns:
            print(f"   ✅ Finalizada: {df_sample['finalizada'].unique()}")
        
        # Verificar rango de notas
        if 'nota' in df_sample.columns:
            notas_sample = pd.to_numeric(df_sample['nota'], errors='coerce')
            print(f"   📊 Rango notas (muestra): {notas_sample.min():.2f} - {notas_sample.max():.2f}")
        
        return len(campos_faltantes) == 0
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_evaluaciones_2024():
    """Verifica que existan las evaluaciones necesarias para 2024"""
    print("\n🔍 VERIFICANDO EVALUACIONES 2024:")
    print("=" * 40)
    
    try:
        # ContentTypes
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        print(f"✅ ContentType Entregable ID: {entregable_ct.id}")
        print(f"✅ ContentType Participación ID: {participacion_ct.id}")
        
        # Verificar evaluaciones 2024 por tipo (trimestres 10, 11, 12)
        entregables_2024 = EvaluacionEntregable.objects.filter(trimestre__id__in=[10, 11, 12])
        participacion_2024 = EvaluacionParticipacion.objects.filter(trimestre__id__in=[10, 11, 12])
        
        print(f"\n📝 Evaluaciones 2024:")
        print(f"   📋 Entregables: {entregables_2024.count()}")
        print(f"   🗣️ Participación: {participacion_2024.count()}")
        
        # Mostrar distribución por trimestre
        for trimestre in [10, 11, 12]:
            ent_count = entregables_2024.filter(trimestre__id=trimestre).count()
            part_count = participacion_2024.filter(trimestre__id=trimestre).count()
            print(f"   📚 Trimestre {trimestre}: {ent_count} entregables, {part_count} participación")
        
        total_evaluaciones = entregables_2024.count() + participacion_2024.count()
        print(f"\n📊 Total evaluaciones 2024: {total_evaluaciones}")
        
        return True  # Permitir continuar incluso si no hay evaluaciones (se crearán dinámicamente)
        
    except Exception as e:
        print(f"❌ Error verificando evaluaciones: {e}")
        return False

def buscar_o_crear_evaluacion_2024(materia_nombre, curso_id, titulo_evaluacion, tipo_evaluacion_id, trimestre_id):
    """Busca una evaluación existente o la crea si no existe (versión 2024)"""
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
        # Para 2024: tipo_evaluacion_id=1 es PARCIAL (entregable), tipo_evaluacion_id=2 es PRÁCTICO (entregable)
        
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
            
            content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
            return evaluacion, content_type
            
    except Exception as e:
        print(f"❌ Error buscando/creando evaluación 2024: {e}")
        return None, None

def importar_calificaciones_2024_ULTRA_RAPIDO():
    """Versión ULTRA RÁPIDA para estructura CSV 2024 real (sin content_type_id/object_id)"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2024.csv')
    
    inicio = time.time()
    print("⚡ IMPORTACIÓN ULTRA RÁPIDA - CALIFICACIONES 2024")
    print("📂 Archivo: calificaciones_2024.csv (estructura real)")
    print("🚫 IGNORANDO campo 'calificado_por_codigo'")
    print("🚀 Sin prints durante guardado para máxima velocidad")
    print("🔧 Crea evaluaciones dinámicamente si no existen")
    
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
    
    # Cache de datos (optimizado)
    print("📊 Cargando cache optimizado...")
    
    # Cache de estudiantes (solo los necesarios)
    estudiantes_cache = {}
    for estudiante in Usuario.objects.filter(rol__id=2).only('codigo', 'id'):
        estudiantes_cache[str(estudiante.codigo)] = estudiante
    
    # Cache de evaluaciones (se llenará dinámicamente)
    evaluaciones_cache = {}
    
    print(f"✅ Cache: {len(estudiantes_cache)} estudiantes")
    print(f"🚫 Campo 'calificado_por_codigo' será IGNORADO")
    print("🚀 Iniciando procesamiento ultra rápido...")
    
    # Procesar CSV sin prints de progreso durante guardado
    try:
        calificaciones_a_crear = []
        batch_size = 1000  # Lotes grandes para mayor velocidad
        ultimo_progreso = 0
        intervalo_progreso = 10000  # Solo mostrar progreso cada 10k registros
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                total_procesadas += 1
                
                # Progreso menos frecuente para no ralentizar
                if total_procesadas - ultimo_progreso >= intervalo_progreso:
                    print(f"⏳ {total_procesadas:,} registros procesados...")
                    ultimo_progreso = total_procesadas
                
                try:
                    # 1. Extraer información de la evaluación del CSV (como en 2023)
                    materia_nombre = row['materia'].strip()
                    curso_id = int(row['curso_id'])
                    titulo_evaluacion = row['titulo_evaluacion'].strip()
                    tipo_evaluacion_id = int(row['tipo_evaluacion_id'])
                    trimestre_id = int(row['trimestre_id'])
                    
                    # 2. Crear clave única para la evaluación
                    eval_key = f"{materia_nombre}_{curso_id}_{titulo_evaluacion}_{tipo_evaluacion_id}_{trimestre_id}"
                    
                    # 3. Buscar en cache o crear evaluación
                    if eval_key not in evaluaciones_cache:
                        evaluacion, content_type = buscar_o_crear_evaluacion_2024(
                            materia_nombre, curso_id, titulo_evaluacion, 
                            tipo_evaluacion_id, trimestre_id
                        )
                        
                        if evaluacion and content_type:
                            evaluaciones_cache[eval_key] = (evaluacion, content_type)
                            evaluaciones_creadas += 1
                        else:
                            errores += 1
                            if len(errores_detalle) < 10:
                                errores_detalle.append(f"Fila {total_procesadas}: No se pudo crear/encontrar evaluación - {eval_key}")
                            continue
                    
                    evaluacion, content_type = evaluaciones_cache[eval_key]
                    
                    # 4. Buscar estudiante
                    codigo_estudiante = str(row['estudiante_codigo']).strip()
                    estudiante = estudiantes_cache.get(codigo_estudiante)
                    
                    if not estudiante:
                        errores += 1
                        if len(errores_detalle) < 10:
                            errores_detalle.append(f"Fila {total_procesadas}: Estudiante no encontrado - {codigo_estudiante}")
                        continue
                    
                    # 5. Verificar si ya existe esta calificación
                    try:
                        calificacion_existente = Calificacion.objects.filter(
                            content_type=content_type,
                            object_id=evaluacion.id,
                            estudiante=estudiante
                        ).first()
                        
                        if calificacion_existente:
                            duplicadas_omitidas += 1
                            continue
                    except Exception as e:
                        # Si hay error en la consulta, continuar sin verificar duplicados
                        pass
                    
                    # 6. IGNORAR COMPLETAMENTE calificado_por_codigo
                    calificado_por = None
                    
                    # 7. Convertir y validar nota (optimizado)
                    try:
                        nota_str = str(row['nota']).replace(',', '.').strip()
                        nota = Decimal(nota_str)
                        if nota < 0 or nota > 100:
                            errores += 1
                            continue
                    except (ValueError, InvalidOperation, TypeError):
                        errores += 1
                        continue
                    
                    # 8. Convertir penalización (optimizado)
                    try:
                        pen_str = str(row.get('penalizacion_aplicada', '0')).replace(',', '.').strip()
                        penalizacion = Decimal(pen_str)
                        if penalizacion < 0 or penalizacion > 100:
                            penalizacion = Decimal('0')
                    except (ValueError, InvalidOperation, TypeError):
                        penalizacion = Decimal('0')
                    
                    # 9. Convertir valores booleanos (optimizado)
                    entrega_tardia = convertir_booleano_2024(row.get('entrega_tardia', False))
                    finalizada = convertir_booleano_2024(row.get('finalizada', True))
                    
                    # 10. Convertir fechas (optimizado)
                    fecha_entrega = None
                    fecha_entrega_str = row.get('fecha_entrega', '').strip()
                    if fecha_entrega_str and fecha_entrega_str != 'nan':
                        try:
                            fecha_naive = datetime.strptime(fecha_entrega_str, '%Y-%m-%d %H:%M:%S')
                            fecha_entrega = timezone.make_aware(fecha_naive)
                        except ValueError:
                            fecha_entrega = timezone.now()
                    
                    fecha_calificacion = None
                    fecha_cal_str = row.get('fecha_calificacion', '').strip()
                    if fecha_cal_str and fecha_cal_str != 'nan':
                        try:
                            fecha_naive = datetime.strptime(fecha_cal_str, '%Y-%m-%d %H:%M:%S')
                            fecha_calificacion = timezone.make_aware(fecha_naive)
                        except ValueError:
                            fecha_calificacion = timezone.now()
                    
                    # 11. Crear objeto Calificacion (sin calificado_por)
                    calificacion = Calificacion(
                        content_type=content_type,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        nota=nota,
                        fecha_entrega=fecha_entrega,
                        entrega_tardia=entrega_tardia,
                        penalizacion_aplicada=penalizacion,
                        observaciones=row.get('observaciones', '').strip()[:500],  # Limitar tamaño
                        retroalimentacion=row.get('retroalimentacion', '').strip()[:1000],  # Limitar tamaño
                        finalizada=finalizada,
                        calificado_por=None,  # SIEMPRE None
                        fecha_calificacion=fecha_calificacion
                    )
                    
                    calificaciones_a_crear.append(calificacion)
                    
                    # Guardar en lotes SIN PRINTS para máxima velocidad
                    if len(calificaciones_a_crear) >= batch_size:
                        try:
                            with transaction.atomic():
                                Calificacion.objects.bulk_create(
                                    calificaciones_a_crear, 
                                    ignore_conflicts=True,
                                    batch_size=500
                                )
                            creadas += len(calificaciones_a_crear)
                            calificaciones_a_crear = []
                        except Exception as e:
                            # En caso de error, intentar guardar uno por uno
                            for cal in calificaciones_a_crear:
                                try:
                                    cal.save()
                                    creadas += 1
                                except:
                                    errores += 1
                            calificaciones_a_crear = []
                
                except Exception as e:
                    errores += 1
                    if len(errores_detalle) < 10:
                        errores_detalle.append(f"Fila {total_procesadas}: Error general - {str(e)}")
                    continue
        
        # Guardar último lote sin print
        if calificaciones_a_crear:
            try:
                with transaction.atomic():
                    Calificacion.objects.bulk_create(
                        calificaciones_a_crear, 
                        ignore_conflicts=True,
                        batch_size=500
                    )
                creadas += len(calificaciones_a_crear)
            except Exception as e:
                for cal in calificaciones_a_crear:
                    try:
                        cal.save()
                        creadas += 1
                    except:
                        errores += 1
        
        # Resumen final
        fin = time.time()
        tiempo_total = fin - inicio
        
        print("\n" + "="*70)
        print("⚡ IMPORTACIÓN ULTRA RÁPIDA COMPLETADA")
        print("="*70)
        print(f"📊 Filas procesadas: {total_procesadas:,}")
        print(f"✅ Calificaciones creadas: {creadas:,}")
        print(f"📝 Evaluaciones creadas: {evaluaciones_creadas:,}")
        print(f"🔄 Duplicadas omitidas: {duplicadas_omitidas:,}")
        print(f"❌ Errores: {errores:,}")
        print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
        print(f"🚫 Campo 'calificado_por_codigo' IGNORADO completamente")
        
        if tiempo_total > 0:
            velocidad = total_procesadas / tiempo_total
            print(f"🚀 Velocidad: {velocidad:.0f} registros/segundo")
            
            if creadas > 0:
                vel_creacion = creadas / tiempo_total
                print(f"💾 Velocidad creación: {vel_creacion:.0f} calificaciones/segundo")
        
        # Mostrar solo primeros errores si los hay
        if errores_detalle:
            print(f"\n⚠️ PRIMEROS ERRORES:")
            for i, error in enumerate(errores_detalle[:5], 1):
                print(f"   {i}. {error}")
            if errores > 5:
                print(f"   ... y {errores-5} errores más (omitidos para velocidad)")
        
        return errores < total_procesadas * 0.1  # Éxito si menos del 10% son errores
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("⚡ IMPORTADOR ULTRA RÁPIDO - CALIFICACIONES 2024")
    print("🚫 IGNORA completamente el campo 'calificado_por_codigo'")
    print("🚀 Sin prints durante guardado para máxima velocidad")
    print("📊 Adaptado para estructura CSV real de 2024")
    print("🔧 Crea evaluaciones dinámicamente si no existen")
    print()
    
    # Diagnóstico de estructura CSV
    if not diagnosticar_estructura_csv_2024():
        print("\n⚠️ Hay problemas en la estructura del CSV.")
        continuar = input("¿Desea continuar a pesar de los problemas? (s/n): ").lower() == 's'
        if not continuar:
            sys.exit(1)
    
    # Verificar evaluaciones disponibles
    verificar_evaluaciones_2024()
    
    print("\n" + "=" * 60)
    confirmacion = input("¿Ejecutar importación ULTRA RÁPIDA para 2024? (s/n): ")
    
    if confirmacion.lower() == 's':
        print("\n🚀 Iniciando importación ultra rápida...")
        exito = importar_calificaciones_2024_ULTRA_RAPIDO()
        if exito:
            print("\n🎉 ¡Importación 2024 completada exitosamente!")
        else:
            print("\n⚠️ Importación completada con errores significativos.")
    else:
        print("\n❌ Importación cancelada por el usuario")