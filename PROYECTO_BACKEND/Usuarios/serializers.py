from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'telefono', 'contrasena']
        extra_kwargs = {'contrasena': {'write_only': True}}
    
    def create(self, validated_data):
        usuario = Usuario.objects.create_user(
            id=validated_data.get('id'),
            nombre=validated_data['nombre'],
            apellido=validated_data['apellido'],
            telefono=validated_data.get('telefono'),
            password=validated_data['contrasena']
        )
        return usuario

class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contrasena = serializers.CharField(write_only=True)