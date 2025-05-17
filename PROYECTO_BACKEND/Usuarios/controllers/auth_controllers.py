from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Usuario
from ..serializers import UsuarioSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registra un nuevo usuario.
    """
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        
        # Generar tokens JWT para el nuevo usuario
        refresh = RefreshToken.for_user(usuario)
        
        return Response({
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Autentica al usuario y devuelve los tokens JWT.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['id']
        password = serializer.validated_data['contrasena']
        
        user = authenticate(request, username=user_id, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'usuario': {
                    'id': user.id,
                    'nombre': user.nombre,
                    'apellido': user.apellido,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)