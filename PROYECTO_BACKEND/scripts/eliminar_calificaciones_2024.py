import os
import sys
import django
import time
from datetime import datetime

# Configuración Django
print("🔄 Inicializando entorno Django...")
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

try:
    django.setup()
    print("✅ Django inicializado correctamente")
except Exception as e:
    print(f"❌ Error inicializando Django: {e}")
    sys.exit(1)

# Imports de Django
from django.contrib.contenttypes.models import ContentType
from Cursos.models import Calificacion, EvaluacionEntregable, Trimestre
from django.db import transaction

def main():
    print("\n🗑️  ELIMINACIÓN DE CALIFICACIONES 2024")
    print("====================================")
    
    # Obtener ContentType
    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
    
    # Obtener trimestres 2024
    trimestres_2024 = Trimestre.objects.filter(nombre__contains='2024').order_by('id')
    if not trimestres_2024.exists():
        print("❌ No se encontraron trimestres para el año 2024")
        return
    
    print(f"Trimestres 2024 encontrados: {trimestres_2024.count()}")
    for t in trimestres_2024:
        print(f"- ID: {t.id}, Nombre: {t.nombre}")
    
    # Análisis por trimestre
    print("\n📊 ANÁLISIS POR TRIMESTRE:")
    print("------------------------")
    total_general = 0
    
    for t in trimestres_2024:
        # Contar evaluaciones
        evaluaciones = EvaluacionEntregable.objects.filter(trimestre=t)
        eval_count = evaluaciones.count()
        
        # Contar calificaciones
        cal_count = Calificacion.objects.filter(
            content_type=entregable_ct,
            object_id__in=evaluaciones.values_list('id', flat=True)
        ).count()
        
        total_general += cal_count
        
        print(f"Trimestre {t.id} ({t.nombre}):")
        print(f"- Evaluaciones: {eval_count}")
        print(f"- Calificaciones: {cal_count}")
    
    print(f"\n📝 RESUMEN:")
    print(f"- Total evaluaciones 2024: {EvaluacionEntregable.objects.filter(trimestre__in=trimestres_2024).count()}")
    print(f"- Total calificaciones 2024: {total_general}")
    
    if total_general == 0:
        print("\n⚠️ No hay calificaciones para eliminar. Operación cancelada.")
        return
    
    # Solicitar confirmación
    print("\n⚠️  ADVERTENCIA ⚠️")
    print("=================")
    print("Esta operación eliminará TODAS las calificaciones del año 2024.")
    print("Esta acción es IRREVERSIBLE y podría afectar a la funcionalidad del sistema.")
    print("Se recomienda hacer una copia de seguridad antes de continuar.")
    
    confirmacion = input("\nEscribe 'ELIMINAR CALIFICACIONES 2024' para confirmar: ")
    
    if confirmacion != "ELIMINAR CALIFICACIONES 2024":
        print("\n❌ Operación cancelada por el usuario.")
        return
    
    # Registrar hora de inicio
    hora_inicio = datetime.now()
    print(f"\n⏳ Iniciando eliminación a las {hora_inicio.strftime('%H:%M:%S')}...")
    inicio = time.time()
    
    try:
        with transaction.atomic():
            eliminadas_total = 0
            for t in trimestres_2024:
                print(f"\n🔄 Procesando {t.nombre}...")
                
                # Obtener IDs de evaluaciones para este trimestre
                eval_ids = EvaluacionEntregable.objects.filter(
                    trimestre=t
                ).values_list('id', flat=True)
                
                # Eliminar calificaciones para estas evaluaciones
                eliminadas = Calificacion.objects.filter(
                    content_type=entregable_ct,
                    object_id__in=eval_ids
                ).delete()[0]
                
                eliminadas_total += eliminadas
                print(f"✓ {eliminadas:,} calificaciones eliminadas")
            
            tiempo_total = time.time() - inicio
            print(f"\n✅ ELIMINACIÓN COMPLETADA")
            print("=======================")
            print(f"📊 Total eliminadas: {eliminadas_total:,} calificaciones")
            print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
            print(f"🚀 Velocidad: {eliminadas_total/tiempo_total:.2f} registros/segundo")
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA ELIMINACIÓN")
        print(f"Error: {str(e)}")
        print("❌ No se eliminaron calificaciones debido al error.")
        
    # Verificación final
    cal_restantes = Calificacion.objects.filter(
        content_type=entregable_ct,
        object_id__in=EvaluacionEntregable.objects.filter(
            trimestre__in=trimestres_2024
        ).values_list('id', flat=True)
    ).count()
    
    print(f"\n🔍 Verificación final: {cal_restantes:,} calificaciones restantes para 2024")
    
    # Siguiente paso
    print("\n🔄 PRÓXIMOS PASOS:")
    print("----------------")
    print("1. Ejecutar el script de importación de calificaciones con las correcciones necesarias")
    print("2. Verificar que las calificaciones se hayan importado correctamente")
    print("3. Asegurarse de que las evaluaciones ahora muestren las calificaciones correctas")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
    finally:
        print("\n📌 Fin del script")