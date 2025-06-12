from django.db import models
from django.contrib.auth.models import User
from Cursos.models import Trimestre, Materia
from Usuarios.models import Usuario  # ✅ IMPORTACIÓN CORRECTA
import uuid

class DatasetAcademico(models.Model):
    """Modelo para almacenar datasets procesados para ML"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    total_registros = models.IntegerField(default=0)
    año_inicio = models.IntegerField()
    año_fin = models.IntegerField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ml_dataset_academico'
        verbose_name = 'Dataset Académico'
        verbose_name_plural = 'Datasets Académicos'

    def __str__(self):
        return f"{self.nombre} ({self.año_inicio}-{self.año_fin})"

class RegistroEstudianteML(models.Model):
    """Registro individual de estudiante para entrenamiento ML"""
    dataset = models.ForeignKey(DatasetAcademico, on_delete=models.CASCADE, related_name='registros')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros_ml')  # ✅ CORREGIDO
    trimestre = models.ForeignKey(Trimestre, on_delete=models.CASCADE, related_name='registros_ml')
    
    # Features de entrada
    promedio_notas_anterior = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_asistencia = models.DecimalField(max_digits=5, decimal_places=2)
    promedio_participaciones = models.DecimalField(max_digits=5, decimal_places=2)
    materias_cursadas = models.IntegerField()
    evaluaciones_completadas = models.IntegerField()
    
    # Target variable
    rendimiento_futuro = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ml_registro_estudiante'
        verbose_name = 'Registro Estudiante ML'
        verbose_name_plural = 'Registros Estudiantes ML'
        unique_together = ['estudiante', 'trimestre', 'dataset']

    def __str__(self):
        return f"{self.estudiante.get_full_name()} - {self.trimestre} - Dataset: {self.dataset.nombre}"

class ModeloML(models.Model):
    """Metadatos de modelos de ML entrenados"""
    ALGORITMOS = [
        ('RANDOM_FOREST', 'Random Forest'),
        ('LINEAR_REGRESSION', 'Regresión Lineal'),
        ('GRADIENT_BOOSTING', 'Gradient Boosting'),
        ('NEURAL_NETWORK', 'Red Neuronal')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    algoritmo = models.CharField(max_length=50, choices=ALGORITMOS)
    dataset = models.ForeignKey(DatasetAcademico, on_delete=models.CASCADE, related_name='modelos')
    
    # Métricas de rendimiento
    mae_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    mse_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    r2_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Metadatos del modelo
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    archivo_modelo = models.CharField(max_length=500)  # Path al archivo del modelo
    activo = models.BooleanField(default=True)
    
    # Audit fields
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='modelos_creados')
    
    class Meta:
        db_table = 'ml_modelo'
        verbose_name = 'Modelo ML'
        verbose_name_plural = 'Modelos ML'
        ordering = ['-fecha_entrenamiento']

    def __str__(self):
        return f"{self.nombre} ({self.algoritmo}) - R²: {self.r2_score or 'N/A'}"

    @property
    def precision_porcentaje(self):
        """Convierte R² a porcentaje de precisión"""
        if self.r2_score:
            return round(float(self.r2_score) * 100, 2)
        return 0

class PrediccionAcademica(models.Model):
    """Predicciones realizadas por el sistema"""
    NIVELES_RENDIMIENTO = [
        ('BAJO', 'Bajo (0-60)'),
        ('MEDIO', 'Medio (60-80)'),
        ('ALTO', 'Alto (80-100)')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='predicciones_ml')  # ✅ CORREGIDO
    modelo = models.ForeignKey(ModeloML, on_delete=models.CASCADE, related_name='predicciones')
    
    # Datos de entrada utilizados para la predicción
    promedio_notas_anterior = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_asistencia = models.DecimalField(max_digits=5, decimal_places=2)
    promedio_participaciones = models.DecimalField(max_digits=5, decimal_places=2)
    materias_cursadas = models.IntegerField()
    evaluaciones_completadas = models.IntegerField()
    
    # Resultados de predicción
    prediccion_numerica = models.DecimalField(max_digits=5, decimal_places=2)
    nivel_rendimiento = models.CharField(max_length=10, choices=NIVELES_RENDIMIENTO)
    confianza = models.DecimalField(max_digits=5, decimal_places=4)
    
    # Metadatos
    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    realizada_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='predicciones_realizadas')
    
    # Para validación posterior
    rendimiento_real = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Rendimiento real para validar la predicción")
    validada = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ml_prediccion'
        verbose_name = 'Predicción Académica'
        verbose_name_plural = 'Predicciones Académicas'
        ordering = ['-fecha_prediccion']

    def __str__(self):
        return f"Predicción: {self.estudiante.get_full_name()} - {self.prediccion_numerica} ({self.nivel_rendimiento})"

    @property
    def precision_porcentaje(self):
        """Convierte confianza a porcentaje"""
        return round(float(self.confianza) * 100, 2)

    @property
    def color_nivel(self):
        """Retorna color CSS según el nivel de rendimiento"""
        colores = {
            'BAJO': '#dc3545',    # Rojo
            'MEDIO': '#ffc107',   # Amarillo
            'ALTO': '#28a745'     # Verde
        }
        return colores.get(self.nivel_rendimiento, '#6c757d')

class MetricasModelo(models.Model):
    """Métricas adicionales y estadísticas de uso de los modelos"""
    modelo = models.OneToOneField(ModeloML, on_delete=models.CASCADE, related_name='metricas_detalladas')
    
    # Métricas de validación cruzada
    mae_cv_mean = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    mae_cv_std = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    r2_cv_mean = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    r2_cv_std = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Estadísticas de uso
    total_predicciones = models.IntegerField(default=0)
    total_validaciones = models.IntegerField(default=0)
    precision_real = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Precisión basada en validaciones reales")
    
    # Distribución de predicciones
    predicciones_bajo = models.IntegerField(default=0)
    predicciones_medio = models.IntegerField(default=0)
    predicciones_alto = models.IntegerField(default=0)
    
    # Metadatos
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ml_metricas_modelo'
        verbose_name = 'Métricas del Modelo'
        verbose_name_plural = 'Métricas de los Modelos'

    def __str__(self):
        return f"Métricas: {self.modelo.nombre}"

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas basadas en las predicciones realizadas"""
        predicciones = self.modelo.predicciones.all()
        
        self.total_predicciones = predicciones.count()
        self.predicciones_bajo = predicciones.filter(nivel_rendimiento='BAJO').count()
        self.predicciones_medio = predicciones.filter(nivel_rendimiento='MEDIO').count()
        self.predicciones_alto = predicciones.filter(nivel_rendimiento='ALTO').count()
        
        # Calcular precisión real si hay validaciones
        validaciones = predicciones.filter(validada=True, rendimiento_real__isnull=False)
        if validaciones.exists():
            self.total_validaciones = validaciones.count()
            # Aquí podrías implementar el cálculo de precisión real
            # comparando prediccion_numerica con rendimiento_real
        
        self.save()

class ResultadoEntrenamiento(models.Model):
    """Registro de resultados de entrenamiento de modelos"""
    
    modelo = models.ForeignKey(
        ModeloML, 
        on_delete=models.CASCADE,
        related_name='resultados_entrenamiento'
    )
    
    dataset = models.ForeignKey(
        DatasetAcademico,
        on_delete=models.CASCADE,
        related_name='resultados_entrenamiento'
    )
    
    precision = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        help_text="Precisión del modelo (R² score)"
    )
    
    error_promedio = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        help_text="Error promedio absoluto (MAE)"
    )
    
    metricas_detalladas = models.JSONField(
        default=dict,
        help_text="Métricas detalladas del entrenamiento"
    )
    
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'ml_resultado_entrenamiento'
        ordering = ['-fecha_entrenamiento']
        verbose_name = 'Resultado de Entrenamiento'
        verbose_name_plural = 'Resultados de Entrenamiento'
    
    def __str__(self):
        return f"Resultado {self.modelo.tipo_modelo} - Precisión: {self.precision}"
    
    @property
    def precision_porcentaje(self):
        """Precisión como porcentaje"""
        return float(self.precision) * 100
    
    @property
    def calidad_modelo(self):
        """Evaluación cualitativa del modelo"""
        precision = float(self.precision)
        if precision >= 0.8:
            return "Excelente"
        elif precision >= 0.6:
            return "Bueno"
        elif precision >= 0.4:
            return "Regular"
        else:
            return "Malo"