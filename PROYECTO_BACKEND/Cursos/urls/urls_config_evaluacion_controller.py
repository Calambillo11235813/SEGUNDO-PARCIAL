from django.urls import path
from ..controllers import config_evaluacion_controller

urlpatterns = [

path('materias/<int:materia_id>/configuracion-evaluacion/', 
     config_evaluacion_controller.get_configuracion_evaluacion_materia, 
     name='get_configuracion_evaluacion_materia'),

path('configuracion-evaluacion/', 
     config_evaluacion_controller.create_configuracion_evaluacion, 
     name='create_configuracion_evaluacion'),

path('configuracion-evaluacion/<int:config_id>/', 
     config_evaluacion_controller.delete_configuracion_evaluacion, 
     name='delete_configuracion_evaluacion'),

]