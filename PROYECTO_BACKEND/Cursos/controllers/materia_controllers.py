from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Materia, Curso, Evaluacion
from ..serializers import MateriaSerializer
from ..serializers import MateriaDetalleSerializer 
from django.db.models import Count, Avg, Max, Min, Sum

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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tipos_evaluacion_por_materia(request, materia_id):
    """
    Obtiene todos los tipos de evaluación que tiene asignados una materia específica.
    Incluye el nombre del tipo de evaluación y la cantidad de evaluaciones de cada tipo.
    
    GET /api/evaluaciones/materia/{materia_id}/tipos/
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener tipos de evaluación únicos de esta materia
        evaluaciones = Evaluacion.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        # Agrupar por tipo de evaluación y contar
        tipos_evaluacion_data = {}
        
        for evaluacion in evaluaciones:
            tipo_id = evaluacion.tipo_evaluacion.id
            tipo_nombre = evaluacion.tipo_evaluacion.nombre
            tipo_display = evaluacion.tipo_evaluacion.get_nombre_display()
            
            if tipo_id not in tipos_evaluacion_data:
                tipos_evaluacion_data[tipo_id] = {
                    'id': tipo_id,
                    'nombre': tipo_nombre,
                    'nombre_display': tipo_display,
                    'descripcion': evaluacion.tipo_evaluacion.descripcion,
                    'cantidad_evaluaciones': 0,
                    'evaluaciones': []
                }
            
            tipos_evaluacion_data[tipo_id]['cantidad_evaluaciones'] += 1
            tipos_evaluacion_data[tipo_id]['evaluaciones'].append({
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'fecha_entrega': evaluacion.fecha_entrega,
                'nota_maxima': float(evaluacion.nota_maxima),
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'publicado': evaluacion.publicado
            })
        
        # Convertir el diccionario a lista
        tipos_list = list(tipos_evaluacion_data.values())
        
        # Ordenar por nombre del tipo
        tipos_list.sort(key=lambda x: x['nombre'])
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
            },
            'tipos_evaluacion': tipos_list,
            'total_tipos': len(tipos_list),
            'total_evaluaciones': sum(tipo['cantidad_evaluaciones'] for tipo in tipos_list)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_resumen_tipos_evaluacion_por_materia(request, materia_id):
    """
    Obtiene un resumen simplificado de los tipos de evaluación por materia.
    Solo devuelve el nombre y la cantidad, sin detalles de las evaluaciones.
    
    GET /api/evaluaciones/materia/{materia_id}/tipos/resumen/
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Query más eficiente usando values y Count
        tipos_resumen = Evaluacion.objects.filter(
            materia=materia,
            activo=True
        ).values(
            'tipo_evaluacion__id',
            'tipo_evaluacion__nombre',
            'tipo_evaluacion__descripcion'
        ).annotate(
            cantidad=Count('id')
        ).order_by('tipo_evaluacion__nombre')
        
        # Formatear la respuesta
        tipos_data = []
        for tipo in tipos_resumen:
            tipos_data.append({
                'id': tipo['tipo_evaluacion__id'],
                'nombre': tipo['tipo_evaluacion__nombre'],
                'descripcion': tipo['tipo_evaluacion__descripcion'],
                'cantidad_evaluaciones': tipo['cantidad']
            })
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre
            },
            'tipos_evaluacion': tipos_data,
            'total_tipos': len(tipos_data),
            'total_evaluaciones': sum(tipo['cantidad_evaluaciones'] for tipo in tipos_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_estadisticas_evaluaciones_por_materia(request, materia_id):
    """
    Obtiene estadísticas completas de evaluaciones por materia.
    Incluye información detallada sobre tipos, fechas, notas, etc.
    
    GET /api/evaluaciones/materia/{materia_id}/estadisticas/
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las evaluaciones de la materia
        evaluaciones = Evaluacion.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        # Calcular estadísticas generales
        total_evaluaciones = evaluaciones.count()
        evaluaciones_publicadas = evaluaciones.filter(publicado=True).count()
        evaluaciones_pendientes = evaluaciones.filter(publicado=False).count()
        
        # Calcular porcentajes
        porcentaje_total = evaluaciones.aggregate(
            total=Sum('porcentaje_nota_final')
        )['total'] or 0
        
        # Agrupar por tipo con estadísticas
        tipos_stats = evaluaciones.values(
            'tipo_evaluacion__id',
            'tipo_evaluacion__nombre',
            'tipo_evaluacion__descripcion'
        ).annotate(
            cantidad=Count('id'),
            porcentaje_promedio=Avg('porcentaje_nota_final'),
            nota_maxima_promedio=Avg('nota_maxima'),
            porcentaje_total=Sum('porcentaje_nota_final')
        ).order_by('tipo_evaluacion__nombre')
        
        tipos_data = []
        for tipo in tipos_stats:
            tipos_data.append({
                'id': tipo['tipo_evaluacion__id'],
                'nombre': tipo['tipo_evaluacion__nombre'],
                'descripcion': tipo['tipo_evaluacion__descripcion'],
                'cantidad_evaluaciones': tipo['cantidad'],
                'porcentaje_promedio': round(float(tipo['porcentaje_promedio'] or 0), 2),
                'nota_maxima_promedio': round(float(tipo['nota_maxima_promedio'] or 0), 2),
                'porcentaje_total': round(float(tipo['porcentaje_total'] or 0), 2)
            })
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
            },
            'estadisticas_generales': {
                'total_evaluaciones': total_evaluaciones,
                'evaluaciones_publicadas': evaluaciones_publicadas,
                'evaluaciones_pendientes': evaluaciones_pendientes,
                'porcentaje_total_asignado': round(float(porcentaje_total), 2),
                'porcentaje_restante': round(100 - float(porcentaje_total), 2)
            },
            'tipos_evaluacion': tipos_data,
            'total_tipos_diferentes': len(tipos_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )