from datetime import datetime  # Añadir esta línea
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from ..models import (Materia, TipoEvaluacion, Trimestre, ConfiguracionEvaluacionMateria,
                    EvaluacionBase, EvaluacionEntregable, EvaluacionParticipacion,
                    Calificacion, Curso)  # Añadido Curso aquí
from ..utils import get_evaluacion_by_id, get_evaluaciones_count, get_evaluaciones_activas

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tipos_evaluacion(request):
    """
    Obtiene todos los tipos de evaluación disponibles.
    """
    try:
        tipos = TipoEvaluacion.objects.filter(activo=True)
        
        tipos_data = []
        for tipo in tipos:
            tipos_data.append({
                'id': tipo.id,
                'nombre': tipo.nombre,
                'nombre_display': tipo.get_nombre_display(),
                'descripcion': tipo.descripcion
            })
        
        return Response({
            'tipos_evaluacion': tipos_data
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_evaluacion(request):
    """
    Crea una nueva evaluación.
    """
    try:
        data = request.data
        
        # Validaciones básicas comunes para todos los tipos
        campos_requeridos_basicos = ['materia_id', 'tipo_evaluacion_id', 'trimestre_id', 'titulo', 'porcentaje_nota_final']
        for campo in campos_requeridos_basicos:
            if not data.get(campo):
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Verificar materia
        try:
            materia = Materia.objects.get(id=data['materia_id'])
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar tipo de evaluación
        try:
            tipo_evaluacion = TipoEvaluacion.objects.get(id=data['tipo_evaluacion_id'])
        except TipoEvaluacion.DoesNotExist:
            return Response(
                {'error': 'Tipo de evaluación no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar trimestre
        try:
            trimestre = Trimestre.objects.get(id=data['trimestre_id'])
        except Trimestre.DoesNotExist:
            return Response(
                {'error': 'Trimestre no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validaciones específicas por tipo de evaluación
        if tipo_evaluacion.nombre == 'PARTICIPACION':
            # Para participación, validar fecha_registro
            if not data.get('fecha_registro'):
                return Response(
                    {'error': 'Para evaluaciones de participación, se requiere fecha_registro'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                fecha_registro = datetime.strptime(data['fecha_registro'], '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_registro inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Para otros tipos, validar fechas de entrega y asignación
            if not data.get('fecha_asignacion') or not data.get('fecha_entrega'):
                return Response(
                    {'error': 'Los campos fecha_asignacion y fecha_entrega son requeridos para este tipo de evaluación'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                fecha_asignacion = datetime.strptime(data['fecha_asignacion'], '%Y-%m-%d').date()
                fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date()
                fecha_limite = None
                
                if data.get('fecha_limite'):
                    fecha_limite = datetime.strptime(data['fecha_limite'], '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar lógica de fechas
            if fecha_entrega < fecha_asignacion:
                return Response(
                    {'error': 'La fecha de entrega no puede ser anterior a la fecha de asignación'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if fecha_limite and fecha_limite < fecha_entrega:
                return Response(
                    {'error': 'La fecha límite no puede ser anterior a la fecha de entrega'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # ✅ ACTUALIZADO: Notas con valores por defecto mejorados
        nota_maxima = data.get('nota_maxima', 100.0)
        nota_minima_aprobacion = data.get('nota_minima_aprobacion', 51.0)
        
        # Validar rango de notas
        if nota_minima_aprobacion > nota_maxima:
            return Response(
                {'error': 'La nota mínima de aprobación no puede ser mayor que la nota máxima'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar la configuración de evaluación para esta materia/tipo
        configuracion = ConfiguracionEvaluacionMateria.objects.filter(
            materia=materia,
            tipo_evaluacion=tipo_evaluacion,
            activo=True
        ).first()

        if not configuracion:
            return Response(
                {'error': f'No existe una configuración de porcentaje para el tipo de evaluación {tipo_evaluacion} en esta materia. Configure los porcentajes primero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que el porcentaje de la evaluación no exceda el configurado para su tipo
        porcentaje_evaluacion = float(data['porcentaje_nota_final'])
        if porcentaje_evaluacion > float(configuracion.porcentaje):
            return Response(
                {'error': f'El porcentaje de la evaluación ({porcentaje_evaluacion}%) excede el configurado para {tipo_evaluacion} ({configuracion.porcentaje}%)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que no se exceda el porcentaje total para este tipo de evaluación en el trimestre
        entregables = EvaluacionEntregable.objects.filter(
            materia=materia,
            tipo_evaluacion=tipo_evaluacion,
            trimestre=trimestre,
            activo=True
        ).exclude(id=data.get('id'))
        
        participaciones = EvaluacionParticipacion.objects.filter(
            materia=materia,
            tipo_evaluacion=tipo_evaluacion,
            trimestre=trimestre,
            activo=True
        ).exclude(id=data.get('id'))
        
        porcentaje_usado = sum(float(e.porcentaje_nota_final) for e in entregables)
        porcentaje_usado += sum(float(e.porcentaje_nota_final) for e in participaciones)
        
        if porcentaje_usado + porcentaje_evaluacion > float(configuracion.porcentaje):
            return Response({
                'error': f'La suma de porcentajes para evaluaciones de tipo {tipo_evaluacion} en este trimestre excedería el máximo configurado ({configuracion.porcentaje}%)',
                'porcentaje_disponible': float(configuracion.porcentaje) - porcentaje_usado,
                'porcentaje_usado': porcentaje_usado
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determinar qué tipo de modelo crear según el tipo_evaluacion
        if tipo_evaluacion.nombre == 'PARTICIPACION':
            # Para participación en clase
            if 'fecha_registro' not in data:
                return Response(
                    {'error': 'Para evaluaciones de participación, se requiere fecha_registro'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                fecha_registro = datetime.strptime(data['fecha_registro'], '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_registro inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            evaluacion = EvaluacionParticipacion.objects.create(
                materia=materia,
                tipo_evaluacion=tipo_evaluacion,
                trimestre=trimestre,
                titulo=data['titulo'],
                descripcion=data.get('descripcion', ''),
                porcentaje_nota_final=data['porcentaje_nota_final'],
                fecha_registro=fecha_registro,
                criterios_participacion=data.get('criterios_participacion', ''),
                escala_calificacion=data.get('escala_calificacion', 'NUMERICA'),
                publicado=data.get('publicado', False)
            )
        else:
            # Para evaluaciones entregables (exámenes, trabajos)
            evaluacion = EvaluacionEntregable.objects.create(
                materia=materia,
                tipo_evaluacion=tipo_evaluacion,
                trimestre=trimestre,
                titulo=data['titulo'],
                descripcion=data.get('descripcion', ''),
                fecha_asignacion=fecha_asignacion,
                fecha_entrega=fecha_entrega,
                fecha_limite=fecha_limite,
                nota_maxima=nota_maxima,
                nota_minima_aprobacion=nota_minima_aprobacion,
                porcentaje_nota_final=data['porcentaje_nota_final'],
                permite_entrega_tardia=data.get('permite_entrega_tardia', False),
                penalizacion_tardio=data.get('penalizacion_tardia', 0.0),
                publicado=data.get('publicado', False)
            )
            
        # Respuesta exitosa
        return Response({
            'mensaje': f'Evaluación "{evaluacion.titulo}" creada correctamente',
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': tipo_evaluacion.get_nombre_display(),
                'materia': materia.nombre,
                'trimestre': trimestre.nombre,
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final)
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_evaluaciones_por_materia(request, materia_id):
    """
    Obtiene todas las evaluaciones de una materia específica.
    """
    try:
        # Verificar materia
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Consultar ambos tipos de evaluaciones
        entregables = EvaluacionEntregable.objects.filter(
            materia=materia, activo=True
        ).select_related('tipo_evaluacion')
        
        participaciones = EvaluacionParticipacion.objects.filter(
            materia=materia, activo=True
        ).select_related('tipo_evaluacion')
        
        # Preparar los datos combinados
        evaluaciones_data = []
        
        # Procesar evaluaciones entregables
        for eval in entregables:
            content_type = ContentType.objects.get_for_model(eval)
            evaluaciones_data.append({
                'id': eval.id,
                'titulo': eval.titulo,
                'tipo_evaluacion': {
                    'id': eval.tipo_evaluacion.id,
                    'nombre': eval.tipo_evaluacion.nombre,
                    'nombre_display': eval.tipo_evaluacion.get_nombre_display()
                },
                'fecha_asignacion': eval.fecha_asignacion,
                'fecha_entrega': eval.fecha_entrega,
                'porcentaje_nota_final': float(eval.porcentaje_nota_final),
                'modelo': 'entregable',
                'content_type_id': content_type.id,
                # otros campos específicos...
            })
        
        # Procesar participaciones
        for eval in participaciones:
            content_type = ContentType.objects.get_for_model(eval)
            evaluaciones_data.append({
                'id': eval.id,
                'titulo': eval.titulo,
                'tipo_evaluacion': {
                    'id': eval.tipo_evaluacion.id,
                    'nombre': eval.tipo_evaluacion.nombre,
                    'nombre_display': eval.tipo_evaluacion.get_nombre_display()
                },
                'fecha_registro': eval.fecha_registro,
                'porcentaje_nota_final': float(eval.porcentaje_nota_final),
                'modelo': 'participacion',
                'content_type_id': content_type.id,
                # otros campos específicos...
            })
        
        # Ordenar por fecha (combinando ambos tipos)
        evaluaciones_data.sort(key=lambda x: x.get('fecha_entrega', x.get('fecha_registro')), reverse=True)
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
            },
            'evaluaciones': evaluaciones_data,
            'total': len(evaluaciones_data)
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_evaluacion(request, evaluacion_id):
    """
    Obtiene los detalles de una evaluación específica.
    """
    try:
        evaluacion = get_evaluacion_by_id(
            evaluacion_id, 
            select_related=['materia', 'tipo_evaluacion']
        )
        
        if not evaluacion:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Campos comunes para ambos tipos
        response_data = {
            'id': evaluacion.id,
            'titulo': evaluacion.titulo,
            'descripcion': evaluacion.descripcion,
            'materia': {
                'id': evaluacion.materia.id,
                'nombre': evaluacion.materia.nombre,
                'curso': str(evaluacion.materia.curso)
            },
            'tipo_evaluacion': {
                'id': evaluacion.tipo_evaluacion.id,
                'nombre': evaluacion.tipo_evaluacion.nombre,
                'nombre_display': evaluacion.tipo_evaluacion.get_nombre_display()
            },
            'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
            'publicado': evaluacion.publicado,
        }
        
        # Propiedades específicas por tipo
        if isinstance(evaluacion, EvaluacionEntregable):
            response_data.update({
                'fecha_asignacion': evaluacion.fecha_asignacion,
                'fecha_entrega': evaluacion.fecha_entrega,
                'fecha_limite': evaluacion.fecha_limite,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                'permite_entrega_tardia': evaluacion.permite_entrega_tardia,
                'penalizacion_tardio': float(evaluacion.penalizacion_tardio),
                'esta_vencido': evaluacion.esta_vencido if hasattr(evaluacion, 'esta_vencido') else False,
                'puede_entregar_tardio': evaluacion.puede_entregar_tardio if hasattr(evaluacion, 'puede_entregar_tardio') else False,
                'tipo': 'entregable'
            })
        elif isinstance(evaluacion, EvaluacionParticipacion):
            response_data.update({
                'fecha_registro': evaluacion.fecha_registro,
                'criterios_participacion': evaluacion.criterios_participacion,
                'escala_calificacion': evaluacion.escala_calificacion,
                'tipo': 'participacion'
            })
        
        # Añadir conteo de calificaciones usando ContentType
        content_type = ContentType.objects.get_for_model(evaluacion)
        calificaciones_count = Calificacion.objects.filter(
            content_type=content_type,
            object_id=evaluacion.id
        ).count()
        response_data['total_calificaciones'] = calificaciones_count
        
        return Response(response_data)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_evaluacion(request, evaluacion_id):
    """
    Actualiza una evaluación existente.
    """
    try:
        evaluacion = get_evaluacion_by_id(evaluacion_id)
        
        if not evaluacion:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Actualizar campos básicos comunes a ambos tipos
        if 'titulo' in data:
            evaluacion.titulo = data['titulo']
        if 'descripcion' in data:
            evaluacion.descripcion = data['descripcion']
        if 'porcentaje_nota_final' in data:
            evaluacion.porcentaje_nota_final = data['porcentaje_nota_final']
        if 'publicado' in data:
            evaluacion.publicado = data['publicado']
        
        # Actualizar campos específicos según el tipo
        if isinstance(evaluacion, EvaluacionEntregable):
            if 'nota_maxima' in data:
                evaluacion.nota_maxima = data['nota_maxima']
            if 'nota_minima_aprobacion' in data:
                evaluacion.nota_minima_aprobacion = data['nota_minima_aprobacion']
                
            # Validar rango de notas
            if hasattr(evaluacion, 'nota_minima_aprobacion') and hasattr(evaluacion, 'nota_maxima'):
                if evaluacion.nota_minima_aprobacion > evaluacion.nota_maxima:
                    return Response(
                        {'error': 'La nota mínima de aprobación no puede ser mayor que la nota máxima'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Actualizar fechas para evaluaciones entregables
            if 'fecha_entrega' in data:
                try:
                    evaluacion.fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha de entrega inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if 'fecha_limite' in data:
                try:
                    evaluacion.fecha_limite = datetime.strptime(data['fecha_limite'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha límite inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        elif isinstance(evaluacion, EvaluacionParticipacion):
            if 'criterios_participacion' in data:
                evaluacion.criterios_participacion = data['criterios_participacion']
            if 'escala_calificacion' in data:
                evaluacion.escala_calificacion = data['escala_calificacion']
            if 'fecha_registro' in data:
                try:
                    evaluacion.fecha_registro = datetime.strptime(data['fecha_registro'], '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha de registro inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        evaluacion.save()
        
        return Response({
            'mensaje': f'Evaluación "{evaluacion.titulo}" actualizada correctamente',
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': 'entregable' if isinstance(evaluacion, EvaluacionEntregable) else 'participacion',
                'publicado': evaluacion.publicado
            }
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_evaluacion(request, evaluacion_id):
    """
    Elimina (desactiva) una evaluación.
    """
    try:
        evaluacion = get_evaluacion_by_id(evaluacion_id)
        
        if not evaluacion:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si tiene calificaciones
        content_type = ContentType.objects.get_for_model(evaluacion)
        tiene_calificaciones = Calificacion.objects.filter(
            content_type=content_type,
            object_id=evaluacion.id
        ).exists()
        
        if tiene_calificaciones:
            return Response(
                {'error': 'No se puede eliminar una evaluación que ya tiene calificaciones registradas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        titulo = evaluacion.titulo
        evaluacion.activo = False
        evaluacion.save()
        
        return Response({
            'mensaje': f'Evaluación "{titulo}" eliminada correctamente'
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_tipo_evaluacion(request):
    """
    Crea un nuevo tipo de evaluación.
    
    Request body:
    {
        "nombre": "PROYECTO",
        "descripcion": "Proyectos a largo plazo con entregables específicos"
    }
    """
    try:
        data = request.data
        
        # Validaciones básicas
        campos_requeridos = ['nombre', 'descripcion']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar nombre (debe ser en mayúsculas y único)
        nombre = data['nombre'].upper()
        if TipoEvaluacion.objects.filter(nombre=nombre).exists():
            return Response(
                {'error': f'Ya existe un tipo de evaluación con el nombre {nombre}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el tipo de evaluación
        tipo_evaluacion = TipoEvaluacion.objects.create(
            nombre=nombre,
            descripcion=data['descripcion']
        )
        
        return Response({
            'mensaje': f'Tipo de evaluación "{tipo_evaluacion.nombre}" creado correctamente',
            'tipo_evaluacion': {
                'id': tipo_evaluacion.id,
                'nombre': tipo_evaluacion.nombre,
                'descripcion': tipo_evaluacion.descripcion
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tipo_evaluacion(request, tipo_id):
    """
    Obtiene los detalles de un tipo de evaluación específico.
    """
    try:
        try:
            tipo = TipoEvaluacion.objects.get(id=tipo_id)
        except TipoEvaluacion.DoesNotExist:
            return Response(
                {'error': 'Tipo de evaluación no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Contar evaluaciones de ambos tipos
        evaluaciones_count = get_evaluaciones_count({'tipo_evaluacion': tipo})
        
        return Response({
            'id': tipo.id,
            'nombre': tipo.nombre,
            'nombre_display': tipo.get_nombre_display(),
            'descripcion': tipo.descripcion,
            'activo': tipo.activo,
            'created_at': tipo.created_at,
            'updated_at': tipo.updated_at,
            'evaluaciones_count': evaluaciones_count
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_tipo_evaluacion(request, tipo_id):
    """
    Actualiza un tipo de evaluación existente.
    
    Request body:
    {
        "descripcion": "Descripción actualizada",
        "activo": true
    }
    """
    try:
        try:
            tipo = TipoEvaluacion.objects.get(id=tipo_id)
        except TipoEvaluacion.DoesNotExist:
            return Response(
                {'error': 'Tipo de evaluación no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Actualizar campos modificables
        if 'descripcion' in data:
            tipo.descripcion = data['descripcion']
            
        if 'activo' in data:
            tipo.activo = data['activo']
        
        # Si se va a desactivar, verificar que no tenga evaluaciones pendientes
        if 'activo' in data and not data['activo']:
            evaluaciones_activas = get_evaluaciones_count({
                'tipo_evaluacion': tipo, 
                'activo': True
            })
            
            if evaluaciones_activas > 0:
                return Response(
                    {'error': f'No se puede desactivar este tipo porque tiene {evaluaciones_activas} evaluaciones activas'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        tipo.save()
        
        return Response({
            'mensaje': f'Tipo de evaluación "{tipo.nombre}" actualizado correctamente',
            'tipo_evaluacion': {
                'id': tipo.id,
                'nombre': tipo.nombre,
                'descripcion': tipo.descripcion,
                'activo': tipo.activo,
                'updated_at': tipo.updated_at
            }
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_tipo_evaluacion(request, tipo_id):
    """
    Elimina (o desactiva) un tipo de evaluación.
    """
    try:
        try:
            tipo = TipoEvaluacion.objects.get(id=tipo_id)
        except TipoEvaluacion.DoesNotExist:
            return Response(
                {'error': 'Tipo de evaluación no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si tiene evaluaciones asociadas
        evaluaciones = get_evaluaciones_count({'tipo_evaluacion': tipo})
        
        if evaluaciones > 0:
            # Si tiene evaluaciones, solo desactivarlo
            tipo.activo = False
            tipo.save()
            return Response({
                'mensaje': f'Tipo de evaluación "{tipo.nombre}" desactivado correctamente (tiene {evaluaciones} evaluaciones asociadas)',
                'desactivado': True
            })
        else:
            # Si no tiene evaluaciones, eliminarlo completamente
            nombre = tipo.nombre
            tipo.delete()
            return Response({
                'mensaje': f'Tipo de evaluación "{nombre}" eliminado completamente',
                'eliminado': True
            })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_evaluaciones_por_curso(request, curso_id):
    """
    Obtiene todas las evaluaciones de las materias asociadas a un curso específico.
    Opcionalmente filtra por trimestre_id (query param) y tipo_evaluacion_id (query param).
    """
    try:
        # Verificar curso
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return Response(
                {'error': f'Curso con ID {curso_id} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las materias del curso
        materias = Materia.objects.filter(curso=curso)
        
        if not materias.exists():
            return Response({
                'mensaje': f'El curso {curso} no tiene materias asignadas',
                'curso': {
                    'id': curso.id,
                    'nombre': str(curso)
                },
                'evaluaciones': [],
                'total': 0
            })
        
        # Parámetros opcionales de filtro
        trimestre_id = request.query_params.get('trimestre_id')
        tipo_evaluacion_id = request.query_params.get('tipo_evaluacion_id')
        
        # Filtros base para ambas consultas
        filtros_entregables = {'materia__in': materias, 'activo': True}
        filtros_participacion = {'materia__in': materias, 'activo': True}
        
        # Aplicar filtros opcionales
        if trimestre_id:
            try:
                trimestre = Trimestre.objects.get(id=trimestre_id)
                filtros_entregables['trimestre'] = trimestre
                filtros_participacion['trimestre'] = trimestre
            except Trimestre.DoesNotExist:
                return Response(
                    {'error': f'Trimestre con ID {trimestre_id} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if tipo_evaluacion_id:
            try:
                tipo_evaluacion = TipoEvaluacion.objects.get(id=tipo_evaluacion_id)
                filtros_entregables['tipo_evaluacion'] = tipo_evaluacion
                filtros_participacion['tipo_evaluacion'] = tipo_evaluacion
            except TipoEvaluacion.DoesNotExist:
                return Response(
                    {'error': f'Tipo de evaluación con ID {tipo_evaluacion_id} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Consultar ambos tipos de evaluaciones
        entregables = EvaluacionEntregable.objects.filter(
            **filtros_entregables
        ).select_related('materia', 'tipo_evaluacion', 'trimestre')
        
        participaciones = EvaluacionParticipacion.objects.filter(
            **filtros_participacion
        ).select_related('materia', 'tipo_evaluacion', 'trimestre')
        
        # Preparar los datos combinados
        evaluaciones_data = []
        
        # Procesar evaluaciones entregables
        for eval in entregables:
            content_type = ContentType.objects.get_for_model(eval)
            evaluaciones_data.append({
                'id': eval.id,
                'titulo': eval.titulo,
                'materia': {
                    'id': eval.materia.id,
                    'nombre': eval.materia.nombre
                },
                'trimestre': {
                    'id': eval.trimestre.id,
                    'nombre': eval.trimestre.nombre,
                    'numero': eval.trimestre.numero,
                    'año_academico': eval.trimestre.año_academico
                },
                'tipo_evaluacion': {
                    'id': eval.tipo_evaluacion.id,
                    'nombre': eval.tipo_evaluacion.nombre,
                    'nombre_display': eval.tipo_evaluacion.get_nombre_display()
                },
                'fecha_asignacion': eval.fecha_asignacion,
                'fecha_entrega': eval.fecha_entrega,
                'porcentaje_nota_final': float(eval.porcentaje_nota_final),
                'modelo': 'entregable',
                'content_type_id': content_type.id,
                'esta_vencido': eval.esta_vencido if hasattr(eval, 'esta_vencido') else (eval.fecha_entrega < datetime.now().date()),
                'publicado': eval.publicado
            })
        
        # Procesar participaciones
        for eval in participaciones:
            content_type = ContentType.objects.get_for_model(eval)
            evaluaciones_data.append({
                'id': eval.id,
                'titulo': eval.titulo,
                'materia': {
                    'id': eval.materia.id,
                    'nombre': eval.materia.nombre
                },
                'trimestre': {
                    'id': eval.trimestre.id,
                    'nombre': eval.trimestre.nombre,
                    'numero': eval.trimestre.numero,
                    'año_academico': eval.trimestre.año_academico
                },
                'tipo_evaluacion': {
                    'id': eval.tipo_evaluacion.id,
                    'nombre': eval.tipo_evaluacion.nombre,
                    'nombre_display': eval.tipo_evaluacion.get_nombre_display()
                },
                'fecha_registro': eval.fecha_registro,
                'porcentaje_nota_final': float(eval.porcentaje_nota_final),
                'modelo': 'participacion',
                'content_type_id': content_type.id,
                'publicado': eval.publicado
            })
        
        # Ordenar evaluaciones (criterio combinado)
        evaluaciones_data.sort(
            key=lambda x: (
                x['trimestre']['año_academico'], 
                x['trimestre']['numero'], 
                x.get('fecha_entrega', x.get('fecha_registro', datetime.now().date()))
            ), 
            reverse=True
        )
        
        # Agrupar por materias para la respuesta
        materias_dict = {}
        for materia in materias:
            materias_dict[materia.id] = {
                'id': materia.id,
                'nombre': materia.nombre,
                'profesor': materia.profesor.get_full_name() if materia.profesor else 'Sin profesor asignado',
                'evaluaciones': []
            }
        
        # Asignar evaluaciones a sus materias
        for eval_data in evaluaciones_data:
            materia_id = eval_data['materia']['id'] 
            if materia_id in materias_dict:
                materias_dict[materia_id]['evaluaciones'].append(eval_data)
        
        # Convertir a lista para la respuesta
        materias_con_evaluaciones = list(materias_dict.values())
        
        # Contar total de evaluaciones
        total_evaluaciones = sum(len(m['evaluaciones']) for m in materias_con_evaluaciones)
        
        return Response({
            'curso': {
                'id': curso.id,
                'nombre': str(curso),
                'grado': curso.grado,
                'paralelo': curso.paralelo,
                'nivel': {
                    'id': curso.nivel.id,
                    'nombre': curso.nivel.nombre
                }
            },
            'filtros_aplicados': {
                'trimestre_id': trimestre_id,
                'tipo_evaluacion_id': tipo_evaluacion_id
            },
            'materias': materias_con_evaluaciones,
            'total_materias': len(materias),
            'total_evaluaciones': total_evaluaciones
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
