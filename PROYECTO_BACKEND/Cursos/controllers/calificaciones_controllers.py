from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.contrib.contenttypes.models import ContentType
from ..models import (Calificacion, EvaluacionEntregable, EvaluacionParticipacion,
                      Materia, TipoEvaluacion)
from Usuarios.models import Usuario


@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_calificacion(request):
    """
    Registra la calificación de un estudiante en una evaluación.
    
    Request body:
    {
        "evaluacion_id": 1,
        "estudiante_id": 2,
        "nota": 85.5,
        "observaciones": "Buen trabajo",
        "retroalimentacion": "Mejorar la presentación",
        "fecha_entrega": "2025-06-15T10:30:00Z",
        "entrega_tardia": false
    }
    """
    try:
        data = request.data
        
        # Validaciones básicas
        campos_requeridos = ['evaluacion_id', 'estudiante_id', 'nota', 'tipo_evaluacion']
        for campo in campos_requeridos:
            if campo not in data:
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener evaluación según su tipo
        tipo_evaluacion = data['tipo_evaluacion']
        evaluacion_id = data['evaluacion_id']
        
        try:
            if tipo_evaluacion == 'entregable':
                evaluacion = EvaluacionEntregable.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionEntregable)
            elif tipo_evaluacion == 'participacion':
                evaluacion = EvaluacionParticipacion.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
            else:
                return Response(
                    {'error': 'Tipo de evaluación no válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (EvaluacionEntregable.DoesNotExist, EvaluacionParticipacion.DoesNotExist):
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener estudiante
        try:
            estudiante = Usuario.objects.get(id=data['estudiante_id'])
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validación de nota
        nota = Decimal(str(data['nota']))
        nota_maxima = evaluacion.nota_maxima if hasattr(evaluacion, 'nota_maxima') else Decimal('100.0')
        
        if nota < 0 or nota > nota_maxima:
            return Response(
                {'error': f'La nota debe estar entre 0 y {nota_maxima}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear o actualizar calificación
        calificacion, created = Calificacion.objects.update_or_create(
            content_type=content_type,
            object_id=evaluacion.id,
            estudiante=estudiante,
            defaults={
                'nota': nota,
                'fecha_entrega': data.get('fecha_entrega'),
                'observaciones': data.get('observaciones', ''),
                'retroalimentacion': data.get('retroalimentacion', ''),
                'finalizada': data.get('finalizada', True),
                'fecha_calificacion': timezone.now()
            }
        )
        
        return Response({
            'mensaje': f'Calificación {"registrada" if created else "actualizada"} correctamente',
            'calificacion': {
                'id': calificacion.id,
                'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
                'evaluacion': evaluacion.titulo,
                'nota': float(calificacion.nota),
                'nota_final': float(calificacion.nota_final),
                'created': created
            }
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_calificaciones_masivo(request):
    """
    Registra calificaciones para múltiples estudiantes de una evaluación.
    """
    try:
        data = request.data
        evaluacion_id = data.get('evaluacion_id')
        tipo_evaluacion = data.get('tipo_evaluacion')  # Nuevo parámetro requerido
        calificaciones_data = data.get('calificaciones', [])
        
        if not evaluacion_id or not tipo_evaluacion or not calificaciones_data:
            return Response(
                {'error': 'Se requiere evaluacion_id, tipo_evaluacion y calificaciones'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener evaluación según su tipo
        try:
            if tipo_evaluacion == 'entregable':
                evaluacion = EvaluacionEntregable.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionEntregable)
                nota_maxima = evaluacion.nota_maxima
                nota_minima_aprobacion = evaluacion.nota_minima_aprobacion
            elif tipo_evaluacion == 'participacion':
                evaluacion = EvaluacionParticipacion.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
                nota_maxima = Decimal('100.0')  # Valor predeterminado
                nota_minima_aprobacion = Decimal('51.0')  # Valor predeterminado
            else:
                return Response(
                    {'error': 'Tipo de evaluación no válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (EvaluacionEntregable.DoesNotExist, EvaluacionParticipacion.DoesNotExist):
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        resultados = []
        
        with transaction.atomic():
            for cal_data in calificaciones_data:
                try:
                    estudiante_id = cal_data.get('estudiante_id')
                    nota = cal_data.get('nota')
                    
                    if not estudiante_id or nota is None:
                        resultados.append({
                            'estudiante_id': estudiante_id,
                            'error': 'Se requiere estudiante_id y nota',
                            'success': False
                        })
                        continue
                    
                    # Obtener estudiante
                    try:
                        estudiante = Usuario.objects.get(id=estudiante_id, rol__nombre='Estudiante')
                    except Usuario.DoesNotExist:
                        resultados.append({
                            'estudiante_id': estudiante_id,
                            'error': 'Estudiante no encontrado',
                            'success': False
                        })
                        continue
                    
                    # Convertir a Decimal
                    nota = Decimal(str(nota))
                    if nota < 0 or nota > nota_maxima:
                        resultados.append({
                            'estudiante_id': estudiante_id,
                            'error': f'Nota fuera del rango válido (0-{nota_maxima})',
                            'success': False
                        })
                        continue
                    
                    # Crear o actualizar calificación
                    calificacion, created = Calificacion.objects.update_or_create(
                        content_type=content_type,
                        object_id=evaluacion.id,
                        estudiante=estudiante,
                        defaults={
                            'nota': nota,
                            'observaciones': cal_data.get('observaciones', ''),
                            'retroalimentacion': cal_data.get('retroalimentacion', ''),
                            'finalizada': True,
                            'fecha_calificacion': timezone.now()
                        }
                    )
                    
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
                        'nota': float(calificacion.nota),
                        'porcentaje': 100.0,  # O el cálculo que corresponda
                        'esta_aprobado': float(calificacion.nota) >= float(nota_minima_aprobacion),
                        'created': created,
                        'success': True
                    })
                
                except Exception as e:
                    resultados.append({
                        'estudiante_id': cal_data.get('estudiante_id'),
                        'error': str(e),
                        'success': False
                    })
        
        exitosos = [r for r in resultados if r['success']]
        errores = [r for r in resultados if not r['success']]
        
        return Response({
            'evaluacion': evaluacion.titulo,
            'total_procesados': len(calificaciones_data),
            'exitosos': len(exitosos),
            'errores': len(errores),
            'resultados': resultados
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_calificaciones_por_evaluacion(request, evaluacion_id):
    """
    Obtiene todas las calificaciones de una evaluación específica.
    """
    try:
        # Determinar el tipo de evaluación desde el query param
        tipo_evaluacion = request.GET.get('tipo', 'entregable')
        
        try:
            if tipo_evaluacion == 'entregable':
                evaluacion = EvaluacionEntregable.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionEntregable)
                nota_minima_aprobacion = evaluacion.nota_minima_aprobacion
            else:  # tipo_evaluacion == 'participacion'
                evaluacion = EvaluacionParticipacion.objects.get(id=evaluacion_id)
                content_type = ContentType.objects.get_for_model(EvaluacionParticipacion)
                nota_minima_aprobacion = Decimal('51.0')  # Valor predeterminado
        except (EvaluacionEntregable.DoesNotExist, EvaluacionParticipacion.DoesNotExist):
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        calificaciones = Calificacion.objects.filter(
            content_type=content_type,
            object_id=evaluacion.id
        ).select_related('estudiante').order_by('estudiante__apellido', 'estudiante__nombre')
        
        calificaciones_data = []
        for calificacion in calificaciones:
            # Quitar 'nota_sobre' del diccionario
            calificaciones_data.append({
                'id': calificacion.id,
                'estudiante': {
                    'id': calificacion.estudiante.id,
                    'nombre': f"{calificacion.estudiante.nombre} {calificacion.estudiante.apellido}",
                    'codigo': calificacion.estudiante.codigo
                },
                'nota': float(calificacion.nota),
                # Calculamos directamente
                'nota_final': float(calificacion.nota),  # Ahora nota = nota_final
                'porcentaje': 100.0,  # O el porcentaje que corresponda
                'esta_aprobado': float(calificacion.nota) >= float(calificacion.evaluacion.nota_minima_aprobacion 
                                                     if hasattr(calificacion.evaluacion, 'nota_minima_aprobacion') 
                                                     else 51.0),
                'fecha_entrega': calificacion.fecha_entrega,
                'entrega_tardia': calificacion.entrega_tardia,
                'penalizacion_aplicada': float(calificacion.penalizacion_aplicada) if hasattr(calificacion, 'penalizacion_aplicada') else 0.0,
                'observaciones': calificacion.observaciones,
                'retroalimentacion': calificacion.retroalimentacion,
                'finalizada': calificacion.finalizada,
                'fecha_calificacion': calificacion.fecha_calificacion
            })
        
        # Calcular estadísticas
        if calificaciones:
            notas = [float(c.nota_final) for c in calificaciones]
            estadisticas = {
                'total_calificaciones': len(calificaciones),
                'promedio': round(sum(notas) / len(notas), 2),
                'nota_maxima': max(notas),
                'nota_minima': min(notas),
                'aprobados': len([n for n in notas if n >= float(nota_minima_aprobacion)]),
                'reprobados': len([n for n in notas if n < float(nota_minima_aprobacion)]),
                'nota_minima_aprobacion': float(nota_minima_aprobacion)
            }
        else:
            estadisticas = {
                'total_calificaciones': 0,
                'promedio': 0,
                'nota_maxima': 0,
                'nota_minima': 0,
                'aprobados': 0,
                'reprobados': 0,
                'nota_minima_aprobacion': float(nota_minima_aprobacion)
            }
        
        # Determinar los campos específicos según el tipo
        if tipo_evaluacion == 'entregable':
            eval_data = {
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                'fecha_entrega': evaluacion.fecha_entrega
            }
        else:
            eval_data = {
                'nota_maxima': 100.0,
                'nota_minima_aprobacion': 51.0,
                'fecha_registro': evaluacion.fecha_registro
            }
            
        return Response({
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                'materia': evaluacion.materia.nombre,
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                **eval_data
            },
            'calificaciones': calificaciones_data,
            'estadisticas': estadisticas
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ✅ MANTENER: Resto de métodos sin cambios significativos
@api_view(['GET'])
@permission_classes([AllowAny])
def get_calificaciones_por_estudiante(request, estudiante_id):
    """
    Obtiene todas las calificaciones de un estudiante específico.
    """
    try:
        try:
            estudiante = Usuario.objects.get(id=estudiante_id, rol__nombre='Estudiante')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener parámetros de filtro
        materia_id = request.GET.get('materia_id')
        tipo_evaluacion_nombre = request.GET.get('tipo_evaluacion')
        
        # Obtener todas las calificaciones del estudiante
        calificaciones = Calificacion.objects.filter(estudiante=estudiante)
        
        # Definir los content types para cada tipo de evaluación
        content_type_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
        content_type_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        calificaciones_data = []
        
        # Procesar cada calificación y obtener su evaluación correspondiente
        for calificacion in calificaciones:
            # Determinar qué tipo de evaluación es
            if calificacion.content_type_id == content_type_entregable.id:
                try:
                    evaluacion = EvaluacionEntregable.objects.get(id=calificacion.object_id)
                    # Aplicar filtros específicos
                    if materia_id and str(evaluacion.materia.id) != materia_id:
                        continue
                    if tipo_evaluacion_nombre and evaluacion.tipo_evaluacion.nombre != tipo_evaluacion_nombre:
                        continue
                    
                    calificaciones_data.append({
                        'id': calificacion.id,
                        'evaluacion': {
                            'id': evaluacion.id,
                            'titulo': evaluacion.titulo,
                            'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                            'materia': evaluacion.materia.nombre,
                            'fecha_entrega': evaluacion.fecha_entrega,
                            'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final)
                        },
                        'nota': float(calificacion.nota),
                        'nota_final': float(calificacion.nota),
                        'porcentaje': 100.0,
                        'esta_aprobado': float(calificacion.nota) >= float(evaluacion.nota_minima_aprobacion),
                        'entrega_tardia': calificacion.entrega_tardia,
                        'observaciones': calificacion.observaciones,
                        'retroalimentacion': calificacion.retroalimentacion,
                        'fecha_calificacion': calificacion.fecha_calificacion
                    })
                except EvaluacionEntregable.DoesNotExist:
                    continue
                    
            elif calificacion.content_type_id == content_type_participacion.id:
                try:
                    evaluacion = EvaluacionParticipacion.objects.get(id=calificacion.object_id)
                    # Aplicar filtros específicos
                    if materia_id and str(evaluacion.materia.id) != materia_id:
                        continue
                    if tipo_evaluacion_nombre and evaluacion.tipo_evaluacion.nombre != tipo_evaluacion_nombre:
                        continue
                    
                    calificaciones_data.append({
                        'id': calificacion.id,
                        'evaluacion': {
                            'id': evaluacion.id,
                            'titulo': evaluacion.titulo,
                            'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                            'materia': evaluacion.materia.nombre,
                            'fecha_registro': evaluacion.fecha_registro,
                            'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final)
                        },
                        'nota': float(calificacion.nota),
                        'nota_final': float(calificacion.nota),
                        'porcentaje': 100.0,
                        'esta_aprobado': float(calificacion.nota) >= 51.0,  # Valor por defecto
                        'entrega_tardia': calificacion.entrega_tardia,
                        'observaciones': calificacion.observaciones,
                        'retroalimentacion': calificacion.retroalimentacion,
                        'fecha_calificacion': calificacion.fecha_calificacion
                    })
                except EvaluacionParticipacion.DoesNotExist:
                    continue
        
        # Ordenar por fecha (descendente)
        calificaciones_data.sort(
            key=lambda x: (x['evaluacion'].get('fecha_entrega') or 
                           x['evaluacion'].get('fecha_registro')),
            reverse=True
        )
        
        return Response({
            'estudiante': {
                'id': estudiante.id,
                'nombre': f"{estudiante.nombre} {estudiante.apellido}",
                'codigo': estudiante.codigo
            },
            'calificaciones': calificaciones_data,
            'total': len(calificaciones_data)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reporte_calificaciones_materia(request, materia_id):
    """
    Genera un reporte completo de calificaciones por materia.
    """
    try:
        from ..utils import get_evaluaciones_activas
        
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': 'Materia no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener estudiantes del curso
        estudiantes = Usuario.objects.filter(
            curso=materia.curso,
            rol__nombre='Estudiante'
        ).order_by('apellido', 'nombre')
        
        # Obtener evaluaciones de la materia (ambos tipos)
        # Se elimina el filtro de publicado=True
        evaluaciones_entregable = EvaluacionEntregable.objects.filter(
            materia=materia,
            activo=True
            # publicado=True  <-- Se eliminó esta línea
        )
        evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
            materia=materia,
            activo=True
            # publicado=True  <-- Se eliminó esta línea
        )
        
        # Combinar y ordenar todas las evaluaciones
        evaluaciones = list(evaluaciones_entregable) + list(evaluaciones_participacion)
        # Ordenar por fecha (primero intentar fecha_asignacion, luego fecha_registro)
        evaluaciones.sort(key=lambda x: getattr(x, 'fecha_asignacion', getattr(x, 'fecha_registro', None)))
        
        # Construir reporte
        reporte_data = []
        content_types = {
            'entregable': ContentType.objects.get_for_model(EvaluacionEntregable),
            'participacion': ContentType.objects.get_for_model(EvaluacionParticipacion)
        }
        
        for estudiante in estudiantes:
            estudiante_data = {
                'estudiante': {
                    'id': estudiante.id,
                    'nombre': f"{estudiante.nombre} {estudiante.apellido}",
                    'codigo': estudiante.codigo
                },
                'calificaciones': {},
                'promedio_final': 0.0,
                'total_porcentaje': 0.0,
                'esta_aprobado': False
            }
            
            # Inicializar variables como Decimal
            suma_ponderada = Decimal('0')
            total_porcentaje = Decimal('0')
            
            for evaluacion in evaluaciones:
                # Determinar el tipo y ContentType para la evaluación
                if isinstance(evaluacion, EvaluacionEntregable):
                    content_type = content_types['entregable']
                    nota_minima = evaluacion.nota_minima_aprobacion
                else:
                    content_type = content_types['participacion']
                    nota_minima = Decimal('51.0')  # Valor por defecto
                
                try:
                    calificacion = Calificacion.objects.get(
                        content_type=content_type,
                        object_id=evaluacion.id,
                        estudiante=estudiante
                    )
                    
                    # Ahora todas las operaciones son entre Decimal
                    nota_ponderada = (calificacion.nota * evaluacion.porcentaje_nota_final) / Decimal('100')
                    suma_ponderada += nota_ponderada
                    total_porcentaje += evaluacion.porcentaje_nota_final
                    
                    estudiante_data['calificaciones'][str(evaluacion.id)] = {
                        'nota': float(calificacion.nota),
                        'porcentaje': 100.0,  # O cálculo directo según tu lógica
                        'esta_aprobado': float(calificacion.nota) >= float(nota_minima),
                        'entrega_tardia': calificacion.entrega_tardia
                    }
                except Calificacion.DoesNotExist:
                    estudiante_data['calificaciones'][str(evaluacion.id)] = {
                        'nota': None,
                        'porcentaje': None,
                        'esta_aprobado': False,
                        'entrega_tardia': False
                    }
            
            # Calcular promedio final si hay evaluaciones
            if total_porcentaje > Decimal('0'):
                promedio = (suma_ponderada / total_porcentaje) * Decimal('100')
                estudiante_data['promedio_final'] = round(float(promedio), 2)  # Convertir a float solo para la respuesta
                estudiante_data['esta_aprobado'] = promedio >= Decimal('51.0')
            else:
                estudiante_data['promedio_final'] = 0.0
                estudiante_data['esta_aprobado'] = False
            
            estudiante_data['total_porcentaje'] = float(total_porcentaje)  # Convertir a float solo para la respuesta
            reporte_data.append(estudiante_data)
        
        # Información de evaluaciones para el frontend
        evaluaciones_info = []
        for evaluacion in evaluaciones:
            eval_data = {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
            }
            
            # Añadir campos específicos según tipo
            if isinstance(evaluacion, EvaluacionEntregable):
                eval_data.update({
                    'fecha_entrega': evaluacion.fecha_entrega,
                    'nota_maxima': float(evaluacion.nota_maxima),
                    'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                    'tipo_objeto': 'entregable'
                })
            else:
                eval_data.update({
                    'fecha_registro': evaluacion.fecha_registro,
                    'nota_maxima': 100.0,
                    'nota_minima_aprobacion': 51.0,
                    'tipo_objeto': 'participacion'
                })
                
            evaluaciones_info.append(eval_data)
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
            },
            'evaluaciones': evaluaciones_info,
            'estudiantes': reporte_data,
            'total_estudiantes': len(reporte_data),
            'total_evaluaciones': len(evaluaciones),
            'nota_minima_aprobacion_general': 51.0
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )