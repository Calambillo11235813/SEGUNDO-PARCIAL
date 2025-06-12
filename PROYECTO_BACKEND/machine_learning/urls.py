from django.urls import path
from machine_learning.controllers import machine_learning_controllers as ml_controllers

app_name = 'machine_learning'

urlpatterns = [
    # Gestión de datasets
    path('crear-dataset/', ml_controllers.crear_dataset, name='crear_dataset'),
    path('datasets/', ml_controllers.obtener_datasets, name='obtener_datasets'),
    
    # Entrenamiento de modelos
    path('entrenar-modelos/<uuid:dataset_id>/', ml_controllers.entrenar_modelos, name='entrenar_modelos'),
    path('modelos/', ml_controllers.obtener_modelos, name='obtener_modelos'),
    path('modelo/<uuid:modelo_id>/estadisticas/', ml_controllers.estadisticas_modelo, name='estadisticas_modelo'),
    
    # Predicciones
    path('predecir/', ml_controllers.predecir_rendimiento, name='predecir_rendimiento'),
    path('predecir-multiple/', ml_controllers.predecir_rendimiento_multiple, name='predecir_multiple'),
    path('historial/<str:estudiante_codigo>/', ml_controllers.historial_predicciones, name='historial_predicciones'),
    
    # Estado del sistema
    path('estado/', ml_controllers.estado_sistema_ml, name='estado_sistema'),
]