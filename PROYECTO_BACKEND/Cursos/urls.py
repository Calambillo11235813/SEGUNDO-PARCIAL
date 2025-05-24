from django.urls import path
from .controllers import materia_controllers, curso_controllers, nivel_controllers

urlpatterns = [
    # Rutas para materias
    path('materias/', materia_controllers.get_materias, name='get_materias'),
    path('materias/<int:id>/', materia_controllers.get_materia, name='get_materia'),
    # Ruta para crear materias por curso
    path('materias/create-por-curso/', materia_controllers.create_materia_por_curso, 
         name='create_materia_por_curso'),
    
    path('materias/<int:id>/update/', materia_controllers.update_materia, name='update_materia'),
    path('materias/<int:id>/delete/', materia_controllers.delete_materia, name='delete_materia'),
    path('cursos/<int:curso_id>/materias/', materia_controllers.get_materias_por_curso, name='get_materias_por_curso'),
    
    # Ruta para obtener materias por curso
    path('materias/por-curso/', materia_controllers.get_materias_por_nivel_grado_paralelo, 
         name='get_materias_por_curso'),
    
 
    # Rutas para cursos
    path('cursos/', curso_controllers.get_cursos, name='get_cursos'),
    path('cursos/<int:id>/', curso_controllers.get_curso, name='get_curso'),
    path('cursos/create/', curso_controllers.create_curso, name='create_curso'),
    path('cursos/<int:id>/update/', curso_controllers.update_curso, name='update_curso'),
    path('cursos/<int:id>/delete/', curso_controllers.delete_curso, name='delete_curso'),
    path('niveles/<int:nivel_id>/cursos/', curso_controllers.get_cursos_por_nivel, name='get_cursos_por_nivel'),
    
    # Rutas para niveles
    path('niveles/', nivel_controllers.get_niveles, name='get_niveles'),
    path('niveles/<int:id>/', nivel_controllers.get_nivel, name='get_nivel'),
    path('niveles/create/', nivel_controllers.create_nivel, name='create_nivel'),
]