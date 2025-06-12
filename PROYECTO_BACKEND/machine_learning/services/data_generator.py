import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from decimal import Decimal
from machine_learning.models import DatasetAcademico, RegistroEstudianteML
from Usuarios.models import Usuario
from Cursos.models import Trimestre
import logging

logger = logging.getLogger(__name__)

class RealisticDataGeneratorFixed:
    """Generador de datos realistas CORREGIDO"""
    
    def __init__(self):
        self.random_state = 42
        np.random.seed(self.random_state)
        random.seed(self.random_state)
    
    def generar_dataset_realista(self, nombre="Dataset Realista ML", num_estudiantes=200, num_periodos=6):
        """Generar un dataset con patrones realistas de rendimiento académico"""
        
        logger.info(f"Generando dataset realista con {num_estudiantes} estudiantes y {num_periodos} períodos")
        
        # Crear dataset SIN campo 'estado'
        dataset = DatasetAcademico.objects.create(
            nombre=nombre,
            descripcion=f"Dataset generado con patrones realistas - {num_estudiantes} estudiantes",
            año_inicio=2023,
            año_fin=2024
            # Removido: estado='procesando'
        )
        
        registros_generados = []
        
        # Generar estudiantes con perfiles diferentes
        for estudiante_id in range(1, num_estudiantes + 1):
            perfil_estudiante = self._generar_perfil_estudiante()
            
            # Generar secuencia temporal de rendimiento
            for periodo in range(num_periodos):
                registro = self._generar_registro_periodo(
                    estudiante_id, periodo, perfil_estudiante, dataset
                )
                if registro:
                    registros_generados.append(registro)
        
        # Guardar en lotes
        RegistroEstudianteML.objects.bulk_create(registros_generados)
        
        # Actualizar dataset
        dataset.total_registros = len(registros_generados)
        dataset.save()
        
        logger.info(f"Dataset generado: {len(registros_generados)} registros")
        return dataset
    
    def _generar_perfil_estudiante(self):
        """Generar perfil de estudiante con características consistentes"""
        
        # Tipos de estudiantes con diferentes patrones
        tipo = np.random.choice(['excelente', 'bueno', 'promedio', 'variable', 'problemático'], 
                               p=[0.15, 0.25, 0.35, 0.15, 0.10])
        
        if tipo == 'excelente':
            base_rendimiento = np.random.uniform(85, 95)
            variabilidad = np.random.uniform(2, 5)
            tendencia = np.random.uniform(-0.5, 1.0)
            asistencia_base = np.random.uniform(90, 98)
            
        elif tipo == 'bueno':
            base_rendimiento = np.random.uniform(75, 85)
            variabilidad = np.random.uniform(3, 7)
            tendencia = np.random.uniform(-1.0, 1.5)
            asistencia_base = np.random.uniform(80, 92)
            
        elif tipo == 'promedio':
            base_rendimiento = np.random.uniform(60, 75)
            variabilidad = np.random.uniform(5, 10)
            tendencia = np.random.uniform(-1.5, 1.5)
            asistencia_base = np.random.uniform(70, 85)
            
        elif tipo == 'variable':
            base_rendimiento = np.random.uniform(50, 80)
            variabilidad = np.random.uniform(8, 15)
            tendencia = np.random.uniform(-2.0, 2.0)
            asistencia_base = np.random.uniform(60, 90)
            
        else:  # problemático
            base_rendimiento = np.random.uniform(40, 65)
            variabilidad = np.random.uniform(10, 20)
            tendencia = np.random.uniform(-2.0, 0.5)
            asistencia_base = np.random.uniform(45, 75)
        
        return {
            'tipo': tipo,
            'base_rendimiento': base_rendimiento,
            'variabilidad': variabilidad,
            'tendencia': tendencia,
            'asistencia_base': asistencia_base,
            'factores_externos': np.random.uniform(0.8, 1.2)
        }
    
    def _generar_registro_periodo(self, estudiante_id, periodo, perfil, dataset):
        """Generar un registro para un período específico"""
        
        # Obtener primer estudiante real para referencia
        try:
            estudiante = Usuario.objects.filter(is_active=True).first()
            if not estudiante:
                return None
        except:
            return None
        
        # Obtener trimestre
        try:
            trimestre = Trimestre.objects.filter(año_academico__in=[2023, 2024]).first()
            if not trimestre:
                return None
        except:
            return None
        
        # Calcular rendimiento actual con evolución temporal
        rendimiento_actual = self._calcular_rendimiento_periodo(perfil, periodo)
        
        # Calcular rendimiento futuro con factores realistas
        rendimiento_futuro = self._calcular_rendimiento_futuro(
            rendimiento_actual, perfil, periodo
        )
        
        # Generar asistencia correlacionada con rendimiento
        asistencia = self._calcular_asistencia(rendimiento_actual, perfil)
        
        # Calcular otras métricas
        participaciones = self._calcular_participaciones(rendimiento_actual, asistencia, perfil)
        materias_cursadas = np.random.randint(4, 8)
        evaluaciones_completadas = np.random.randint(8, 16)
        
        return RegistroEstudianteML(
            dataset=dataset,
            estudiante=estudiante,
            trimestre=trimestre,
            promedio_notas_anterior=Decimal(str(round(rendimiento_actual, 2))),
            porcentaje_asistencia=Decimal(str(round(asistencia, 2))),
            promedio_participaciones=Decimal(str(round(participaciones, 2))),
            materias_cursadas=materias_cursadas,
            evaluaciones_completadas=evaluaciones_completadas,
            rendimiento_futuro=Decimal(str(round(rendimiento_futuro, 2)))
        )
    
    def _calcular_rendimiento_periodo(self, perfil, periodo):
        """Calcular rendimiento actual considerando evolución temporal"""
        
        evolucion_temporal = perfil['tendencia'] * periodo
        ruido = np.random.normal(0, perfil['variabilidad'])
        factor_estacional = np.sin(periodo * np.pi / 3) * np.random.uniform(-2, 2)
        
        rendimiento = (
            perfil['base_rendimiento'] + 
            evolucion_temporal + 
            ruido + 
            factor_estacional
        )
        
        return np.clip(rendimiento, 0, 100)
    
    def _calcular_rendimiento_futuro(self, rendimiento_actual, perfil, periodo):
        """Calcular rendimiento futuro con factores predictivos realistas"""
        
        factor_persistencia = 0.7
        media_personal = perfil['base_rendimiento']
        factor_regresion = 0.15
        evento_aleatorio = np.random.normal(0, perfil['variabilidad'] * 0.8)
        factor_tendencia = perfil['tendencia'] * np.random.uniform(0.5, 1.5)
        asistencia_efecto = (self._calcular_asistencia(rendimiento_actual, perfil) - 75) * 0.1
        
        rendimiento_futuro = (
            rendimiento_actual * factor_persistencia +
            media_personal * factor_regresion +
            evento_aleatorio +
            factor_tendencia +
            asistencia_efecto +
            np.random.uniform(-3, 3)
        )
        
        return np.clip(rendimiento_futuro, 0, 100)
    
    def _calcular_asistencia(self, rendimiento, perfil):
        """Calcular asistencia correlacionada con rendimiento"""
        
        correlacion_base = 0.6
        
        asistencia = (
            perfil['asistencia_base'] +
            (rendimiento - perfil['base_rendimiento']) * correlacion_base * 0.3 +
            np.random.normal(0, 8)
        )
        
        return np.clip(asistencia, 0, 100)
    
    def _calcular_participaciones(self, rendimiento, asistencia, perfil):
        """Calcular participaciones basadas en rendimiento y asistencia"""
        
        participaciones = (
            rendimiento * 0.4 +
            asistencia * 0.3 +
            perfil['base_rendimiento'] * 0.2 +
            np.random.normal(0, 5)
        )
        
        return np.clip(participaciones, 0, 100)
    
    def generar_estadisticas_dataset(self, dataset):
        """Generar estadísticas del dataset creado"""
        
        registros = RegistroEstudianteML.objects.filter(dataset=dataset)
        
        if not registros.exists():
            return None
        
        data = []
        for r in registros:
            data.append({
                'promedio_anterior': float(r.promedio_notas_anterior),
                'rendimiento_futuro': float(r.rendimiento_futuro),
                'asistencia': float(r.porcentaje_asistencia),
                'participaciones': float(r.promedio_participaciones)
            })
        
        df = pd.DataFrame(data)
        
        stats = {
            'total_registros': len(df),
            'correlacion_rendimiento': df['promedio_anterior'].corr(df['rendimiento_futuro']),
            'diferencia_promedio': abs(df['rendimiento_futuro'].mean() - df['promedio_anterior'].mean()),
            'std_diferencia': (df['rendimiento_futuro'] - df['promedio_anterior']).std(),
            'rango_rendimiento': (df['promedio_anterior'].min(), df['promedio_anterior'].max()),
            'rango_futuro': (df['rendimiento_futuro'].min(), df['rendimiento_futuro'].max())
        }
        
        return stats

# Crear instancia del generador corregido
print("✅ GeneradorDataRealistaFixed creado")