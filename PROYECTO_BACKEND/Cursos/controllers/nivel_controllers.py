from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Nivel
from ..serializers import NivelSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_niveles(request):
    """
    Obtiene todos los niveles educativos registrados.
    """
    try:
        niveles = Nivel.objects.all()
        serializer = NivelSerializer(niveles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_nivel(request, id):
    """
    Obtiene un nivel específico por su ID.
    """
    try:
        nivel = Nivel.objects.get(pk=id)
        serializer = NivelSerializer(nivel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Nivel.DoesNotExist:
        return Response({'error': 'El nivel no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_nivel(request):
    """
    Crea un nuevo nivel educativo.
    """
    try:
        serializer = NivelSerializer(data=request.data)
        if serializer.is_valid():
            nivel = serializer.save()
            return Response({
                'mensaje': f'Nivel {nivel.nombre} creado correctamente',
                'nivel': NivelSerializer(nivel).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)