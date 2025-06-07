from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from ..models import Materia, Curso, EvaluacionEntregable, EvaluacionParticipacion
from ..serializers import MateriaSerializer
from ..serializers import MateriaDetalleSerializer 
from django.db.models import Count, Avg, Max, Min, Sum
from ..utils import get_evaluacion_by_id, get_evaluaciones_activas

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
        
        # Obtener evaluaciones de ambos tipos
        evaluaciones_entregable = EvaluacionEntregable.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        # Combinar todas las evaluaciones
        evaluaciones = list(evaluaciones_entregable) + list(evaluaciones_participacion)
        
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
            
            eval_data = {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'publicado': evaluacion.publicado,
                'tipo_objeto': 'entregable' if isinstance(evaluacion, EvaluacionEntregable) else 'participacion'
            }
            
            # Añadir campos específicos según el tipo
            if isinstance(evaluacion, EvaluacionEntregable):
                eval_data.update({
                    'fecha_entrega': evaluacion.fecha_entrega,
                    'nota_maxima': float(evaluacion.nota_maxima)
                })
            else:  # Es EvaluacionParticipacion
                eval_data.update({
                    'fecha_registro': evaluacion.fecha_registro
                })
                
            tipos_evaluacion_data[tipo_id]['evaluaciones'].append(eval_data)
        
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
        
        # Este enfoque es más complejo ahora que tenemos dos modelos
        # Haremos consultas separadas y luego combinaremos los resultados
        
        # Consulta para entregables
        entregables_resumen = EvaluacionEntregable.objects.filter(
            materia=materia,
            activo=True
        ).values(
            'tipo_evaluacion__id',
            'tipo_evaluacion__nombre',
            'tipo_evaluacion__descripcion'
        ).annotate(
            cantidad=Count('id')
        )
        
        # Consulta para participaciones
        participaciones_resumen = EvaluacionParticipacion.objects.filter(
            materia=materia,
            activo=True
        ).values(
            'tipo_evaluacion__id',
            'tipo_evaluacion__nombre',
            'tipo_evaluacion__descripcion'
        ).annotate(
            cantidad=Count('id')
        )
        
        # Combinar resultados
        tipos_data = {}
        
        # Procesar entregables
        for tipo in entregables_resumen:
            tipo_id = tipo['tipo_evaluacion__id']
            tipos_data[tipo_id] = {
                'id': tipo_id,
                'nombre': tipo['tipo_evaluacion__nombre'],
                'descripcion': tipo['tipo_evaluacion__descripcion'],
                'cantidad_evaluaciones': tipo['cantidad']
            }
        
        # Procesar participaciones (agregando a los existentes o creando nuevos)
        for tipo in participaciones_resumen:
            tipo_id = tipo['tipo_evaluacion__id']
            if tipo_id in tipos_data:
                tipos_data[tipo_id]['cantidad_evaluaciones'] += tipo['cantidad']
            else:
                tipos_data[tipo_id] = {
                    'id': tipo_id,
                    'nombre': tipo['tipo_evaluacion__nombre'],
                    'descripcion': tipo['tipo_evaluacion__descripcion'],
                    'cantidad_evaluaciones': tipo['cantidad']
                }
        
        # Convertir a lista y ordenar
        tipos_lista = list(tipos_data.values())
        tipos_lista.sort(key=lambda x: x['nombre'])
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre
            },
            'tipos_evaluacion': tipos_lista,
            'total_tipos': len(tipos_lista),
            'total_evaluaciones': sum(tipo['cantidad_evaluaciones'] for tipo in tipos_lista)
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
        
        # Obtener evaluaciones de ambos tipos
        evaluaciones_entregable = EvaluacionEntregable.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        # Calcular estadísticas generales
        total_entregables = evaluaciones_entregable.count()
        total_participaciones = evaluaciones_participacion.count()
        total_evaluaciones = total_entregables + total_participaciones
        
        entregables_publicados = evaluaciones_entregable.filter(publicado=True).count()
        participaciones_publicadas = evaluaciones_participacion.filter(publicado=True).count()
        evaluaciones_publicadas = entregables_publicados + participaciones_publicadas
        
        evaluaciones_pendientes = total_evaluaciones - evaluaciones_publicadas
        
        # Calcular porcentajes
        porcentaje_entregables = sum(float(e.porcentaje_nota_final) for e in evaluaciones_entregable)
        porcentaje_participaciones = sum(float(e.porcentaje_nota_final) for e in evaluaciones_participacion)
        porcentaje_total = porcentaje_entregables + porcentaje_participaciones
        
        # Para estadísticas por tipo, necesitamos combinar datos de ambos modelos
        tipos_stats = {}
        
        # Procesar todas las evaluaciones y agrupar por tipo
        for evaluacion in list(evaluaciones_entregable) + list(evaluaciones_participacion):
            tipo_id = evaluacion.tipo_evaluacion.id
            tipo_nombre = evaluacion.tipo_evaluacion.nombre
            tipo_descripcion = evaluacion.tipo_evaluacion.descripcion
            
            if tipo_id not in tipos_stats:
                tipos_stats[tipo_id] = {
                    'id': tipo_id,
                    'nombre': tipo_nombre,
                    'descripcion': tipo_descripcion,
                    'cantidad_evaluaciones': 0,
                    'porcentaje_total': 0,
                    'nota_maxima_suma': 0,
                    'nota_maxima_count': 0,
                    'porcentaje_suma': 0
                }
            
            tipos_stats[tipo_id]['cantidad_evaluaciones'] += 1
            tipos_stats[tipo_id]['porcentaje_total'] += float(evaluacion.porcentaje_nota_final)
            tipos_stats[tipo_id]['porcentaje_suma'] += float(evaluacion.porcentaje_nota_final)
            
            # Solo las evaluaciones entregables tienen nota_maxima
            if isinstance(evaluacion, EvaluacionEntregable):
                tipos_stats[tipo_id]['nota_maxima_suma'] += float(evaluacion.nota_maxima)
                tipos_stats[tipo_id]['nota_maxima_count'] += 1
        
        # Calcular promedios y formatear datos
        tipos_data = []
        for tipo_id, stats in tipos_stats.items():
            nota_maxima_promedio = 0
            if stats['nota_maxima_count'] > 0:
                nota_maxima_promedio = stats['nota_maxima_suma'] / stats['nota_maxima_count']
            
            porcentaje_promedio = 0
            if stats['cantidad_evaluaciones'] > 0:
                porcentaje_promedio = stats['porcentaje_suma'] / stats['cantidad_evaluaciones']
            
            tipos_data.append({
                'id': stats['id'],
                'nombre': stats['nombre'],
                'descripcion': stats['descripcion'],
                'cantidad_evaluaciones': stats['cantidad_evaluaciones'],
                'porcentaje_promedio': round(porcentaje_promedio, 2),
                'nota_maxima_promedio': round(nota_maxima_promedio, 2),
                'porcentaje_total': round(stats['porcentaje_total'], 2)
            })
        
        # Ordenar por nombre
        tipos_data.sort(key=lambda x: x['nombre'])
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
            },
            'estadisticas_generales': {
                'total_evaluaciones': total_evaluaciones,
                'evaluaciones_entregables': total_entregables,
                'evaluaciones_participacion': total_participaciones,
                'evaluaciones_publicadas': evaluaciones_publicadas,
                'evaluaciones_pendientes': evaluaciones_pendientes,
                'porcentaje_total_asignado': round(porcentaje_total, 2),
                'porcentaje_restante': round(100 - porcentaje_total, 2)
            },
            'tipos_evaluacion': tipos_data,
            'total_tipos_diferentes': len(tipos_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )