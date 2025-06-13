import os
import django
import sys
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import (
    EvaluacionEntregable, 
    EvaluacionParticipacion, 
    Calificacion,
    PromedioTrimestral,
    PromedioAnual
)

def mostrar_estadisticas_antes():
    """Muestra estadísticas antes de la eliminación"""
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS ANTES DE LA ELIMINACIÓN")
    print("="*60)
    
    # Contar evaluaciones
    eval_entregables = EvaluacionEntregable.objects.count()
    eval_participacion = EvaluacionParticipacion.objects.count()
    total_evaluaciones = eval_entregables + eval_participacion
    
    # Contar calificaciones
    total_calificaciones = Calificacion.objects.count()
    
    # Contar promedios
    promedios_trimestrales = PromedioTrimestral.objects.count()
    promedios_anuales = PromedioAnual.objects.count()
    
    print(f"📝 Evaluaciones Entregables: {eval_entregables:,}")
    print(f"💬 Evaluaciones de Participación: {eval_participacion:,}")
    print(f"📊 Total de Evaluaciones: {total_evaluaciones:,}")
    print(f"🎯 Total de Calificaciones: {total_calificaciones:,}")
    print(f"📈 Promedios Trimestrales: {promedios_trimestrales:,}")
    print(f"📊 Promedios Anuales: {promedios_anuales:,}")
    print("="*60)

def eliminar_todo():
    """
    Elimina TODAS las evaluaciones, calificaciones y promedios del sistema.
    ⚠️ OPERACIÓN IRREVERSIBLE ⚠️
    """
    try:
        with transaction.atomic():
            print("\n🗑️ Iniciando eliminación completa...")
            
            # Obtener conteos antes de eliminar
            eval_entregables = EvaluacionEntregable.objects.count()
            eval_participacion = EvaluacionParticipacion.objects.count()
            total_calificaciones = Calificacion.objects.count()
            promedios_trimestrales = PromedioTrimestral.objects.count()
            promedios_anuales = PromedioAnual.objects.count()
            
            # Eliminar en orden para evitar problemas de FK
            print("1️⃣ Eliminando Promedios Anuales...")
            PromedioAnual.objects.all().delete()
            
            print("2️⃣ Eliminando Promedios Trimestrales...")
            PromedioTrimestral.objects.all().delete()
            
            print("3️⃣ Eliminando Calificaciones...")
            Calificacion.objects.all().delete()
            
            print("4️⃣ Eliminando Evaluaciones de Participación...")
            EvaluacionParticipacion.objects.all().delete()
            
            print("5️⃣ Eliminando Evaluaciones Entregables...")
            EvaluacionEntregable.objects.all().delete()
            
            # Verificar eliminación
            eval_entregables_despues = EvaluacionEntregable.objects.count()
            eval_participacion_despues = EvaluacionParticipacion.objects.count()
            total_calificaciones_despues = Calificacion.objects.count()
            promedios_trimestrales_despues = PromedioTrimestral.objects.count()
            promedios_anuales_despues = PromedioAnual.objects.count()
            
            print("\n" + "="*60)
            print("✅ RESUMEN DE ELIMINACIÓN COMPLETADA")
            print("="*60)
            print(f"📝 Evaluaciones Entregables eliminadas: {eval_entregables:,}")
            print(f"💬 Evaluaciones de Participación eliminadas: {eval_participacion:,}")
            print(f"🎯 Calificaciones eliminadas: {total_calificaciones:,}")
            print(f"📈 Promedios Trimestrales eliminados: {promedios_trimestrales:,}")
            print(f"📊 Promedios Anuales eliminados: {promedios_anuales:,}")
            print("\n📊 VERIFICACIÓN FINAL:")
            print(f"   Evaluaciones Entregables restantes: {eval_entregables_despues}")
            print(f"   Evaluaciones Participación restantes: {eval_participacion_despues}")
            print(f"   Calificaciones restantes: {total_calificaciones_despues}")
            print(f"   Promedios Trimestrales restantes: {promedios_trimestrales_despues}")
            print(f"   Promedios Anuales restantes: {promedios_anuales_despues}")
            print("="*60)
            
            total_eliminado = (eval_entregables + eval_participacion + 
                             total_calificaciones + promedios_trimestrales + promedios_anuales)
            print(f"🎯 TOTAL DE REGISTROS ELIMINADOS: {total_eliminado:,}")
            print("✅ Operación completada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error al eliminar datos: {str(e)}")
        print("❌ La transacción ha sido revertida.")

def eliminar_solo_calificaciones():
    """
    Elimina solo las calificaciones, manteniendo las evaluaciones.
    """
    try:
        with transaction.atomic():
            total_calificaciones = Calificacion.objects.count()
            promedios_trimestrales = PromedioTrimestral.objects.count()
            promedios_anuales = PromedioAnual.objects.count()
            
            print("\n🗑️ Eliminando solo calificaciones y promedios...")
            
            PromedioAnual.objects.all().delete()
            PromedioTrimestral.objects.all().delete()
            Calificacion.objects.all().delete()
            
            print(f"✅ Eliminadas {total_calificaciones:,} calificaciones")
            print(f"✅ Eliminados {promedios_trimestrales:,} promedios trimestrales")
            print(f"✅ Eliminados {promedios_anuales:,} promedios anuales")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal con menú de opciones"""
    print("\n" + "🚨"*20)
    print("⚠️  SCRIPT DE ELIMINACIÓN MASIVA  ⚠️")
    print("🚨"*20)
    print("⚠️ ESTA OPERACIÓN ES IRREVERSIBLE ⚠️")
    print("⚠️ HAGA BACKUP ANTES DE CONTINUAR ⚠️")
    
    # Mostrar estadísticas actuales
    mostrar_estadisticas_antes()
    
    print("\n🔧 OPCIONES DISPONIBLES:")
    print("1️⃣ Eliminar TODO (evaluaciones + calificaciones + promedios)")
    print("2️⃣ Eliminar solo calificaciones y promedios (mantener evaluaciones)")
    print("3️⃣ Mostrar estadísticas y salir")
    print("0️⃣ Cancelar y salir")
    
    opcion = input("\n➡️ Selecciona una opción (0-3): ").strip()
    
    if opcion == "1":
        print("\n⚠️ VAS A ELIMINAR TODO EL SISTEMA DE EVALUACIONES ⚠️")
        confirmacion = input("Escribe 'ELIMINAR TODO' para confirmar: ").strip()
        if confirmacion == "ELIMINAR TODO":
            eliminar_todo()
        else:
            print("❌ Confirmación incorrecta. Operación cancelada.")
            
    elif opcion == "2":
        print("\n⚠️ VAS A ELIMINAR TODAS LAS CALIFICACIONES Y PROMEDIOS ⚠️")
        confirmacion = input("Escribe 'ELIMINAR CALIFICACIONES' para confirmar: ").strip()
        if confirmacion == "ELIMINAR CALIFICACIONES":
            eliminar_solo_calificaciones()
        else:
            print("❌ Confirmación incorrecta. Operación cancelada.")
            
    elif opcion == "3":
        print("📊 Estadísticas mostradas arriba.")
        
    elif opcion == "0":
        print("✅ Operación cancelada por el usuario.")
        
    else:
        print("❌ Opción inválida.")

if __name__ == '__main__':
    main()