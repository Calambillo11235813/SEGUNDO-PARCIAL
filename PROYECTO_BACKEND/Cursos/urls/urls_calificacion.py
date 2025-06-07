from django.urls import path
from ..controllers import calificaciones_controllers

urlpatterns = [
    # URLs para Calificaciones
    path('calificaciones/registrar/', calificaciones_controllers.registrar_calificacion, name='registrar_calificacion'),
    path('calificaciones/registrar-masivo/', calificaciones_controllers.registrar_calificaciones_masivo, name='registrar_calificaciones_masivo'),
    path('evaluaciones/<int:evaluacion_id>/calificaciones/', calificaciones_controllers.get_calificaciones_por_evaluacion, name='get_calificaciones_por_evaluacion'),
    path('materias/<int:materia_id>/reporte-calificaciones/', calificaciones_controllers.get_reporte_calificaciones_materia, name='get_reporte_calificaciones_materia'),
    # Agregar esta nueva URL
    path('estudiantes/<int:estudiante_id>/calificaciones/', calificaciones_controllers.get_calificaciones_por_estudiante, name='get_calificaciones_por_estudiante'),
]