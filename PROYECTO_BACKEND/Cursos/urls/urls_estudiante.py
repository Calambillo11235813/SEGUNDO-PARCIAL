from django.urls import path
from ..controllers import calificaciones_controllers, estudiante_controllers

urlpatterns = [
    # URLs para calificaciones de estudiantes
    path('estudiantes/<int:estudiante_id>/calificaciones/', calificaciones_controllers.get_calificaciones_por_estudiante, name='get_calificaciones_por_estudiante'),
    
    # URLs para el controlador de estudiantes
    path('estudiante/materias/', estudiante_controllers.obtener_materias_estudiante, name='obtener_materias_estudiante'),
    
    path('estudiantes/<int:estudiante_id>/curso-materias/', estudiante_controllers.obtener_estudiante_curso_materias, name='obtener_estudiante_curso_materias'),
    
    path('estudiantes/<int:estudiante_id>/evaluaciones/', estudiante_controllers.obtener_evaluaciones_estudiante, name='obtener_evaluaciones_estudiante'),
    
    path('estudiantes/<int:estudiante_id>/asistencias/', estudiante_controllers.obtener_asistencias_estudiante, name='obtener_asistencias_estudiante'),
    
    # Nueva URL para obtener trimestres de un estudiante específico
    path('estudiantes/<int:estudiante_id>/trimestres/', estudiante_controllers.obtener_trimestres_estudiante, name='obtener_trimestres_estudiante'),

    # Nueva URL para obtener calificaciones de un trimestre específico de un estudiante
    path('estudiantes/<int:estudiante_id>/trimestres/<int:trimestre_id>/calificaciones/', 
         estudiante_controllers.obtener_calificaciones_trimestre, 
         name='obtener_calificaciones_trimestre'),
]