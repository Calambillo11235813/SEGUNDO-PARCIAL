from django.urls import path
from ..controllers import trimestre_controllers

urlpatterns = [
    # URLs para Trimestres
    path('trimestres/', trimestre_controllers.get_trimestres, name='get_trimestres'),
    path('trimestres/create/', trimestre_controllers.create_trimestre, name='create_trimestre'),
    path('trimestres/<int:trimestre_id>/', trimestre_controllers.update_trimestre, name='update_trimestre'),
    
    # Cálculo de promedios
    path('trimestres/<int:trimestre_id>/calcular-promedios/', trimestre_controllers.calcular_promedios_trimestre, name='calcular_promedios_trimestre'),
    path('años/<int:año_academico>/calcular-promedios-anuales/', trimestre_controllers.calcular_promedios_anuales, name='calcular_promedios_anuales'),
    
    # Reportes
    path('trimestres/<int:trimestre_id>/reporte/', trimestre_controllers.get_reporte_trimestral, name='get_reporte_trimestral'),
    path('años/<int:año_academico>/reporte-anual-comparativo/', trimestre_controllers.get_reporte_anual_comparativo, name='get_reporte_anual_comparativo'),
]