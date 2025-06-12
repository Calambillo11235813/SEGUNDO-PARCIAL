from django.urls import path
from machine_learning.controllers import machine_learning_controllers

app_name = 'machine_learning'

urlpatterns = [
    # Gestión de datasets
    path('datasets/', machine_learning_controllers.obtener_datasets, name='obtener_datasets'),
    path('datasets/crear/', machine_learning_controllers.crear_dataset, name='crear_dataset'),
    
    # Entrenamiento de modelos
    path('modelos/', machine_learning_controllers.obtener_modelos, name='obtener_modelos'),
    path('modelos/entrenar/<uuid:dataset_id>/', machine_learning_controllers.entrenar_modelos, name='entrenar_modelos'),
    path('modelos/<uuid:modelo_id>/estadisticas/', machine_learning_controllers.estadisticas_modelo, name='estadisticas_modelo'),
    
    # Predicciones
    path('predecir/', machine_learning_controllers.predecir_rendimiento, name='predecir_rendimiento'),
    path('predicciones/<str:estudiante_codigo>/', machine_learning_controllers.historial_predicciones, name='historial_predicciones'),
]