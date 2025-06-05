from django.urls import path
from ..controllers import evaluaciones_controllers

urlpatterns = [
    # URLs para gestión de Tipos de Evaluación
    path('tipos-evaluacion/create/', evaluaciones_controllers.create_tipo_evaluacion, name='create_tipo_evaluacion'),
    path('tipos-evaluacion/<int:tipo_id>/', evaluaciones_controllers.get_tipo_evaluacion, name='get_tipo_evaluacion'),
    path('tipos-evaluacion/<int:tipo_id>/update/', evaluaciones_controllers.update_tipo_evaluacion, name='update_tipo_evaluacion'),
    path('tipos-evaluacion/<int:tipo_id>/delete/', evaluaciones_controllers.delete_tipo_evaluacion, name='delete_tipo_evaluacion'),
    path('tipos-evaluacion/', evaluaciones_controllers.get_tipos_evaluacion, name='get_tipos_evaluacion'),
    
    # URLs para Evaluaciones
    path('evaluaciones/create/', evaluaciones_controllers.create_evaluacion, name='create_evaluacion'),
    path('evaluaciones/<int:evaluacion_id>/', evaluaciones_controllers.get_evaluacion, name='get_evaluacion'),
    path('evaluaciones/<int:evaluacion_id>/update/', evaluaciones_controllers.update_evaluacion, name='update_evaluacion'),
    path('evaluaciones/<int:evaluacion_id>/delete/', evaluaciones_controllers.delete_evaluacion, name='delete_evaluacion'),
    path('materias/<int:materia_id>/evaluaciones/', evaluaciones_controllers.get_evaluaciones_por_materia, name='get_evaluaciones_por_materia'),
]