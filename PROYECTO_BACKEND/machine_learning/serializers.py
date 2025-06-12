from rest_framework import serializers
from machine_learning.models import DatasetAcademico, ModeloML, PrediccionAcademica
from decimal import Decimal

class DatasetAcademicoSerializer(serializers.ModelSerializer):
    """Serializer para DatasetAcademico"""
    
    class Meta:
        model = DatasetAcademico
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_creacion', 
            'fecha_actualizacion', 'total_registros', 'año_inicio', 
            'año_fin', 'activo'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

class ModeloMLSerializer(serializers.ModelSerializer):
    """Serializer para ModeloML"""
    precision_porcentaje = serializers.ReadOnlyField()
    dataset_nombre = serializers.CharField(source='dataset.nombre', read_only=True)
    
    class Meta:
        model = ModeloML
        fields = [
            'id', 'nombre', 'algoritmo', 'dataset', 'dataset_nombre',
            'mae_score', 'mse_score', 'r2_score', 'precision_porcentaje',
            'fecha_entrenamiento', 'activo'
        ]
        read_only_fields = ['id', 'fecha_entrenamiento']

class PrediccionAcademicaSerializer(serializers.ModelSerializer):
    """Serializer para PrediccionAcademica"""
    estudiante_nombre = serializers.CharField(source='estudiante.get_full_name', read_only=True)
    estudiante_codigo = serializers.CharField(source='estudiante.codigo', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    precision_porcentaje = serializers.ReadOnlyField()
    color_nivel = serializers.ReadOnlyField()
    
    class Meta:
        model = PrediccionAcademica
        fields = [
            'id', 'estudiante', 'estudiante_nombre', 'estudiante_codigo',
            'modelo', 'modelo_nombre', 'promedio_notas_anterior',
            'porcentaje_asistencia', 'promedio_participaciones',
            'materias_cursadas', 'evaluaciones_completadas',
            'prediccion_numerica', 'nivel_rendimiento', 'confianza',
            'precision_porcentaje', 'color_nivel', 'fecha_prediccion',
            'rendimiento_real', 'validada'
        ]
        read_only_fields = ['id', 'fecha_prediccion']

class PrediccionRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de predicción"""
    promedio_notas_anterior = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    porcentaje_asistencia = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    promedio_participaciones = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    materias_cursadas = serializers.IntegerField(min_value=1)
    evaluaciones_completadas = serializers.IntegerField(min_value=0)
    estudiante_codigo = serializers.CharField(max_length=20, required=False)
    
    def validate(self, data):
        """Validaciones adicionales"""
        if data['promedio_notas_anterior'] < 0 or data['promedio_notas_anterior'] > 100:
            raise serializers.ValidationError("El promedio de notas debe estar entre 0 y 100")
        
        if data['porcentaje_asistencia'] < 0 or data['porcentaje_asistencia'] > 100:
            raise serializers.ValidationError("El porcentaje de asistencia debe estar entre 0 y 100")
            
        return data

class PrediccionResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de predicción"""
    prediccion_numerica = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    nivel_rendimiento = serializers.CharField(read_only=True)
    confianza = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    modelo_utilizado = serializers.CharField(read_only=True)
    id_prediccion = serializers.CharField(read_only=True, required=False)
    estudiante = serializers.DictField(read_only=True, required=False)