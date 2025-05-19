from django.urls import path
from .controllers import auth_controllers, usuario_controllers
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Rutas de autenticación
    path('auth/register/', auth_controllers.register, name='register'),
    path('auth/login/', auth_controllers.login, name='login'),
    path('auth/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas de gestión de usuarios
    path('usuarios/', usuario_controllers.get_usuarios, name='get_usuarios'),
    path('usuarios/<int:id>/', usuario_controllers.get_usuario, name='get_usuario'),
    path('usuarios/<int:id>/update/', usuario_controllers.update_usuario, name='update_usuario'),
    path('usuarios/<int:id>/delete/', usuario_controllers.delete_usuario, name='delete_usuario'),
    path('usuarios/<int:usuario_id>/cambiar-rol/', usuario_controllers.update_rol_usuario, name='update_rol_usuario'),
]