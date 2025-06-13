import os
import sys
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import time
from django.utils import timezone

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

try:
    import django
    django.setup()
    import pandas as pd # type: ignore
except Exception as e:
    print(f"❌ Error inicializando Django: {e}")
    sys.exit(1)

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Calificacion, EvaluacionEntregable, Materia
from Usuarios.models import Usuario

def verificar_estructura_csv():
    """Verifica la estructura del archivo CSV"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2022.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo no encontrado: {csv_path}")
        return False
    
    print("🔍 VERIFICANDO ESTRUCTURA DEL CSV:")
    
    try:
        # Leer las primeras filas para análisis
        df_sample = pd.read_csv(csv_path, nrows=10)
        
        # Columnas esperadas
        columnas_esperadas = [
            'estudiante_codigo', 'materia', 'curso_id', 'titulo_evaluacion', 
            'trimestre_id', 'nota', 'penalizacion_aplicada', 'entrega_tardia', 
            'finalizada', 'fecha_calificacion'
        ]
        
        columnas_encontradas = df_sample.columns.tolist()
        print(f"📊 Columnas encontradas: {columnas_encontradas}")
        
        # Verificar columnas faltantes
        faltantes = [col for col in columnas_esperadas if col not in columnas_encontradas]
        if faltantes:
            print(f"⚠️ Columnas faltantes: {faltantes}")
        
        # Verificar tipos de datos
        print("\n📋 MUESTRA DE DATOS:")
        for col in columnas_encontradas[:5]:  # Mostrar solo las primeras 5 columnas
            valores_unicos = df_sample[col].unique()[:3]  # Primeros 3 valores únicos
            print(f"   {col}: {valores_unicos}")
        
        # Verificar valores booleanos específicamente
        if 'entrega_tardia' in df_sample.columns:
            valores_tardia = df_sample['entrega_tardia'].unique()
            print(f"   entrega_tardia valores únicos: {valores_tardia}")
        
        if 'finalizada' in df_sample.columns:
            valores_finalizada = df_sample['finalizada'].unique()
            print(f"   finalizada valores únicos: {valores_finalizada}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando CSV: {e}")
        return False

def convertir_booleano(valor):
    """Convierte valores a booleano de manera robusta"""
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

def importar_calificaciones_2022_mejorado():
    """Versión mejorada del importador de calificaciones 2022"""
    csv_path = os.path.join(project_root, 'csv', 'calificaciones_2022.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Archivo CSV no encontrado: {csv_path}")
        return False
    
    print("🚀 INICIANDO IMPORTACIÓN MEJORADA 2022")
    inicio = time.time()
    
    # Contadores
    total_procesadas = 0
    creadas = 0
    errores = 0
    errores_detalle = []
    
    # Pre-cargar datos
    print("📊 Cargando datos en cache...")
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    
    # Cache de estudiantes
    estudiantes_cache = {}
    for estudiante in Usuario.objects.filter(rol__id=2):
        estudiantes_cache[str(estudiante.codigo).strip()] = estudiante
    
    # Cache de materias - más flexible
    materias_cache = {}
    for materia in Materia.objects.all():
        # Múltiples claves para la misma materia
        clave1 = f"{materia.nombre.strip()}_{materia.curso_id}"
        clave2 = materia.nombre.strip()
        materias_cache[clave1] = materia
        materias_cache[clave2] = materia
    
    # Cache de evaluaciones - más flexible
    evaluaciones_cache = {}
    for evaluacion in EvaluacionEntregable.objects.filter(trimestre__id__in=[1, 2, 3, 4, 5, 6]):
        # Múltiples claves para la misma evaluación
        clave1 = f"{evaluacion.titulo.strip()}_{evaluacion.trimestre.id}_{evaluacion.materia.id}"
        clave2 = f"{evaluacion.titulo.strip()}_{evaluacion.trimestre.id}"
        evaluaciones_cache[clave1] = evaluacion
        evaluaciones_cache[clave2] = evaluacion
    
    print(f"✅ Cache cargado: {len(estudiantes_cache)} estudiantes, {len(set(materias_cache.values()))} materias, {len(set(evaluaciones_cache.values()))} evaluaciones")
    
    # Procesar CSV con pandas para mejor manejo de tipos
    try:
        print("📖 Leyendo archivo CSV...")
        df = pd.read_csv(csv_path)
        total_filas = len(df)
        print(f"📊 Total de filas en CSV: {total_filas:,}")
        
        calificaciones_a_crear = []
        batch_size = 1000
        
        for index, row in df.iterrows():
            total_procesadas += 1
            
            if total_procesadas % 5000 == 0:
                print(f"⏳ Procesadas {total_procesadas:,}/{total_filas:,} filas...")
            
            try:
                # 1. Buscar estudiante
                codigo_estudiante = str(row['estudiante_codigo']).strip()
                estudiante = estudiantes_cache.get(codigo_estudiante)
                if not estudiante:
                    errores += 1
                    errores_detalle.append(f"Fila {index+2}: Estudiante no encontrado: {codigo_estudiante}")
                    continue
                
                # 2. Buscar materia (intentar múltiples claves)
                materia_nombre = str(row['materia']).strip()
                curso_id = int(row['curso_id'])
                
                materia = None
                claves_materia = [
                    f"{materia_nombre}_{curso_id}",
                    materia_nombre
                ]
                
                for clave in claves_materia:
                    materia = materias_cache.get(clave)
                    if materia and materia.curso_id == curso_id:
                        break
                
                if not materia:
                    errores += 1
                    errores_detalle.append(f"Fila {index+2}: Materia no encontrada: {materia_nombre} (curso {curso_id})")
                    continue
                
                # 3. Buscar evaluación (intentar múltiples claves)
                titulo_evaluacion = str(row['titulo_evaluacion']).strip()
                trimestre_id = int(row['trimestre_id'])
                
                evaluacion = None
                claves_evaluacion = [
                    f"{titulo_evaluacion}_{trimestre_id}_{materia.id}",
                    f"{titulo_evaluacion}_{trimestre_id}"
                ]
                
                for clave in claves_evaluacion:
                    eval_temp = evaluaciones_cache.get(clave)
                    if eval_temp and eval_temp.materia.id == materia.id and eval_temp.trimestre.id == trimestre_id:
                        evaluacion = eval_temp
                        break
                
                if not evaluacion:
                    errores += 1
                    errores_detalle.append(f"Fila {index+2}: Evaluación no encontrada: {titulo_evaluacion} (trimestre {trimestre_id}, materia {materia.id})")
                    continue
                
                # 4. Convertir valores numéricos
                try:
                    nota = Decimal(str(row['nota']).strip())
                    penalizacion = Decimal(str(row.get('penalizacion_aplicada', 0)).strip()) if pd.notna(row.get('penalizacion_aplicada')) else Decimal('0')
                except (ValueError, InvalidOperation) as e:
                    errores += 1
                    errores_detalle.append(f"Fila {index+2}: Error en valores numéricos: {e}")
                    continue
                
                # 5. Convertir valores booleanos
                entrega_tardia = convertir_booleano(row.get('entrega_tardia', False))
                finalizada = convertir_booleano(row.get('finalizada', True))
                
                # 6. Fecha de calificación
                fecha_calificacion = timezone.now()
                if pd.notna(row.get('fecha_calificacion')):
                    try:
                        fecha_str = str(row['fecha_calificacion']).strip()
                        # Intentar diferentes formatos de fecha
                        formatos = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
                        for formato in formatos:
                            try:
                                fecha_naive = datetime.strptime(fecha_str, formato)
                                fecha_calificacion = timezone.make_aware(fecha_naive)
                                break
                            except ValueError:
                                continue
                    except:
                        pass  # Usar fecha actual si hay error
                
                # 7. Crear objeto calificación
                calificacion = Calificacion(
                    content_type=entregable_ct,
                    object_id=evaluacion.id,
                    estudiante=estudiante,
                    nota=nota,
                    entrega_tardia=entrega_tardia,
                    penalizacion_aplicada=penalizacion,
                    finalizada=finalizada,
                    fecha_calificacion=fecha_calificacion,
                    observaciones=f"Importado CSV 2022 - fila {index+2}"
                )
                
                calificaciones_a_crear.append(calificacion)
                
                # Guardar en lotes
                if len(calificaciones_a_crear) >= batch_size:
                    with transaction.atomic():
                        Calificacion.objects.bulk_create(calificaciones_a_crear, ignore_conflicts=True)
                    creadas += len(calificaciones_a_crear)
                    calificaciones_a_crear = []
                    print(f"💾 Guardadas {creadas:,} calificaciones...")
                
            except Exception as e:
                errores += 1
                errores_detalle.append(f"Fila {index+2}: Error general: {str(e)}")
        
        # Guardar último lote
        if calificaciones_a_crear:
            with transaction.atomic():
                Calificacion.objects.bulk_create(calificaciones_a_crear, ignore_conflicts=True)
            creadas += len(calificaciones_a_crear)
        
        # Resumen
        fin = time.time()
        tiempo_total = fin - inicio
        
        print("\n✅ IMPORTACIÓN COMPLETADA")
        print(f"⏱️ Tiempo: {tiempo_total:.2f} segundos")
        print(f"📊 Filas procesadas: {total_procesadas:,}")
        print(f"✅ Calificaciones creadas: {creadas:,}")
        print(f"❌ Errores: {errores:,}")
        
        # Mostrar algunos errores
        if errores_detalle:
            print(f"\n⚠️ PRIMEROS 10 ERRORES:")
            for error in errores_detalle[:10]:
                print(f"   {error}")
            if len(errores_detalle) > 10:
                print(f"   ... y {len(errores_detalle)-10} errores más")
        
        return errores == 0
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🎓 IMPORTADOR MEJORADO - CALIFICACIONES 2022")
    print("🔧 Versión con mejor manejo de errores y validaciones")
    
    # Verificar estructura primero
    if not verificar_estructura_csv():
        print("\n❌ Problemas en la estructura del CSV")
        sys.exit(1)
    
    confirmacion = input("\n¿Ejecutar importación mejorada? (s/n): ")
    if confirmacion.lower() == 's':
        exito = importar_calificaciones_2022_mejorado()
        if exito:
            print("\n🎉 ¡Importación exitosa!")
        else:
            print("\n⚠️ Importación completada con errores")
    else:
        print("\n❌ Operación cancelada")