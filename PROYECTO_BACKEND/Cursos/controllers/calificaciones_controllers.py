from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count, Q
from ..models import Calificacion, Evaluacion
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
        campos_requeridos = ['evaluacion_id', 'estudiante_id', 'nota']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener evaluación
        try:
            evaluacion = Evaluacion.objects.get(id=data['evaluacion_id'])
        except Evaluacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener estudiante
        try:
            estudiante = Usuario.objects.get(id=data['estudiante_id'], rol__nombre='Estudiante')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ CORREGIDO: Convertir a Decimal para compatibilidad
        nota = Decimal(str(data['nota']))
        if nota < 0 or nota > evaluacion.nota_maxima:
            return Response(
                {'error': f'La nota debe estar entre 0 y {evaluacion.nota_maxima}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular penalización por entrega tardía
        entrega_tardia = data.get('entrega_tardia', False)
        penalizacion_aplicada = Decimal('0.0')
        
        if entrega_tardia and evaluacion.penalizacion_tardio > 0:
            penalizacion_aplicada = evaluacion.penalizacion_tardio
        
        # Crear o actualizar calificación
        calificacion, created = Calificacion.objects.update_or_create(
            evaluacion=evaluacion,
            estudiante=estudiante,
            defaults={
                'nota': nota,
                'nota_sobre': evaluacion.nota_maxima,
                'fecha_entrega': data.get('fecha_entrega'),
                'entrega_tardia': entrega_tardia,
                'penalizacion_aplicada': penalizacion_aplicada,
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
                'porcentaje': round(float(calificacion.porcentaje), 2),
                'esta_aprobado': calificacion.esta_aprobado,
                'penalizacion_aplicada': float(calificacion.penalizacion_aplicada),
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
        calificaciones_data = data.get('calificaciones', [])
        
        if not evaluacion_id or not calificaciones_data:
            return Response(
                {'error': 'Se requiere evaluacion_id y calificaciones'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener evaluación
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
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
                    
                    # ✅ CORREGIDO: Convertir a Decimal
                    nota = Decimal(str(nota))
                    if nota < 0 or nota > evaluacion.nota_maxima:
                        resultados.append({
                            'estudiante_id': estudiante_id,
                            'error': f'Nota fuera del rango válido (0-{evaluacion.nota_maxima})',
                            'success': False
                        })
                        continue
                    
                    # Crear o actualizar calificación
                    calificacion, created = Calificacion.objects.update_or_create(
                        evaluacion=evaluacion,
                        estudiante=estudiante,
                        defaults={
                            'nota': nota,
                            'nota_sobre': evaluacion.nota_maxima,
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
                        'porcentaje': round(float(calificacion.porcentaje), 2),
                        'esta_aprobado': calificacion.esta_aprobado,
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
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        calificaciones = Calificacion.objects.filter(
            evaluacion=evaluacion
        ).select_related('estudiante').order_by('estudiante__apellido', 'estudiante__nombre')
        
        calificaciones_data = []
        for calificacion in calificaciones:
            calificaciones_data.append({
                'id': calificacion.id,
                'estudiante': {
                    'id': calificacion.estudiante.id,
                    'nombre': f"{calificacion.estudiante.nombre} {calificacion.estudiante.apellido}",
                    'codigo': calificacion.estudiante.codigo
                },
                'nota': float(calificacion.nota),
                'nota_sobre': float(calificacion.nota_sobre),
                'nota_final': float(calificacion.nota_final),
                'porcentaje': round(calificacion.porcentaje, 2),
                'esta_aprobado': calificacion.esta_aprobado,
                'fecha_entrega': calificacion.fecha_entrega,
                'entrega_tardia': calificacion.entrega_tardia,
                'penalizacion_aplicada': float(calificacion.penalizacion_aplicada),
                'observaciones': calificacion.observaciones,
                'retroalimentacion': calificacion.retroalimentacion,
                'finalizada': calificacion.finalizada,
                'fecha_calificacion': calificacion.fecha_calificacion
            })
        
        # ✅ ACTUALIZADO: Calcular estadísticas con nota mínima de aprobación 51
        if calificaciones:
            notas = [float(c.nota_final) for c in calificaciones]
            estadisticas = {
                'total_calificaciones': len(calificaciones),
                'promedio': round(sum(notas) / len(notas), 2),
                'nota_maxima': max(notas),
                'nota_minima': min(notas),
                'aprobados': len([n for n in notas if n >= evaluacion.nota_minima_aprobacion]),
                'reprobados': len([n for n in notas if n < evaluacion.nota_minima_aprobacion]),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion)
            }
        else:
            estadisticas = {
                'total_calificaciones': 0,
                'promedio': 0,
                'nota_maxima': 0,
                'nota_minima': 0,
                'aprobados': 0,
                'reprobados': 0,
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion)
            }
        
        return Response({
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                'materia': evaluacion.materia.nombre,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final)
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
        
        # Filtros opcionales
        materia_id = request.GET.get('materia_id')
        tipo_evaluacion = request.GET.get('tipo_evaluacion')
        
        filtros = {'estudiante': estudiante}
        if materia_id:
            filtros['evaluacion__materia_id'] = materia_id
        if tipo_evaluacion:
            filtros['evaluacion__tipo_evaluacion__nombre'] = tipo_evaluacion
        
        calificaciones = Calificacion.objects.filter(
            **filtros
        ).select_related(
            'evaluacion__materia', 
            'evaluacion__tipo_evaluacion'
        ).order_by('-evaluacion__fecha_asignacion')
        
        calificaciones_data = []
        for calificacion in calificaciones:
            calificaciones_data.append({
                'id': calificacion.id,
                'evaluacion': {
                    'id': calificacion.evaluacion.id,
                    'titulo': calificacion.evaluacion.titulo,
                    'tipo': calificacion.evaluacion.tipo_evaluacion.get_nombre_display(),
                    'materia': calificacion.evaluacion.materia.nombre,
                    'fecha_entrega': calificacion.evaluacion.fecha_entrega,
                    'porcentaje_nota_final': float(calificacion.evaluacion.porcentaje_nota_final)
                },
                'nota': float(calificacion.nota),
                'nota_sobre': float(calificacion.nota_sobre),
                'nota_final': float(calificacion.nota_final),
                'porcentaje': round(calificacion.porcentaje, 2),
                'esta_aprobado': calificacion.esta_aprobado,
                'entrega_tardia': calificacion.entrega_tardia,
                'penalizacion_aplicada': float(calificacion.penalizacion_aplicada),
                'observaciones': calificacion.observaciones,
                'retroalimentacion': calificacion.retroalimentacion,
                'fecha_calificacion': calificacion.fecha_calificacion
            })
        
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
        from ..models import Materia
        
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
        
        # Obtener evaluaciones de la materia
        evaluaciones = Evaluacion.objects.filter(
            materia=materia,
            activo=True,
            publicado=True
        ).order_by('fecha_asignacion')
        
        # Construir reporte
        reporte_data = []
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
            
            suma_ponderada = 0.0
            total_porcentaje = 0.0
            
            for evaluacion in evaluaciones:
                try:
                    calificacion = Calificacion.objects.get(
                        evaluacion=evaluacion,
                        estudiante=estudiante
                    )
                    
                    nota_ponderada = (calificacion.nota_final * evaluacion.porcentaje_nota_final) / 100
                    suma_ponderada += nota_ponderada
                    total_porcentaje += evaluacion.porcentaje_nota_final
                    
                    estudiante_data['calificaciones'][str(evaluacion.id)] = {
                        'nota': float(calificacion.nota_final),
                        'porcentaje': round(calificacion.porcentaje, 2),
                        'esta_aprobado': calificacion.esta_aprobado,
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
            if total_porcentaje > 0:
                promedio = (suma_ponderada / total_porcentaje) * 100
                estudiante_data['promedio_final'] = round(promedio, 2)
                # ✅ ACTUALIZADO: Verificar aprobación con nota mínima 51
                estudiante_data['esta_aprobado'] = promedio >= 51.0
            else:
                estudiante_data['promedio_final'] = 0.0
                estudiante_data['esta_aprobado'] = False
            
            estudiante_data['total_porcentaje'] = float(total_porcentaje)
            reporte_data.append(estudiante_data)
        
        # Información de evaluaciones para el frontend
        evaluaciones_info = []
        for evaluacion in evaluaciones:
            evaluaciones_info.append({
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                'fecha_entrega': evaluacion.fecha_entrega,
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion)
            })
        
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