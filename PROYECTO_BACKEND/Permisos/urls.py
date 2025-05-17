from django.urls import path
from .controllers import rol_controllers

urlpatterns = [
    path('roles/', rol_controllers.get_roles, name='get_roles'),
    path('roles/<int:id>/', rol_controllers.get_rol, name='get_rol'),
    path('roles/create/', rol_controllers.create_rol, name='create_rol'),
    path('roles/update/<int:id>/', rol_controllers.update_rol, name='update_rol'),
    path('roles/delete/<int:id>/', rol_controllers.delete_rol, name='delete_rol'),
]