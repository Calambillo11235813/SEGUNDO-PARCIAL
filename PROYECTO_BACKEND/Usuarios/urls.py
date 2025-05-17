from django.urls import path
from .controllers import auth_controllers
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', auth_controllers.register, name='register'),
    path('auth/login/', auth_controllers.login, name='login'),
    path('auth/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
]