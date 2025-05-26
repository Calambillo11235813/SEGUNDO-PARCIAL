from django.urls import path
from .controllers import materia_controllers, curso_controllers, nivel_controllers, asistencia_controllers

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

    # Rutas para asignar y desasignar profesores
    path('materias/<int:materia_id>/asignar-profesor/', materia_controllers.asignar_profesor, name='asignar_profesor'),
    path('materias/<int:materia_id>/desasignar-profesor/', materia_controllers.desasignar_profesor, name='desasignar_profesor'),
    path('profesores/<int:profesor_id>/materias/', materia_controllers.get_materias_por_profesor, name='get_materias_por_profesor'),

    # Rutas para asistencias
    path('asistencias/registrar/', asistencia_controllers.registrar_asistencia, name='registrar_asistencia'),
    path('asistencias/registrar-masivo/', asistencia_controllers.registrar_asistencias_masivo, name='registrar_asistencias_masivo'),
    path('materias/<int:materia_id>/asistencias/', asistencia_controllers.get_asistencias_por_materia, name='get_asistencias_por_materia'),
    path('materias/<int:materia_id>/estudiantes/', asistencia_controllers.get_estudiantes_por_materia, name='get_estudiantes_por_materia'),

    # URLs para gestión de estudiantes en cursos
    path('cursos/asignar-estudiante/', curso_controllers.asignar_estudiante_a_curso, name='asignar_estudiante_a_curso'),
    path('cursos/<int:curso_id>/estudiantes/', curso_controllers.get_estudiantes_de_curso, name='get_estudiantes_de_curso'),
    path('estudiantes/<int:estudiante_id>/desasignar-curso/', curso_controllers.desasignar_estudiante_de_curso, name='desasignar_estudiante_de_curso'),
    path('estudiantes/sin-curso/', curso_controllers.get_estudiantes_sin_curso, name='get_estudiantes_sin_curso'),
]