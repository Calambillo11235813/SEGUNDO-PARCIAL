from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Materia, Curso
from ..serializers import MateriaSerializer
from ..serializers import MateriaDetalleSerializer 

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
def create_materia_por_curso(request):
    """
    Crea una nueva materia especificando solo el curso_id y el nombre.
    """
    try:
        # Extraer datos
        nombre = request.data.get('nombre')
        curso_id = request.data.get('curso_id')
        
        # Validaciones básicas
        if not all([nombre, curso_id]):
            return Response(
                {'error': 'Debe proporcionar nombre y curso_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar el curso
        try:
            curso = Curso.objects.get(pk=curso_id)
        except Curso.DoesNotExist:
            return Response(
                {'error': 'No se encontró el curso especificado'},
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

@api_view(['POST'])
@permission_classes([AllowAny])  # Reemplaza con la política de permisos adecuada
def asignar_profesor(request, materia_id):
    """
    Asigna un profesor a una materia específica.
    Requiere materia_id en la URL y profesor_id en el cuerpo de la solicitud.
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(pk=materia_id)
        except Materia.DoesNotExist:
            return Response({'error': 'La materia no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener el profesor_id del cuerpo de la solicitud
        profesor_id = request.data.get('profesor_id')
        if not profesor_id:
            return Response(
                {'error': 'Debe proporcionar el ID del profesor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el profesor existe y tiene rol de profesor
        try:
            # Importamos el modelo Usuario
            from Usuarios.models import Usuario
            profesor = Usuario.objects.get(pk=profesor_id)
            
            # Verificar si tiene rol de profesor
            if not profesor.rol or profesor.rol.nombre != 'Profesor':
                return Response(
                    {'error': 'El usuario seleccionado no tiene rol de profesor'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {'error': 'El profesor no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asignar el profesor a la materia
        materia.profesor = profesor
        materia.save()
        
        return Response({
            'mensaje': f'Profesor {profesor.nombre} {profesor.apellido} asignado a la materia {materia.nombre}',
            'materia': MateriaDetalleSerializer(materia).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # Reemplaza con la política de permisos adecuada
def desasignar_profesor(request, materia_id):
    """
    Desasigna al profesor de una materia específica.
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(pk=materia_id)
        except Materia.DoesNotExist:
            return Response({'error': 'La materia no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        if not materia.profesor:
            return Response(
                {'error': 'La materia no tiene profesor asignado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nombre_profesor = f"{materia.profesor.nombre} {materia.profesor.apellido}"
        
        # Desasignar el profesor
        materia.profesor = None
        materia.save()
        
        return Response({
            'mensaje': f'Profesor {nombre_profesor} desasignado de la materia {materia.nombre}',
            'materia': MateriaDetalleSerializer(materia).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])  # Reemplaza con la política de permisos adecuada
def get_materias_por_profesor(request, profesor_id):
    """
    Obtiene todas las materias asignadas a un profesor específico.
    """
    try:
        # Verificar que el profesor existe
        try:
            # Importamos el modelo Usuario
            from Usuarios.models import Usuario
            profesor = Usuario.objects.get(pk=profesor_id)
        except:
            return Response(
                {'error': 'El profesor no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener las materias del profesor
        materias = Materia.objects.filter(profesor=profesor)
        
        # Serializar con información adicional del curso
        serializer = MateriaDetalleSerializer(materias, many=True)
        
        return Response({
            'profesor': f"{profesor.nombre} {profesor.apellido}",
            'materias': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)