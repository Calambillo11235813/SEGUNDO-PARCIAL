import os
import sys
import django
from django.db.models import Count, Avg, Min, Max, F, Q
from datetime import datetime
from decimal import Decimal

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Importar modelos después de configurar Django
from Cursos.models import Calificacion, Materia, Trimestre, EvaluacionEntregable, EvaluacionParticipacion
from Usuarios.models import Usuario
from django.contrib.contenttypes.models import ContentType

def analizar_calificaciones():
    """
    Analiza todas las calificaciones guardadas en el sistema y muestra estadísticas.
    """
    print("\n======= ANÁLISIS DE CALIFICACIONES EN EL SISTEMA =======\n")
    
    # 1. Contar total de calificaciones
    total_calificaciones = Calificacion.objects.count()
    print(f"Total de calificaciones en el sistema: {total_calificaciones}")
    
    # 2. Calificaciones por tipo de evaluación
    content_type_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
    content_type_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
    
    calificaciones_entregables = Calificacion.objects.filter(content_type=content_type_entregable).count()
    calificaciones_participacion = Calificacion.objects.filter(content_type=content_type_participacion).count()
    
    print(f"Calificaciones de evaluaciones entregables: {calificaciones_entregables}")
    print(f"Calificaciones de participación: {calificaciones_participacion}")
    
    # 3. Estadísticas de notas
    if total_calificaciones > 0:
        stats = Calificacion.objects.aggregate(
            promedio=Avg('nota'),
            minima=Min('nota'),
            maxima=Max('nota')
        )
        
        print(f"\nEstadísticas de notas:")
        print(f"  - Nota promedio: {stats['promedio']:.2f}")
        print(f"  - Nota más baja: {stats['minima']:.2f}")
        print(f"  - Nota más alta: {stats['maxima']:.2f}")
    
        # 4. Calificaciones aprobadas vs reprobadas
        aprobadas = Calificacion.objects.filter(nota__gte=51.0).count()
        reprobadas = total_calificaciones - aprobadas
        
        print(f"\nCalificaciones aprobadas: {aprobadas} ({(aprobadas/total_calificaciones)*100:.2f}%)")
        print(f"Calificaciones reprobadas: {reprobadas} ({(reprobadas/total_calificaciones)*100:.2f}%)")
    
    # 5. Calificaciones por trimestre (top 5 trimestres)
    print("\nCalificaciones por trimestre (top 5):")
    calificaciones_por_trimestre = []
    
    # Para evaluaciones entregables
    entregables = Calificacion.objects.filter(
        content_type=content_type_entregable
    ).select_related('content_type')
    
    for calificacion in entregables:
        try:
            evaluacion = EvaluacionEntregable.objects.get(id=calificacion.object_id)
            if evaluacion.trimestre:
                calificaciones_por_trimestre.append(evaluacion.trimestre.id)
        except EvaluacionEntregable.DoesNotExist:
            pass
    
    # Para evaluaciones de participación
    participaciones = Calificacion.objects.filter(
        content_type=content_type_participacion
    ).select_related('content_type')
    
    for calificacion in participaciones:
        try:
            evaluacion = EvaluacionParticipacion.objects.get(id=calificacion.object_id)
            if evaluacion.trimestre:
                calificaciones_por_trimestre.append(evaluacion.trimestre.id)
        except EvaluacionParticipacion.DoesNotExist:
            pass
    
    # Contar frecuencia de cada trimestre
    from collections import Counter
    contador_trimestres = Counter(calificaciones_por_trimestre)
    top_trimestres = contador_trimestres.most_common(5)
    
    for trimestre_id, cantidad in top_trimestres:
        try:
            trimestre = Trimestre.objects.get(id=trimestre_id)
            print(f"  - {trimestre.nombre} ({trimestre.año_academico}): {cantidad} calificaciones")
        except Trimestre.DoesNotExist:
            print(f"  - Trimestre ID {trimestre_id}: {cantidad} calificaciones")
    
    # 6. Calificaciones por estudiante (top 10 estudiantes con más evaluaciones)
    print("\nEstudiantes con más calificaciones (top 10):")
    estudiantes_top = Calificacion.objects.values(
        'estudiante'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    for i, est in enumerate(estudiantes_top, 1):
        try:
            estudiante = Usuario.objects.get(id=est['estudiante'])
            print(f"  {i}. {estudiante.get_full_name()}: {est['total']} calificaciones")
        except Usuario.DoesNotExist:
            print(f"  {i}. Estudiante ID {est['estudiante']}: {est['total']} calificaciones")
    
    # 7. Calificaciones por año
    print("\nCalificaciones por año:")
    años = Calificacion.objects.extra(
        select={'año': "EXTRACT(YEAR FROM fecha_calificacion)"}
    ).values('año').annotate(total=Count('id')).order_by('año')
    
    for año_data in años:
        año = año_data['año']
        if año:  # Puede ser None si fecha_calificacion es NULL
            print(f"  - {int(año)}: {año_data['total']} calificaciones")
    
    # 8. Calificaciones con entregas tardías
    entregas_tardias = Calificacion.objects.filter(entrega_tardia=True).count()
    if total_calificaciones > 0:
        print(f"\nEntregas tardías: {entregas_tardias} ({(entregas_tardias/total_calificaciones)*100:.2f}%)")
    
    print("\n========================================================")

def eliminar_todas_calificaciones():
    """
    Elimina todas las calificaciones de la base de datos.
    Solicita confirmación al usuario antes de proceder.
    """
    total = Calificacion.objects.count()
    
    if total == 0:
        print("No hay calificaciones para eliminar en la base de datos.")
        return
    
    print(f"\n¡ADVERTENCIA! Vas a eliminar {total} calificaciones de la base de datos.")
    print("Esta acción NO SE PUEDE DESHACER.")
    
    confirmacion = input("\n¿Estás seguro de que deseas eliminar TODAS las calificaciones? (escribe 'SI' para confirmar): ")
    
    if confirmacion.upper() == 'SI':
        try:
            Calificacion.objects.all().delete()
            print(f"\n✓ Se han eliminado exitosamente {total} calificaciones de la base de datos.")
        except Exception as e:
            print(f"\n✗ Error al eliminar las calificaciones: {str(e)}")
    else:
        print("\nOperación cancelada. No se eliminó ninguna calificación.")

if __name__ == "__main__":
    # Mostrar menú
    print("\n=== SISTEMA DE GESTIÓN DE CALIFICACIONES ===")
    print("1. Analizar calificaciones")
    print("2. Eliminar todas las calificaciones")
    print("0. Salir")
    
    opcion = input("\nSelecciona una opción: ")
    
    if opcion == "1":
        analizar_calificaciones()
    elif opcion == "2":
        eliminar_todas_calificaciones()
    else:
        print("Saliendo...")