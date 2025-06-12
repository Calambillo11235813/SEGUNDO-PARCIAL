import os
import django
import sys
import csv
import time
from datetime import datetime

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Materia, Trimestre, TipoEvaluacion, EvaluacionParticipacion
from Usuarios.models import Usuario

def importar_participaciones_2023_ultra_rapido():
    """Versión ultra-rápida para importar participaciones 2023"""
    csv_path = os.path.join(project_root, 'csv', 'participaciones_2023.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - PARTICIPACIONES 2023")
    print("📚 Evaluaciones de participación estudiantil...")
    
    total = 0
    creados = 0
    errores = 0
    
    # Pre-cargar datos
    print("📊 Pre-cargando datos...")
    materias_dict = {f"{m.nombre}_{m.curso_id}": m for m in Materia.objects.all()}
    trimestres_dict = {t.id: t for t in Trimestre.objects.filter(id__in=[7, 8, 9])}  # Trimestres 2023
    tipo_evaluacion = TipoEvaluacion.objects.get(id=3)  # Tipo evaluación participación
    
    print(f"✅ Listo | {len(materias_dict)} materias | {len(trimestres_dict)} trimestres | ⚡ Procesando...")
    
    participaciones_bulk = []
    errores_detalle = []
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            total += 1
            try:
                # Buscar materia por nombre y curso_id
                materia = materias_dict.get(f"{row['materia']}_{row['curso_id']}")
                
                # Buscar trimestre
                trimestre = trimestres_dict.get(int(row['trimestre_id']))
                
                if materia and trimestre:
                    # ✅ CORRECCIÓN: Solo usar campos que EXISTEN en el modelo
                    participaciones_bulk.append(EvaluacionParticipacion(
                        materia=materia,
                        trimestre=trimestre,
                        tipo_evaluacion=tipo_evaluacion,
                        titulo=row['titulo'],
                        descripcion=row['descripcion'],
                        porcentaje_nota_final=float(row['porcentaje_nota_final']),
                        fecha_registro=datetime.strptime(row['fecha_registro'], '%Y-%m-%d').date(),
                        activo=True,
                        publicado=True  # ✅ CAMPO QUE SÍ EXISTE
                        # ❌ REMOVIDOS: criterios_evaluacion, peso_porcentaje
                    ))
                    creados += 1
                    
                    # Insertar en lotes de 1000 para mejor debugging
                    if len(participaciones_bulk) >= 1000:
                        try:
                            EvaluacionParticipacion.objects.bulk_create(participaciones_bulk, ignore_conflicts=True)
                            participaciones_bulk = []
                            print(f"✅ Lote insertado: {creados:,} registros procesados")
                        except Exception as e:
                            print(f"❌ Error en lote: {e}")
                            errores += len(participaciones_bulk)
                            participaciones_bulk = []
                else:
                    errores += 1
                    if not materia:
                        errores_detalle.append(f"Materia no encontrada: {row['materia']} - Curso {row['curso_id']}")
                    if not trimestre:
                        errores_detalle.append(f"Trimestre no encontrado: ID {row['trimestre_id']}")
                        
            except Exception as e:
                errores += 1
                errores_detalle.append(f"Error fila {total}: {str(e)}")
                if len(errores_detalle) <= 5:  # Solo mostrar primeros 5 errores
                    print(f"❌ Error fila {total}: {str(e)}")
    
    # Insertar registros restantes
    if participaciones_bulk:
        try:
            EvaluacionParticipacion.objects.bulk_create(participaciones_bulk, ignore_conflicts=True)
            print(f"✅ Lote final insertado")
        except Exception as e:
            print(f"❌ Error en lote final: {e}")
            errores += len(participaciones_bulk)
    
    tiempo_total = time.time() - inicio
    velocidad = creados / tiempo_total if tiempo_total > 0 else 0
    
    print(f"\n🎉 PARTICIPACIONES 2023 COMPLETADAS:")
    print(f"   ✅ {creados:,}/{total:,} registros en {tiempo_total:.2f}s")
    print(f"   🚀 Velocidad: {velocidad:.0f} registros/segundo")
    print(f"   ❌ Errores: {errores:,}")
    print(f"   📚 Período: Año académico 2023 (Trimestres 7, 8, 9)")
    print(f"   🎯 Tipo: Evaluaciones de participación estudiantil")

def verificar_datos_participaciones_2023():
    """Verifica los datos después de la importación"""
    print("\n📊 VERIFICACIÓN DE PARTICIPACIONES 2023")
    print("=" * 50)
    
    from django.db.models import Count, Avg
    
    # Verificar por trimestre
    for trimestre_id in [7, 8, 9]:
        try:
            trimestre = Trimestre.objects.get(id=trimestre_id)
            
            # Estadísticas de participaciones
            stats = EvaluacionParticipacion.objects.filter(
                trimestre_id=trimestre_id,
                tipo_evaluacion_id=3
            ).aggregate(
                total=Count('id'),
                promedio_porcentaje=Avg('porcentaje_nota_final')
            )
            
            if stats['total'] > 0:
                print(f"📚 {trimestre.nombre} (ID: {trimestre_id})")
                print(f"   📊 Total participaciones: {stats['total']:,}")
                print(f"   📈 Promedio porcentaje: {stats['promedio_porcentaje']:.2f}%")
                
                # Contar por materia
                materias_count = EvaluacionParticipacion.objects.filter(
                    trimestre_id=trimestre_id,
                    tipo_evaluacion_id=3
                ).values('materia__nombre').distinct().count()
                
                print(f"   📖 Materias con participaciones: {materias_count}")
                print()
            else:
                print(f"❌ {trimestre.nombre} (ID: {trimestre_id}): Sin participaciones")
            
        except Trimestre.DoesNotExist:
            print(f"❌ Trimestre ID {trimestre_id} no encontrado")
    
    # Estadísticas generales
    total_participaciones = EvaluacionParticipacion.objects.filter(
        trimestre_id__in=[7, 8, 9],
        tipo_evaluacion_id=3
    ).count()
    
    print(f"📈 RESUMEN GENERAL 2023:")
    print(f"   📚 Total participaciones importadas: {total_participaciones:,}")
    print(f"   🎯 Distribución: 5 participaciones × materia × trimestre")
    print(f"   ⚡ Sistema optimizado para evaluación continua")

def verificar_archivo_participaciones():
    """Verifica el archivo CSV antes de importar"""
    csv_path = os.path.join(project_root, 'csv', 'participaciones_2023.csv')
    
    print("🔍 VERIFICACIÓN DEL ARCHIVO CSV")
    print("=" * 40)
    
    if os.path.isfile(csv_path):
        tamaño = os.path.getsize(csv_path)
        
        # Contar líneas
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lineas = sum(1 for _ in f) - 1  # -1 por header
        except:
            lineas = "Error"
        
        print(f"✅ participaciones_2023.csv")
        print(f"   📁 Tamaño: {tamaño:,} bytes")
        print(f"   🔤 Codificación: UTF-8")
        print(f"   📊 Registros: {lineas:,}")
        print(f"   🎯 Estructura: materia,curso_id,tipo_evaluacion_id,trimestre_id,titulo,descripcion,porcentaje_nota_final,fecha_registro")
    else:
        print(f"❌ participaciones_2023.csv: No encontrado")
        print(f"📍 Ruta esperada: {csv_path}")
    print()

def verificar_estructura_modelo():
    """Verifica la estructura real del modelo antes de importar"""
    print("🔍 VERIFICACIÓN DE ESTRUCTURA DEL MODELO")
    print("=" * 50)
    
    campos_reales = [f.name for f in EvaluacionParticipacion._meta.fields]
    print(f"📋 Campos disponibles en EvaluacionParticipacion:")
    for i, campo in enumerate(campos_reales, 1):
        print(f"   {i:2d}. {campo}")
    
    print(f"\n✅ Total de campos: {len(campos_reales)}")
    print(f"🎯 Tipo de evaluación ID 3: {TipoEvaluacion.objects.get(id=3)}")

if __name__ == '__main__':
    print("🎓 IMPORTADOR ULTRA-RÁPIDO - PARTICIPACIONES 2023 (CORREGIDO)")
    print("📚 Evaluaciones de participación estudiantil")
    print("⚡ Optimizado para máximo rendimiento")
    print()
    
    # Verificar estructura del modelo
    verificar_estructura_modelo()
    print()
    
    # Verificar archivo
    verificar_archivo_participaciones()
    
    respuesta = input("¿Continuar con la importación? (s/n): ").lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        print()
        importar_participaciones_2023_ultra_rapido()
        verificar_datos_participaciones_2023()
    else:
        print("❌ Importación cancelada")