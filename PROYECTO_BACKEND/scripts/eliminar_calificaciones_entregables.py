import os
import sys
import django
import time
from django.db import transaction

# Configurar entorno Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar modelos necesarios
from Cursos.models import Calificacion, Trimestre, EvaluacionEntregable
from django.contrib.contenttypes.models import ContentType

def main():
    """Función principal para eliminar calificaciones de evaluaciones entregables"""
    print("\n🗑️ ELIMINACIÓN DE CALIFICACIONES DE EVALUACIONES ENTREGABLES")
    print("=" * 70)
    print("\nEste script eliminará TODAS las calificaciones asociadas a evaluaciones")
    print("entregables (parciales y prácticos) de los años 2022, 2023 y 2024.")
    print("\n⚠️ ADVERTENCIA: Esta acción no se puede deshacer.")
    
    years = [2022, 2023, 2024]
    
    # Mostrar estadísticas antes de eliminar
    mostrar_estadisticas_actuales(years)
    
    # Confirmación
    confirmacion = input("\n¿Estás seguro que deseas eliminar estas calificaciones? (escriba 'SI' para confirmar): ")
    
    if confirmacion.strip().upper() != "SI":
        print("\n❌ Operación cancelada. No se eliminaron calificaciones.")
        return
    
    # Confirmar tipo de eliminación
    print("\nSeleccione el tipo de eliminación:")
    print("1. 🚀 Eliminación RÁPIDA (recomendado para grandes volúmenes)")
    print("2. 🔍 Eliminación DETALLADA (muestra contadores)")
    
    modo = input("\nSeleccione una opción (1/2): ").strip()
    
    if modo == "1":
        eliminar_calificaciones_rapido(years)
    else:
        eliminar_calificaciones_detallado(years)
    
    # Mostrar estadísticas después de eliminar
    print("\n✅ Proceso completado. Estadísticas actualizadas:")
    mostrar_estadisticas_actuales(years)

def obtener_trimestres_ids(years):
    """Obtiene los IDs de trimestres para los años especificados"""
    trimestres_ids_por_year = {}
    for year in years:
        trimestres = Trimestre.objects.filter(nombre__contains=str(year))
        trimestres_ids_por_year[year] = list(trimestres.values_list('id', flat=True))
    return trimestres_ids_por_year

def mostrar_estadisticas_actuales(years):
    """Muestra estadísticas de calificaciones actuales por año"""
    print("\n📊 ESTADÍSTICAS ACTUALES:")
    
    ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
    trimestres_ids_por_year = obtener_trimestres_ids(years)
    
    for year in years:
        # Obtener evaluaciones entregables de este año
        evaluacion_ids = EvaluacionEntregable.objects.filter(
            trimestre_id__in=trimestres_ids_por_year[year]
        ).values_list('id', flat=True)
        
        # Contar calificaciones
        count = Calificacion.objects.filter(
            content_type=ct_entregable,
            object_id__in=evaluacion_ids
        ).count()
        
        print(f"  • {year}: {count:,} calificaciones de evaluaciones entregables")

def eliminar_calificaciones_rapido(years):
    """Eliminación rápida de calificaciones usando un solo query por año"""
    inicio = time.time()
    
    ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
    trimestres_ids_por_year = obtener_trimestres_ids(years)
    
    total_eliminado = 0
    
    for year in years:
        print(f"\n🚀 Eliminando calificaciones de entregables {year}...")
        
        # Obtener IDs de evaluaciones del año
        evaluacion_ids = EvaluacionEntregable.objects.filter(
            trimestre_id__in=trimestres_ids_por_year[year]
        ).values_list('id', flat=True)
        
        # Eliminar en una sola transacción
        with transaction.atomic():
            eliminados = Calificacion.objects.filter(
                content_type=ct_entregable,
                object_id__in=evaluacion_ids
            ).delete()[0]
            
            total_eliminado += eliminados
            
            print(f"  ✅ {eliminados:,} calificaciones eliminadas para {year}")
    
    fin = time.time()
    print(f"\n🏁 Proceso completado en {fin-inicio:.2f} segundos.")
    print(f"  Total eliminado: {total_eliminado:,} calificaciones")

def eliminar_calificaciones_detallado(years):
    """Eliminación detallada que muestra progreso"""
    inicio = time.time()
    
    ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
    trimestres_ids_por_year = obtener_trimestres_ids(years)
    
    total_eliminado = 0
    
    for year in years:
        print(f"\n🔍 Eliminando calificaciones de entregables {year}...")
        
        # Obtener todas las evaluaciones del año
        evaluaciones = EvaluacionEntregable.objects.filter(
            trimestre_id__in=trimestres_ids_por_year[year]
        )
        
        total_evaluaciones = evaluaciones.count()
        print(f"  Encontradas {total_evaluaciones:,} evaluaciones para {year}")
        
        # Eliminar por lotes para evitar bloqueos prolongados
        procesadas = 0
        eliminadas_year = 0
        lote_size = 1000
        
        for i in range(0, total_evaluaciones, lote_size):
            lote = evaluaciones[i:i+lote_size]
            lote_ids = [eval.id for eval in lote]
            
            with transaction.atomic():
                eliminados_lote = Calificacion.objects.filter(
                    content_type=ct_entregable,
                    object_id__in=lote_ids
                ).delete()[0]
                
                eliminadas_year += eliminados_lote
                total_eliminado += eliminados_lote
            
            procesadas += len(lote)
            
            # Mostrar progreso
            if procesadas % 5000 == 0 or procesadas >= total_evaluaciones:
                porcentaje = (procesadas / total_evaluaciones) * 100
                tiempo_transcurrido = time.time() - inicio
                print(f"  ⏳ {procesadas:,}/{total_evaluaciones:,} evaluaciones procesadas ({porcentaje:.1f}%) - {eliminadas_year:,} calificaciones eliminadas")
    
    fin = time.time()
    print(f"\n🏁 Proceso completado en {fin-inicio:.2f} segundos.")
    print(f"  Total eliminado: {total_eliminado:,} calificaciones")

if __name__ == "__main__":
    main()