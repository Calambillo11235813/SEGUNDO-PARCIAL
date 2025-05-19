from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Usuario
from ..serializers import UsuarioSerializer, LoginSerializer
from Permisos.models import Rol

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registrar un nuevo usuario.
    Opcionalmente puede asignar un rol.
    """
    try:
        # Obtener datos del usuario a registrar
        serializer = UsuarioSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Devolver respuesta exitosa
            return Response({
                'mensaje': f'Usuario {usuario.nombre} {usuario.apellido} registrado correctamente',
                'usuario': UsuarioSerializer(usuario).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Autentica al usuario y devuelve los tokens JWT.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        codigo = serializer.validated_data['codigo']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=codigo, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'mensaje': 'Inicio de sesión exitoso. ¡Bienvenido!',
                'usuario': {
                    'id': user.id,
                    'codigo': user.codigo,
                    'nombre': user.nombre,
                    'apellido': user.apellido,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)