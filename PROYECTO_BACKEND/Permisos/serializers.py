from rest_framework import serializers
from .models import Rol, Privilegio, Permiso, Notificacion

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']  # Solo incluimos los campos id y nombre
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation