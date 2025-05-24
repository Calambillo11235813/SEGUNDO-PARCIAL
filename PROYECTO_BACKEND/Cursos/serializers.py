from rest_framework import serializers
from .models import Nivel, Curso, Materia, Notas, Boletin

class NivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nivel
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    nivel_nombre = serializers.ReadOnlyField(source='nivel.nombre')
    
    class Meta:
        model = Curso
        fields = ['id', 'grado', 'paralelo', 'nivel', 'nivel_nombre']

class MateriaSerializer(serializers.ModelSerializer):
    nombre_curso = serializers.ReadOnlyField(source='curso.nombre')
    
    class Meta:
        model = Materia
        fields = ['id', 'nombre', 'curso', 'nombre_curso']

class NotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notas
        fields = '__all__'

class BoletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boletin
        fields = '__all__'