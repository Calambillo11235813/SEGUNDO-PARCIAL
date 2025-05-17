from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'codigo', 'nombre', 'apellido', 'telefono', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'codigo': {'required': False}
        }
    
    def create(self, validated_data):
        # Extrae la contraseña para pasarla como parámetro separado
        password = validated_data.pop('password')
        usuario = Usuario.objects.create_user(
            **validated_data,
            password=password
        )
        return usuario

class LoginSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    password = serializers.CharField(write_only=True)