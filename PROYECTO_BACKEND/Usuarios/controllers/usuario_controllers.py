from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Usuario, Rol
from ..serializers import UsuarioSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_usuarios(request):
    """
    Obtiene todos los usuarios registrados.
    Acceso público para todos.
    """
    try:
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_usuario(request, id):
    """
    Obtiene un usuario específico por su ID.
    Acceso público para todos.
    """
    try:
        usuario = Usuario.objects.get(pk=id)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_usuario(request, id):
    """
    Actualiza los datos de un usuario específico.
    Acceso público para todos.
    """
    try:
        usuario = Usuario.objects.get(pk=id)
        
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            # Si se está cambiando la contraseña
            if 'password' in request.data:
                usuario.set_password(request.data['password'])
                # Quitar para no procesarla en el serializer
                serializer.validated_data.pop('password', None)
            
            usuario = serializer.save()
            return Response(UsuarioSerializer(usuario).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Usuario.DoesNotExist:
        return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_usuario(request, id):
    """
    Elimina un usuario específico.
    Acceso público para todos.
    """
    try:
        usuario = Usuario.objects.get(pk=id)
        usuario.delete()
        return Response(
            {'mensaje': f'Usuario {usuario.nombre} {usuario.apellido} eliminado correctamente'}, 
            status=status.HTTP_200_OK
        )
    except Usuario.DoesNotExist:
        return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_rol_usuario(request, usuario_id):
    """
    Actualiza el rol de un usuario específico.
    """
    try:
        rol_id = request.data.get('rol_id')
        
        # Validar datos
        if not rol_id:
            return Response(
                {'error': 'Se requiere rol_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Obtener objetos
        usuario = Usuario.objects.get(pk=usuario_id)
        
        try:
            rol = Rol.objects.get(pk=rol_id)
        except Rol.DoesNotExist:
            return Response({'error': 'El rol no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        # Asignar rol al usuario
        usuario.rol = rol
        usuario.save()
        
        return Response({
            'mensaje': f'Rol {rol.nombre} asignado con éxito al usuario {usuario.nombre} {usuario.apellido}',
            'usuario': UsuarioSerializer(usuario).data
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_estudiantes_por_curso(request, curso_id):
    """
    Obtiene todos los estudiantes asignados a un curso específico por su ID.
    
    URL: /api/usuarios/estudiantes/1/
    """
    try:
        # Obtener estudiantes con rol "Estudiante" y del curso especificado
        estudiantes = Usuario.objects.filter(
            rol__nombre='Estudiante',
            curso_id=curso_id
        ).order_by('apellido', 'nombre')
        
        # Si no hay estudiantes en el curso
        if not estudiantes.exists():
            return Response(
                {'mensaje': f'No hay estudiantes asignados al curso con ID {curso_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = UsuarioSerializer(estudiantes, many=True)
        
        # Añadir metadatos al resultado
        result = {
            'total': estudiantes.count(),
            'curso_id': curso_id,
            'estudiantes': serializer.data
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_estudiantes(request):
    """
    Obtiene todos los estudiantes registrados en el sistema.
    """
    try:
        estudiantes = Usuario.objects.filter(rol__nombre='Estudiante').order_by('apellido', 'nombre')
        serializer = UsuarioSerializer(estudiantes, many=True)
        
        result = {
            'total': estudiantes.count(),
            'estudiantes': serializer.data
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_profesores(request):
    """
    Obtiene todos los usuarios con rol de Profesor.
    
    Parámetros de consulta opcionales:
    - materia_id: Filtra profesores asignados a una materia específica
    - activo: Filtra por estado activo (true/false)
    
    Ejemplo: /api/usuarios/profesores/?materia_id=10&activo=true
    """
    try:
        # Obtener profesores por su rol
        profesores = Usuario.objects.filter(rol__nombre='Profesor')
        
        # Aplicar filtros adicionales si se proporcionan
        materia_id = request.GET.get('materia_id')
        if materia_id:
            # Filtra profesores que tengan asignada esta materia
            profesores = profesores.filter(materias_asignadas__id=materia_id).distinct()
            
        activo = request.GET.get('activo')
        if activo is not None:
            is_active = activo.lower() == 'true'
            profesores = profesores.filter(is_active=is_active)
        
        # Ordenar por apellido y nombre
        profesores = profesores.order_by('apellido', 'nombre')
        
        serializer = UsuarioSerializer(profesores, many=True)
        
        # Añadir metadatos al resultado
        result = {
            'total': profesores.count(),
            'profesores': serializer.data
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)