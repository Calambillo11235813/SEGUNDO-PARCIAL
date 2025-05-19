from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    rol_id = serializers.IntegerField(write_only=True, required=False)  # Campo para recibir el ID del rol
    rol = serializers.SerializerMethodField()  # Campo para mostrar información del rol
    
    class Meta:
        model = Usuario
        fields = ['id', 'codigo', 'nombre', 'apellido', 'telefono', 'password', 'rol_id', 'rol']
        extra_kwargs = {
            'id': {'read_only': True},
            'codigo': {'required': False}
        }
    
    def get_rol(self, obj):
        if obj.rol:
            return {
                'id': obj.rol.id,
                'nombre': obj.rol.nombre
            }
        return None
    
    def create(self, validated_data):
        # Extraer rol_id y password
        rol_id = validated_data.pop('rol_id', None)
        password = validated_data.pop('password')
        
        # Crear el usuario
        usuario = Usuario.objects.create_user(
            **validated_data,
            password=password
        )
        
        # Si se proporcionó un rol_id, asignar el rol
        if rol_id:
            from Permisos.models import Rol
            try:
                rol = Rol.objects.get(id=rol_id)
                usuario.rol = rol
                usuario.save()
            except Rol.DoesNotExist:
                pass
                
        return usuario

class LoginSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    password = serializers.CharField(write_only=True)