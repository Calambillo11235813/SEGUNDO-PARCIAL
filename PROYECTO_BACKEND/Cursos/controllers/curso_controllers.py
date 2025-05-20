from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Curso, Nivel
from ..serializers import CursoSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cursos(request):
    """
    Obtiene todos los cursos registrados.
    """
    try:
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_curso(request, id):
    """
    Obtiene un curso específico por su ID.
    """
    try:
        curso = Curso.objects.get(pk=id)
        serializer = CursoSerializer(curso)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Curso.DoesNotExist:
        return Response({'error': 'El curso no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_curso(request):
    """
    Crea un nuevo curso.
    """
    try:
        # Validamos los datos
        serializer = CursoSerializer(data=request.data)
        if serializer.is_valid():
            curso = serializer.save()
            return Response({
                'mensaje': f'Curso {curso} creado correctamente',
                'curso': CursoSerializer(curso).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_curso(request, id):
    """
    Actualiza los datos de un curso específico.
    """
    try:
        curso = Curso.objects.get(pk=id)
        
        serializer = CursoSerializer(curso, data=request.data, partial=True)
        if serializer.is_valid():
            curso = serializer.save()
            return Response({
                'mensaje': f'Curso {curso} actualizado correctamente',
                'curso': CursoSerializer(curso).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Curso.DoesNotExist:
        return Response({'error': 'El curso no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_curso(request, id):
    """
    Elimina un curso específico.
    """
    try:
        curso = Curso.objects.get(pk=id)
        curso_str = str(curso)
        curso.delete()
        return Response(
            {'mensaje': f'Curso {curso_str} eliminado correctamente'}, 
            status=status.HTTP_200_OK
        )
    except Curso.DoesNotExist:
        return Response({'error': 'El curso no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cursos_por_nivel(request, nivel_id):
    """
    Obtiene todos los cursos de un nivel específico.
    """
    try:
        # Verificar que el nivel existe
        try:
            nivel = Nivel.objects.get(pk=nivel_id)
        except Nivel.DoesNotExist:
            return Response({'error': 'El nivel no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        cursos = Curso.objects.filter(nivel=nivel)
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)