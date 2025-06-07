from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.db.models import Prefetch, Q
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from decimal import Decimal

from Usuarios.models import Usuario
from ..models import Curso, Materia, EvaluacionEntregable, EvaluacionParticipacion, Calificacion, Asistencia, TipoEvaluacion, Trimestre, PromedioTrimestral
from ..utils import get_evaluacion_by_id, get_evaluaciones_activas

@api_view(['GET'])
def obtener_materias_estudiante(request):
    """
    Obtiene las materias del estudiante basado en su curso.
    
    GET /api/cursos/estudiante/materias/?estudiante_id=1
    """
    try:
        # Obtener el ID del estudiante desde la consulta
        estudiante_id = request.query_params.get('estudiante_id')
        if not estudiante_id:
            return Response(
                {'error': 'Se requiere el ID del estudiante'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener el usuario
        try:
            usuario = Usuario.objects.get(id=estudiante_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que tenga un curso asignado
        if not usuario.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener el curso
        curso = Curso.objects.get(id=usuario.curso.id)
        
        # Obtener materias del curso
        materias = Materia.objects.filter(curso=curso).select_related('profesor')
        
        # Preparar la respuesta
        curso_data = {
            'id': curso.id,
            'nombre': str(curso),
            'nivel': {
                'id': curso.nivel.id,
                'nombre': curso.nivel.nombre
            } if curso.nivel else None,
            'materias': []
        }
        
        # Agregar materias al response
        for materia in materias:
            materia_data = {
                'id': materia.id,
                'nombre': materia.nombre,
                'profesor': None
            }
            
            # Agregar información del profesor si existe
            if materia.profesor:
                try:
                    materia_data['profesor'] = {
                        'id': materia.profesor.id,
                        'nombre': materia.profesor.nombre,
                        'apellido': materia.profesor.apellido
                    }
                except AttributeError:
                    # Si hay algún problema accediendo a los campos del profesor
                    pass
            
            curso_data['materias'].append(materia_data)
        
        return Response(curso_data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def obtener_estudiante_curso_materias(request, estudiante_id):
    """
    Consultar el curso y materias de un estudiante específico.
    
    GET /api/cursos/estudiantes/{estudiante_id}/curso-materias/
    """
    try:
        # Obtener el estudiante
        try:
            estudiante_usuario = Usuario.objects.get(id=estudiante_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Verificar que tenga un curso asignado
        if not estudiante_usuario.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Obtener el curso
        curso = Curso.objects.get(id=estudiante_usuario.curso.id)
        
        # Obtener materias del curso con información del profesor
        materias = Materia.objects.filter(curso=curso).select_related('profesor')
        
        # Formatear el nombre del curso
        nombre_curso = f"{curso.grado}° {curso.paralelo}"
        
        # Preparar la respuesta
        estudiante_data = {
            'id': estudiante_usuario.id,
            'nombre': estudiante_usuario.nombre,
            'apellido': estudiante_usuario.apellido,
            'codigo': estudiante_usuario.codigo,
            'curso': {
                'id': curso.id,
                'nombre': nombre_curso,
                'nivel': {
                    'id': curso.nivel.id,
                    'nombre': curso.nivel.nombre
                } if curso.nivel else None,
                'materias': []
            }
        }
        
        # Agregar materias con información del profesor
        for materia in materias:
            materia_data = {
                'id': materia.id,
                'nombre': materia.nombre,
                'profesor': None  # Por defecto es None
            }
            
            # Añadir información del profesor si existe
            if materia.profesor:
                try:
                    materia_data['profesor'] = {
                        'id': materia.profesor.id,
                        'nombre': materia.profesor.nombre,
                        'apellido': materia.profesor.apellido,
                        # Puedes añadir más campos del profesor si es necesario
                        'nombre_completo': f"{materia.profesor.nombre} {materia.profesor.apellido}"
                    }
                except AttributeError:
                    # Si hay algún problema accediendo a los campos del profesor
                    pass
            
            estudiante_data['curso']['materias'].append(materia_data)
        
        return Response(estudiante_data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def obtener_evaluaciones_estudiante(request, estudiante_id):
    """
    Obtiene todas las evaluaciones y calificaciones de un estudiante.
    
    GET /api/cursos/estudiantes/{estudiante_id}/evaluaciones/
    Parámetros opcionales:
    - materia_id: Filtra por materia específica
    - trimestre_id: Filtra por trimestre específico
    """
    try:
        # Obtener el estudiante
        try:
            estudiante = Usuario.objects.get(id=estudiante_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que tenga un curso asignado
        if not estudiante.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtros adicionales
        materia_id = request.query_params.get('materia_id')
        trimestre_id = request.query_params.get('trimestre_id')
        
        # Construir filtros para las evaluaciones
        filtros_evaluacion = Q(materia__curso=estudiante.curso)
        
        if materia_id:
            filtros_evaluacion &= Q(materia_id=materia_id)
            
        if trimestre_id:
            filtros_evaluacion &= Q(trimestre_id=trimestre_id)
        
        # Obtener evaluaciones de ambos tipos
        evaluaciones_entregables = EvaluacionEntregable.objects.filter(
            filtros_evaluacion
        ).select_related('tipo_evaluacion', 'materia', 'trimestre')
        
        evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
            filtros_evaluacion
        ).select_related('tipo_evaluacion', 'materia', 'trimestre')
        
        # Preparar ContentTypes para consultas de calificaciones
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Preparar la respuesta
        resultado = []
        
        # Procesar evaluaciones entregables
        for evaluacion in evaluaciones_entregables:
            # Intentar obtener la calificación del estudiante para esta evaluación
            try:
                calificacion = Calificacion.objects.get(
                    content_type=entregable_ct,
                    object_id=evaluacion.id,
                    estudiante=estudiante
                )
                calificacion_data = {
                    'id': calificacion.id,
                    'nota': float(calificacion.nota),
                    'nota_final': float(calificacion.nota_final),
                    'entrega_tardia': calificacion.entrega_tardia,
                    'penalizacion_aplicada': float(calificacion.penalizacion_aplicada),
                    'fecha_entrega': calificacion.fecha_entrega,
                    'observaciones': calificacion.observaciones,
                    'retroalimentacion': calificacion.retroalimentacion,
                    'finalizada': calificacion.finalizada
                }
            except Calificacion.DoesNotExist:
                calificacion_data = None
            
            # Datos de la evaluación
            evaluacion_data = {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'descripcion': evaluacion.descripcion,
                'tipo_evaluacion': {
                    'id': evaluacion.tipo_evaluacion.id,
                    'nombre': evaluacion.tipo_evaluacion.nombre
                } if evaluacion.tipo_evaluacion else None,
                'fecha_asignacion': evaluacion.fecha_asignacion,
                'fecha_entrega': evaluacion.fecha_entrega,
                'fecha_limite': evaluacion.fecha_limite,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'permite_entrega_tardia': evaluacion.permite_entrega_tardia,
                'penalizacion_tardio': float(evaluacion.penalizacion_tardio),
                'activo': evaluacion.activo,
                'publicado': evaluacion.publicado,
                'tipo_objeto': 'entregable',
                'materia': {
                    'id': evaluacion.materia.id,
                    'nombre': evaluacion.materia.nombre
                },
                'trimestre': {
                    'id': evaluacion.trimestre.id,
                    'nombre': evaluacion.trimestre.nombre,
                    'año_academico': evaluacion.trimestre.año_academico
                } if evaluacion.trimestre else None,
                'calificacion': calificacion_data
            }
            
            resultado.append(evaluacion_data)
            
        # Procesar evaluaciones de participación
        for evaluacion in evaluaciones_participacion:
            # Intentar obtener la calificación del estudiante para esta evaluación
            try:
                calificacion = Calificacion.objects.get(
                    content_type=participacion_ct,
                    object_id=evaluacion.id,
                    estudiante=estudiante
                )
                calificacion_data = {
                    'id': calificacion.id,
                    'nota': float(calificacion.nota),
                    'nota_final': float(calificacion.nota_final),
                    'entrega_tardia': calificacion.entrega_tardia,
                    'penalizacion_aplicada': float(calificacion.penalizacion_aplicada),
                    'fecha_entrega': calificacion.fecha_entrega,
                    'observaciones': calificacion.observaciones,
                    'retroalimentacion': calificacion.retroalimentacion,
                    'finalizada': calificacion.finalizada
                }
            except Calificacion.DoesNotExist:
                calificacion_data = None
            
            # Datos de la evaluación (campos específicos para participación)
            evaluacion_data = {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'descripcion': evaluacion.descripcion,
                'tipo_evaluacion': {
                    'id': evaluacion.tipo_evaluacion.id,
                    'nombre': evaluacion.tipo_evaluacion.nombre
                } if evaluacion.tipo_evaluacion else None,
                'fecha_registro': evaluacion.fecha_registro,
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'activo': evaluacion.activo,
                'publicado': evaluacion.publicado,
                'tipo_objeto': 'participacion',
                'materia': {
                    'id': evaluacion.materia.id,
                    'nombre': evaluacion.materia.nombre
                },
                'trimestre': {
                    'id': evaluacion.trimestre.id,
                    'nombre': evaluacion.trimestre.nombre,
                    'año_academico': evaluacion.trimestre.año_academico
                } if evaluacion.trimestre else None,
                'calificacion': calificacion_data
            }
            
            resultado.append(evaluacion_data)
        
        # Ordenar por fecha (primero las más recientes)
        # Ordenamos por fecha_entrega o fecha_registro según el tipo
        resultado.sort(
            key=lambda x: x.get('fecha_entrega', x.get('fecha_registro', '2000-01-01')),
            reverse=True
        )
        
        return Response(resultado)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def obtener_asistencias_estudiante(request, estudiante_id):
    """
    Obtiene el registro de asistencias de un estudiante.
    
    GET /api/cursos/estudiantes/{estudiante_id}/asistencias/
    Parámetros opcionales:
    - materia_id: Filtra por materia específica
    - fecha_inicio: Filtra desde esta fecha (formato YYYY-MM-DD)
    - fecha_fin: Filtra hasta esta fecha (formato YYYY-MM-DD)
    """
    try:
        # Obtener el estudiante
        try:
            estudiante = Usuario.objects.get(id=estudiante_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que tenga un curso asignado
        if not estudiante.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener filtros adicionales
        materia_id = request.query_params.get('materia_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Construir filtros
        filtros = {'estudiante': estudiante}
        
        if materia_id:
            filtros['materia_id'] = materia_id
            
        if fecha_inicio and fecha_fin:
            filtros['fecha__range'] = [fecha_inicio, fecha_fin]
        elif fecha_inicio:
            filtros['fecha__gte'] = fecha_inicio
        elif fecha_fin:
            filtros['fecha__lte'] = fecha_fin
        
        # Obtener asistencias
        asistencias = Asistencia.objects.filter(**filtros).select_related('materia')
        
        # Agrupar por materia para un mejor análisis
        resumen_por_materia = {}
        
        for asistencia in asistencias:
            materia_id = asistencia.materia.id
            materia_nombre = asistencia.materia.nombre
            
            if materia_id not in resumen_por_materia:
                resumen_por_materia[materia_id] = {
                    'id': materia_id,
                    'nombre': materia_nombre,
                    'total_clases': 0,
                    'asistencias': 0,
                    'faltas': 0,
                    'porcentaje_asistencia': 0,
                    'detalle': []
                }
            
            # Actualizar contadores
            resumen_por_materia[materia_id]['total_clases'] += 1
            
            if asistencia.presente:
                resumen_por_materia[materia_id]['asistencias'] += 1
            else:
                resumen_por_materia[materia_id]['faltas'] += 1
            
            # Agregar detalle
            resumen_por_materia[materia_id]['detalle'].append({
                'id': asistencia.id,
                'fecha': asistencia.fecha,
                'presente': asistencia.presente,
                'justificada': asistencia.justificada
            })
        
        # Calcular porcentajes
        for materia_id in resumen_por_materia:
            total = resumen_por_materia[materia_id]['total_clases']
            if total > 0:
                asistencias = resumen_por_materia[materia_id]['asistencias']
                porcentaje = (asistencias / total) * 100
                resumen_por_materia[materia_id]['porcentaje_asistencia'] = round(porcentaje, 2)
        
        # Convertir a lista para la respuesta
        resultado = list(resumen_por_materia.values())
        
        return Response(resultado)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def calcular_promedios_trimestre(request, trimestre_id):
    """
    Calcula los promedios de un trimestre para todas las materias y estudiantes.
    """
    try:
        # Obtener el trimestre
        try:
            trimestre = Trimestre.objects.get(id=trimestre_id)
        except Trimestre.DoesNotExist:
            return Response(
                {'error': 'Trimestre no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Iniciar transacción para mantener consistencia de datos
        with transaction.atomic():
            resultados = []
            
            # Obtener parámetros opcionales
            solo_materia_id = request.data.get('solo_materia_id')
            solo_estudiantes = request.data.get('solo_estudiantes')
            
            # Filtrar materias si es necesario
            materias_query = Materia.objects.all()
            if solo_materia_id:
                materias_query = materias_query.filter(id=solo_materia_id)
            
            # Procesar cada materia
            for materia in materias_query:
                print(f"Procesando materia: {materia.nombre}")
                
                # Obtener estudiantes del curso
                estudiantes = Usuario.objects.filter(
                    curso=materia.curso,
                    rol__nombre='Estudiante'
                ).order_by('apellido', 'nombre')
                
                # Filtrar estudiantes si es necesario
                if solo_estudiantes:
                    estudiantes = estudiantes.filter(id__in=request.data['solo_estudiantes'])
                
                for estudiante in estudiantes:
                    # Obtener evaluaciones del trimestre (ambos tipos)
                    evaluaciones_entregable = EvaluacionEntregable.objects.filter(
                        materia=materia,
                        trimestre=trimestre
                    )
                    
                    evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
                        materia=materia,
                        trimestre=trimestre
                    )
                    
                    # Contenttypes para calificaciones
                    entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
                    participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
                    
                    print(f"Debug - Estudiante: {estudiante.nombre}, Materia: {materia.nombre}")
                    print(f"Debug - Evaluaciones entregables: {evaluaciones_entregable.count()}")
                    print(f"Debug - Evaluaciones participación: {evaluaciones_participacion.count()}")
                    
                    # Combinar evaluaciones y verificar si hay alguna
                    total_evaluaciones = evaluaciones_entregable.count() + evaluaciones_participacion.count()
                    
                    if total_evaluaciones > 0:
                        suma_ponderada = Decimal('0.0')  # ✅ USAR DECIMAL
                        total_porcentaje = Decimal('0.0')  # ✅ USAR DECIMAL
                        calificaciones_encontradas = 0
                        
                        # Procesar evaluaciones entregables
                        for evaluacion in evaluaciones_entregable:
                            try:
                                calificacion = Calificacion.objects.get(
                                    content_type=entregable_ct,
                                    object_id=evaluacion.id,
                                    estudiante=estudiante
                                )
                                
                                # ✅ CORRECCIÓN: Asegurar que todo sea Decimal
                                nota_estudiante = calificacion.nota_final if calificacion.nota_final else calificacion.nota
                                porcentaje_eval = Decimal(str(evaluacion.porcentaje_nota_final))
                                
                                # ✅ CORRECCIÓN: Operaciones con Decimal
                                nota_ponderada = nota_estudiante * (porcentaje_eval / Decimal('100.0'))
                                suma_ponderada += nota_ponderada
                                total_porcentaje += porcentaje_eval
                                calificaciones_encontradas += 1
                                
                                print(f"Debug - Evaluación: {evaluacion.titulo}")
                                print(f"Debug - Nota estudiante: {nota_estudiante}")
                                print(f"Debug - Porcentaje evaluación: {porcentaje_eval}")
                            except Calificacion.DoesNotExist:
                                print(f"No se encontró calificación para {estudiante.nombre} en {evaluacion.titulo}")
                        
                        # Procesar evaluaciones de participación
                        for evaluacion in evaluaciones_participacion:
                            try:
                                calificacion = Calificacion.objects.get(
                                    content_type=participacion_ct,
                                    object_id=evaluacion.id,
                                    estudiante=estudiante
                                )
                                
                                # ✅ CORRECCIÓN: Asegurar que todo sea Decimal
                                nota_estudiante = calificacion.nota_final if calificacion.nota_final else calificacion.nota
                                porcentaje_eval = Decimal(str(evaluacion.porcentaje_nota_final))
                                
                                # ✅ CORRECCIÓN: Operaciones con Decimal
                                nota_ponderada = nota_estudiante * (porcentaje_eval / Decimal('100.0'))
                                suma_ponderada += nota_ponderada
                                total_porcentaje += porcentaje_eval
                                calificaciones_encontradas += 1
                                
                                print(f"Debug - Evaluación: {evaluacion.titulo}")
                                print(f"Debug - Nota estudiante: {nota_estudiante}")
                                print(f"Debug - Porcentaje evaluación: {porcentaje_eval}")
                            except Calificacion.DoesNotExist:
                                print(f"No se encontró calificación para {estudiante.nombre} en {evaluacion.titulo}")
                        
                        # Calcular promedio de evaluaciones
                        promedio_evaluaciones = Decimal('0.0')
                        if calificaciones_encontradas > 0 and total_porcentaje > 0:
                            # Ajustar al porcentaje total evaluado
                            promedio_evaluaciones = (suma_ponderada / total_porcentaje) * 100
                        
                        # Calcular asistencia
                        asistencias = Asistencia.objects.filter(
                            estudiante=estudiante,
                            materia=materia,
                            fecha__range=[trimestre.fecha_inicio, trimestre.fecha_fin]
                        )
                        
                        total_clases = asistencias.count()
                        asistencias_presentes = asistencias.filter(presente=True).count()
                        porcentaje_asistencia = Decimal('0.0')
                        
                        if total_clases > 0:
                            porcentaje_asistencia = Decimal(asistencias_presentes) / Decimal(total_clases) * 100
                        
                        # Determinar si el estudiante aprueba el trimestre
                        # Verificar asistencia mínima y nota mínima
                        promedio_final = promedio_evaluaciones
                        aprobado = (porcentaje_asistencia >= trimestre.porcentaje_asistencia_minima and 
                                    promedio_final >= trimestre.nota_minima_aprobacion)
                        
                        # Crear o actualizar el promedio trimestral
                        promedio, created = PromedioTrimestral.objects.update_or_create(
                            estudiante=estudiante,
                            materia=materia,
                            trimestre=trimestre,
                            defaults={
                                'promedio_evaluaciones': promedio_evaluaciones,
                                'promedio_final': promedio_final,
                                'total_clases': total_clases,
                                'asistencias': asistencias_presentes,
                                'porcentaje_asistencia': porcentaje_asistencia,
                                'aprobado': aprobado,
                                'calculado_automaticamente': True
                            }
                        )
                        
                        resultados.append({
                            'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
                            'materia': materia.nombre,
                            'promedio_evaluaciones': float(promedio_evaluaciones),
                            'promedio_final': float(promedio_final),
                            'porcentaje_asistencia': float(porcentaje_asistencia),
                            'aprobado': aprobado,
                            'created': created
                        })
        
        return Response({
            'mensaje': f'Promedios calculados para el {trimestre.nombre}',
            'trimestre': str(trimestre),
            'total_procesados': len(resultados),
            'resultados': resultados
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )