from django.urls import path
from ..controllers import nivel_controllers

urlpatterns = [
    # Rutas para niveles
    path('niveles/', nivel_controllers.get_niveles, name='get_niveles'),
    path('niveles/<int:id>/', nivel_controllers.get_nivel, name='get_nivel'),
    path('niveles/create/', nivel_controllers.create_nivel, name='create_nivel'),
]