from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Curso, Nivel, Trimestre  # Eliminar Usuario de aquí
from ..serializers import CursoSerializer
from django.db.models import F

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



@api_view(['POST'])
@permission_classes([AllowAny])
def asignar_estudiante_a_curso(request):
    """
    Asigna un estudiante a un curso específico.
    Verifica que el estudiante no tenga otro curso asignado.
    
    Request body:
    {
        "estudiante_id": 1,
        "curso_id": 2
    }
    """
    try:
        estudiante_id = request.data.get('estudiante_id')
        curso_id = request.data.get('curso_id')
        
        # Validaciones
        if not estudiante_id or not curso_id:
            return Response(
                {'error': 'Se requiere estudiante_id y curso_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener estudiante
        try:
            from Usuarios.models import Usuario
            estudiante = Usuario.objects.get(id=estudiante_id, rol__nombre='Estudiante')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ NUEVA VALIDACIÓN: Verificar que el estudiante no tenga curso asignado
        if estudiante.curso:
            return Response(
                {
                    'error': f'El estudiante {estudiante.nombre} {estudiante.apellido} ya está asignado al curso {estudiante.curso}',
                    'curso_actual': str(estudiante.curso),
                    'estudiante': f"{estudiante.nombre} {estudiante.apellido}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener curso
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return Response(
                {'error': 'Curso no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asignar curso al estudiante
        estudiante.curso = curso
        estudiante.save()
        
        return Response({
            'mensaje': f'Estudiante {estudiante.nombre} {estudiante.apellido} asignado exitosamente al curso {curso}',
            'estudiante': {
                'id': estudiante.id,
                'nombre': f"{estudiante.nombre} {estudiante.apellido}",
                'codigo': estudiante.codigo
            },
            'curso': {
                'id': curso.id,
                'nombre': str(curso)
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ✅ NUEVO ENDPOINT: Obtener estudiantes sin curso asignado
@api_view(['GET'])
@permission_classes([AllowAny])
def get_estudiantes_sin_curso(request):
    """
    Obtiene todos los estudiantes que no tienen curso asignado.
    """
    try:
        from Usuarios.models import Usuario
        
        # Obtener estudiantes sin curso
        estudiantes_sin_curso = Usuario.objects.filter(
            rol__nombre='Estudiante',
            curso__isnull=True  # Solo estudiantes sin curso
        ).select_related('rol')
        
        # Preparar respuesta
        estudiantes_data = []
        for estudiante in estudiantes_sin_curso:
            estudiantes_data.append({
                'id': estudiante.id,
                'codigo': estudiante.codigo,
                'nombre': estudiante.nombre,
                'apellido': estudiante.apellido,
                'nombre_completo': f"{estudiante.nombre} {estudiante.apellido}"
            })
        
        return Response({
            'estudiantes': estudiantes_data,
            'total': len(estudiantes_data),
            'mensaje': f'Se encontraron {len(estudiantes_data)} estudiantes disponibles para asignar'
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_estudiantes_de_curso(request, curso_id):
    """
    Obtiene todos los estudiantes asignados a un curso específico.
    """
    try:
        # Verificar que el curso existe
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return Response(
                {'error': f'Curso con id {curso_id} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Importar Usuario donde se necesita
        from Usuarios.models import Usuario
        
        # Obtener estudiantes asignados a este curso
        estudiantes = Usuario.objects.filter(
            curso=curso,
            rol__nombre='Estudiante'
        ).select_related('rol')
        
        # Preparar respuesta
        estudiantes_data = []
        for estudiante in estudiantes:
            estudiantes_data.append({
                'id': estudiante.id,
                'codigo': estudiante.codigo,
                'nombre': estudiante.nombre,
                'apellido': estudiante.apellido,
                'nombre_completo': f"{estudiante.nombre} {estudiante.apellido}"
            })
        
        return Response({
            'curso': {
                'id': curso.id,
                'nombre': str(curso),
                'nivel': curso.nivel.nombre if curso.nivel else None,
                'grado': curso.grado,
                'paralelo': curso.paralelo
            },
            'estudiantes': estudiantes_data,
            'total_estudiantes': len(estudiantes_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def desasignar_estudiante_de_curso(request, estudiante_id):
    """
    Desasigna un estudiante de su curso actual.
    """
    try:
        # Importar Usuario donde se necesita
        from Usuarios.models import Usuario
        
        # Obtener estudiante
        try:
            estudiante = Usuario.objects.get(id=estudiante_id, rol__nombre='Estudiante')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el estudiante tenga un curso asignado
        if not estudiante.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        curso_anterior = str(estudiante.curso)
        estudiante.curso = None
        estudiante.save()
        
        return Response({
            'mensaje': f'Estudiante {estudiante.nombre} {estudiante.apellido} desasignado del curso {curso_anterior}',
            'estudiante': f"{estudiante.nombre} {estudiante.apellido}"
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_años_academicos(request):
    """
    Obtiene todos los años académicos disponibles en el sistema.
    """
    try:
        # Obtener años académicos distintos de los trimestres
        años = Trimestre.objects.values_list('año_academico', flat=True).distinct().order_by('-año_academico')
        return Response(list(años), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_trimestres(request):
    """
    Obtiene todos los trimestres, con opción de filtrar por año académico.
    """
    try:
        # Obtener parámetros de filtro
        año_academico = request.query_params.get('año_academico')
        
        # Aplicar filtros si se proporcionan
        trimestres = Trimestre.objects.all()
        if año_academico:
            trimestres = trimestres.filter(año_academico=año_academico)
        
        # Ordenar por año académico (descendente) y luego por el orden natural de los trimestres
        trimestres = trimestres.order_by('-año_academico', 'id')
        
        # Crear respuesta manual para controlar exactamente qué campos devolver
        resultado = []
        for trimestre in trimestres:
            resultado.append({
                'id': trimestre.id,
                'nombre': trimestre.nombre,
                'año_academico': trimestre.año_academico,
                'fecha_inicio': trimestre.fecha_inicio,
                'fecha_fin': trimestre.fecha_fin,
                'activo': trimestre.activo
            })
        
        return Response(resultado, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def get_cantidad_cursos(request):
    """
    Devuelve la cantidad total de cursos registrados en el sistema.
    """
    try:
        cantidad_cursos = Curso.objects.count()
        
        return Response({
            'cantidad_cursos': cantidad_cursos,
            'mensaje': f'Hay {cantidad_cursos} cursos registrados en el sistema'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
