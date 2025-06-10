# Importar las listas de patrones desde cada archivo
from .urls_curso import urlpatterns as curso_urls
from .urls_materia import urlpatterns as materia_urls
from .urls_evaluacion import urlpatterns as evaluacion_urls
from .urls_config_evaluacion_controller import urlpatterns as config_evaluacion_urls
from .urls_estudiante import urlpatterns as estudiante_urls
from .urls_trimestre import urlpatterns as trimestre_urls
from .urls_asistencia import urlpatterns as asistencia_urls
from .urls_calificacion import urlpatterns as calificacion_urls
from .urls_nivel import urlpatterns as nivel_urls
from .urls_tutor import urlpatterns as tutor_urls   


# Combinar todos los patrones
urlpatterns = []
urlpatterns.extend(curso_urls)
urlpatterns.extend(materia_urls)
urlpatterns.extend(evaluacion_urls)
urlpatterns.extend(estudiante_urls)
urlpatterns.extend(trimestre_urls)
urlpatterns.extend(asistencia_urls)
urlpatterns.extend(calificacion_urls)
urlpatterns.extend(nivel_urls)
urlpatterns.extend(config_evaluacion_urls)
urlpatterns.extend(tutor_urls)