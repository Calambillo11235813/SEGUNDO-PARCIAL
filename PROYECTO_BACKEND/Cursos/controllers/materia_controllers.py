from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Materia, Curso
from ..serializers import MateriaSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_materias(request):
    """
    Obtiene todas las materias registradas.
    Acceso público para todos.
    """
    try:
        materias = Materia.objects.all()
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_materia(request, id):
    """
    Obtiene una materia específica por su ID.
    Acceso público para todos.
    """
    try:
        materia = Materia.objects.get(pk=id)
        serializer = MateriaSerializer(materia)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Materia.DoesNotExist:
        return Response({'error': 'La materia no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@permission_classes([AllowAny])
def update_materia(request, id):
    """
    Actualiza los datos de una materia específica.
    Acceso público para todos.
    """
    try:
        materia = Materia.objects.get(pk=id)
        
        serializer = MateriaSerializer(materia, data=request.data, partial=True)
        if serializer.is_valid():
            materia = serializer.save()
            return Response({
                'mensaje': f'Materia {materia.nombre} actualizada correctamente',
                'materia': MateriaSerializer(materia).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Materia.DoesNotExist:
        return Response({'error': 'La materia no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_materia(request, id):
    """
    Elimina una materia específica.
    Acceso público para todos.
    """
    try:
        materia = Materia.objects.get(pk=id)
        nombre = materia.nombre
        materia.delete()
        return Response(
            {'mensaje': f'Materia {nombre} eliminada correctamente'}, 
            status=status.HTTP_200_OK
        )
    except Materia.DoesNotExist:
        return Response({'error': 'La materia no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_materias_por_curso(request, curso_id):
    """
    Obtiene todas las materias de un curso específico.
    Acceso público para todos.
    """
    try:
        # Verificar que el curso existe
        try:
            curso = Curso.objects.get(pk=curso_id)
        except Curso.DoesNotExist:
            return Response({'error': 'El curso no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        materias = Materia.objects.filter(curso=curso)
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_materia_por_nivel_grado(request):
    """
    Crea una nueva materia especificando el nivel_id, grado y paralelo del curso.
    """
    try:
        # Extraer datos
        nombre = request.data.get('nombre')
        nivel_id = request.data.get('nivel_id')
        grado = request.data.get('grado')
        paralelo = request.data.get('paralelo')
        
        # Validaciones básicas
        if not all([nombre, nivel_id, grado, paralelo]):
            return Response(
                {'error': 'Debe proporcionar nombre, nivel_id, grado y paralelo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar el curso
        try:
            curso = Curso.objects.get(nivel_id=nivel_id, grado=grado, paralelo=paralelo)
        except Curso.DoesNotExist:
            return Response(
                {'error': 'No se encontró un curso con los parámetros especificados'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Crear la materia
        materia_data = {
            'nombre': nombre,
            'curso': curso.id
        }
        
        serializer = MateriaSerializer(data=materia_data)
        if serializer.is_valid():
            materia = serializer.save()
            return Response({
                'mensaje': f'Materia {materia.nombre} creada correctamente en el curso {curso}',
                'materia': MateriaSerializer(materia).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_materias_por_nivel_grado_paralelo(request):
    """
    Obtiene todas las materias de un curso específico mediante nivel_id, grado y paralelo.
    """
    try:
        # Obtener parámetros de la URL
        nivel_id = request.GET.get('nivel_id')
        grado = request.GET.get('grado')
        paralelo = request.GET.get('paralelo')
        
        # Validar que se proporcionen todos los parámetros
        if not all([nivel_id, grado, paralelo]):
            return Response(
                {'error': 'Debe proporcionar nivel_id, grado y paralelo como parámetros'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar el curso
        try:
            curso = Curso.objects.get(nivel_id=nivel_id, grado=grado, paralelo=paralelo)
        except Curso.DoesNotExist:
            return Response(
                {'error': 'No se encontró un curso con los parámetros especificados'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener las materias del curso
        materias = Materia.objects.filter(curso=curso)
        serializer = MateriaSerializer(materias, many=True)
        
        return Response({
            'curso': str(curso),
            'materias': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)