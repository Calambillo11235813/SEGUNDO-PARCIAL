import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from django.conf import settings
from machine_learning.models import ModeloML, RegistroEstudianteML  # Sin ResultadoEntrenamiento por ahora
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ModelTrainerServiceSimplificado:
    """Versión simplificada del servicio de entrenamiento"""
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.modelos_disponibles = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression(),
            'svr': SVR(kernel='rbf', C=1.0)
        }
        self.scaler = StandardScaler()
        
    def cargar_datos_entrenamiento(self):
        """Cargar datos del dataset para entrenamiento"""
        logger.info(f"Cargando datos del dataset: {self.dataset.nombre}")
        
        registros = RegistroEstudianteML.objects.filter(dataset=self.dataset)
        
        if not registros.exists():
            raise ValueError(f"No hay datos en el dataset {self.dataset.nombre}")
        
        # Convertir a DataFrame
        data = []
        for registro in registros:
            data.append({
                'promedio_notas_anterior': float(registro.promedio_notas_anterior),
                'porcentaje_asistencia': float(registro.porcentaje_asistencia),
                'promedio_participaciones': float(registro.promedio_participaciones),
                'materias_cursadas': registro.materias_cursadas,
                'evaluaciones_completadas': registro.evaluaciones_completadas,
                'rendimiento_futuro': float(registro.rendimiento_futuro)
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Datos cargados: {len(df)} registros con {len(df.columns)} columnas")
        
        return df
    
    def preparar_datos(self, df):
        """Preparar datos para entrenamiento"""
        logger.info("Preparando datos para entrenamiento...")
        
        # Separar features y target
        feature_columns = [
            'promedio_notas_anterior',
            'porcentaje_asistencia', 
            'promedio_participaciones',
            'materias_cursadas',
            'evaluaciones_completadas'
        ]
        
        X = df[feature_columns]
        y = df['rendimiento_futuro']
        
        # División en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Datos preparados: {len(X_train)} entrenamiento, {len(X_test)} prueba")
        
        return X_train_scaled, X_test_scaled, y_train, y_test, feature_columns
    
    def evaluar_modelo(self, modelo, X_test, y_test):
        """Evaluar rendimiento del modelo"""
        # Predicciones
        y_pred = modelo.predict(X_test)
        
        # Métricas
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Accuracy personalizado
        tolerancia = 10
        predicciones_aceptables = np.abs(y_pred - y_test) <= tolerancia
        accuracy_custom = np.mean(predicciones_aceptables) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'accuracy_custom': accuracy_custom
        }
    
    def entrenar_todos_los_modelos(self):
        """Entrenar y comparar todos los modelos"""
        logger.info("Iniciando entrenamiento simplificado...")
        
        # Cargar y preparar datos
        df = self.cargar_datos_entrenamiento()
        X_train, X_test, y_train, y_test, feature_columns = self.preparar_datos(df)
        
        resultados = {}
        
        for nombre, modelo in self.modelos_disponibles.items():
            try:
                logger.info(f"Entrenando: {nombre}")
                
                # Entrenar modelo
                modelo.fit(X_train, y_train)
                
                # Evaluar modelo
                metricas = self.evaluar_modelo(modelo, X_test, y_test)
                
                # Guardar resultados
                resultados[nombre] = {
                    'modelo': modelo,
                    'metricas': metricas
                }
                
                logger.info(f"{nombre} - R²: {metricas['r2']:.4f}, RMSE: {metricas['rmse']:.4f}")
                
            except Exception as e:
                logger.error(f"Error entrenando {nombre}: {str(e)}")
                continue
        
        # Seleccionar mejor modelo
        mejor_modelo = None
        if resultados:
            mejor_nombre = max(resultados.keys(), key=lambda x: resultados[x]['metricas']['r2'])
            mejor_modelo = {
                'nombre': mejor_nombre,
                'modelo': resultados[mejor_nombre]['modelo'],
                'metricas': resultados[mejor_nombre]['metricas'],
                'score_combinado': resultados[mejor_nombre]['metricas']['r2']
            }
        
        return resultados, mejor_modelo
    
    def predecir(self, modelo_entrenado, datos_estudiante):
        """Hacer predicción para un estudiante específico"""
        try:
            # Preparar datos de entrada
            features = [
                datos_estudiante['promedio_notas_anterior'],
                datos_estudiante['porcentaje_asistencia'],
                datos_estudiante['promedio_participaciones'],
                datos_estudiante['materias_cursadas'],
                datos_estudiante['evaluaciones_completadas']
            ]
            
            # Escalar features
            features_scaled = self.scaler.transform([features])
            
            # Hacer predicción
            prediccion = modelo_entrenado.predict(features_scaled)[0]
            
            return float(prediccion)
            
        except Exception as e:
            logger.error(f"Error en predicción: {str(e)}")
            return None