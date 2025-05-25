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
    class Meta:
        model = Materia
        fields = ['id', 'nombre', 'curso', 'profesor']
        
# También puedes crear un serializador especial para respuestas detalladas
class MateriaDetalleSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.StringRelatedField(source='curso')
    profesor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Materia
        fields = ['id', 'nombre', 'curso', 'curso_nombre', 'profesor', 'profesor_nombre']
    
    def get_profesor_nombre(self, obj):
        if obj.profesor:
            return f"{obj.profesor.nombre} {obj.profesor.apellido}"
        return None

class NotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notas
        fields = '__all__'

class BoletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boletin
        fields = '__all__'