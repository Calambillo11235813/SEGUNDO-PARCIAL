from django.urls import path
from .views import predecir_view

urlpatterns = [
    path('predecir/', predecir_view, name='predecir'),
]