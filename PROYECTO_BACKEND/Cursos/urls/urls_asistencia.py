from django.urls import path
from ..controllers import asistencia_controllers

urlpatterns = [
    # Rutas para asistencias
    path('asistencias/registrar/', asistencia_controllers.registrar_asistencia, name='registrar_asistencia'),
    path('asistencias/registrar-masivo/', asistencia_controllers.registrar_asistencias_masivo, name='registrar_asistencias_masivo'),
    path('materias/<int:materia_id>/asistencias/', asistencia_controllers.get_asistencias_por_materia, name='get_asistencias_por_materia'),
    path('materias/<int:materia_id>/estudiantes/', asistencia_controllers.get_estudiantes_por_materia, name='get_estudiantes_por_materia'),
]