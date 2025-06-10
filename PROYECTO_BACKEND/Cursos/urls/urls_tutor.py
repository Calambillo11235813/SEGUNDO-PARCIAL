from django.urls import path
from ..controllers import tutor_controllers

urlpatterns = [
    path('tutores/<int:tutor_id>/estudiantes/', 
         tutor_controllers.obtener_estudiantes_tutor, 
         name='obtener_estudiantes_tutor'),
    
    path('tutores/<int:tutor_id>/calificaciones/', 
         tutor_controllers.obtener_calificaciones_estudiantes, 
         name='obtener_calificaciones_estudiantes'),
    
    path('tutores/<int:tutor_id>/estudiantes/<int:estudiante_id>/calificaciones/', 
         tutor_controllers.obtener_calificaciones_estudiante_detalle, 
         name='obtener_calificaciones_estudiante_detalle'),

    path('tutores/<int:tutor_id>/asignar-estudiantes/',
         tutor_controllers.asignar_estudiantes_tutor, 
         name='asignar_estudiantes_tutor'),
]