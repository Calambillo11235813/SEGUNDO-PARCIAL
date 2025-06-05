from django.urls import path
from ..controllers import curso_controllers

urlpatterns = [
    # Rutas para cursos
    path('cursos/', curso_controllers.get_cursos, name='get_cursos'),
    path('cursos/<int:id>/', curso_controllers.get_curso, name='get_curso'),
    path('cursos/create/', curso_controllers.create_curso, name='create_curso'),
    path('cursos/<int:id>/update/', curso_controllers.update_curso, name='update_curso'),
    path('cursos/<int:id>/delete/', curso_controllers.delete_curso, name='delete_curso'),
    path('niveles/<int:nivel_id>/cursos/', curso_controllers.get_cursos_por_nivel, name='get_cursos_por_nivel'),
    
    # URLs para gestión de estudiantes en cursos
    path('cursos/asignar-estudiante/', curso_controllers.asignar_estudiante_a_curso, name='asignar_estudiante_a_curso'),
    path('cursos/<int:curso_id>/estudiantes/', curso_controllers.get_estudiantes_de_curso, name='get_estudiantes_de_curso'),
    path('estudiantes/<int:estudiante_id>/desasignar-curso/', curso_controllers.desasignar_estudiante_de_curso, name='desasignar_estudiante_de_curso'),
    path('estudiantes/sin-curso/', curso_controllers.get_estudiantes_sin_curso, name='get_estudiantes_sin_curso'),
]