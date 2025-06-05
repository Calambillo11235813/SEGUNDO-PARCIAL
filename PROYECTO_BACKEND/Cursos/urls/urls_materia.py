from django.urls import path
from ..controllers import materia_controllers

urlpatterns = [
    # Rutas para materias
    path('materias/', materia_controllers.get_materias, name='get_materias'),
    path('materias/<int:id>/', materia_controllers.get_materia, name='get_materia'),
    # Ruta para crear materias por curso solo el id
    path('materias/create-por-curso/', materia_controllers.create_materia_por_curso, 
         name='create_materia_por_curso'),
    path('materias/<int:id>/update/', materia_controllers.update_materia, name='update_materia'),
    path('materias/<int:id>/delete/', materia_controllers.delete_materia, name='delete_materia'),
    path('cursos/<int:curso_id>/materias/', materia_controllers.get_materias_por_curso, name='get_materias_por_curso'),

    # Rutas para asignar y desasignar profesores
    path('materias/<int:materia_id>/asignar-profesor/', materia_controllers.asignar_profesor, name='asignar_profesor'),
    path('materias/<int:materia_id>/desasignar-profesor/', materia_controllers.desasignar_profesor, name='desasignar_profesor'),
    path('profesores/<int:profesor_id>/materias/', materia_controllers.get_materias_por_profesor, name='get_materias_por_profesor'),
]