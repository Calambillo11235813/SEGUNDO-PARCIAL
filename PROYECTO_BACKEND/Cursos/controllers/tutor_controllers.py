import logging

# Configurar el logger
logger = logging.getLogger(__name__)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # Cambiar por permisos adecuados en producción
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from Usuarios.models import Usuario, Tutor, Estudiante
from ..models import (Calificacion, EvaluacionEntregable, EvaluacionParticipacion,
                     Materia, Trimestre, PromedioTrimestral, Asistencia)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_estudiantes_tutor(request, tutor_id):
    """
    Obtiene la lista de estudiantes asignados a un tutor específico.
    """
    logger.info(f"Iniciando obtener_estudiantes_tutor para tutor_id: {tutor_id}")
    
    try:
        # Verificar que el tutor existe
        try:
            # Verificar primero si el usuario existe
            try:
                usuario = Usuario.objects.get(id=tutor_id)
                logger.info(f"Usuario encontrado: {usuario.nombre} {usuario.apellido}")
                
                # Verificar si el rol es de tutor
                if usuario.rol and usuario.rol.nombre == 'Tutor':
                    # Intentar obtener el tutor
                    try:
                        tutor = Tutor.objects.get(usuario_id=tutor_id)
                        logger.info(f"Tutor encontrado: {tutor}")
                    except Tutor.DoesNotExist:
                        # El usuario tiene rol de tutor pero no existe en la tabla Tutor
                        # Crear el registro automáticamente
                        logger.warning(f"Usuario {usuario.nombre} {usuario.apellido} tiene rol Tutor pero no existe registro en tabla Tutor. Creando...")
                        tutor = Tutor.objects.create(usuario=usuario)
                        logger.info(f"Tutor creado automáticamente: {tutor}")
                else:
                    # El usuario no tiene rol de tutor
                    rol_nombre = usuario.rol.nombre if usuario.rol else "Sin rol asignado"
                    logger.error(f"El usuario {usuario.nombre} {usuario.apellido} no tiene rol de Tutor. Rol actual: {rol_nombre}")
                    return Response(
                        {'error': f'El usuario no es un Tutor. Rol actual: {rol_nombre}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
            except Usuario.DoesNotExist:
                logger.error(f"No existe un usuario con id={tutor_id}")
                return Response(
                    {'error': f'No existe un usuario con id={tutor_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            logger.error(f"Error al verificar tutor: {str(e)}")
            return Response(
                {'error': f'Error al verificar tutor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Obtener estudiantes asignados al tutor
        logger.info(f"Obteniendo estudiantes para el tutor {tutor_id}")
        estudiantes = tutor.estudiantes.all().select_related('usuario')
        logger.info(f"Total estudiantes encontrados: {estudiantes.count()}")
        
        # Si no hay estudiantes asignados
        if not estudiantes.exists():
            logger.warning(f"El tutor {tutor_id} no tiene estudiantes asignados")
            return Response({
                'tutor': {
                    'id': tutor.usuario.id,
                    'nombre': tutor.usuario.nombre,
                    'apellido': tutor.usuario.apellido
                },
                'estudiantes': [],
                'total': 0,
                'mensaje': 'No hay estudiantes asignados a este tutor'
            })
        
        # Preparar la respuesta
        estudiantes_data = []
        for i, estudiante in enumerate(estudiantes):
            logger.info(f"Procesando estudiante {i+1}/{estudiantes.count()}: {estudiante}")
            try:
                curso_info = {
                    'id': estudiante.curso.id,
                    'nombre': str(estudiante.curso)
                } if estudiante.curso else None
                
                estudiante_data = {
                    'id': estudiante.usuario.id,
                    'codigo': estudiante.usuario.codigo,
                    'nombre': estudiante.usuario.nombre,
                    'apellido': estudiante.usuario.apellido,
                    'curso': curso_info
                }
                estudiantes_data.append(estudiante_data)
                logger.info(f"Estudiante {estudiante.usuario.id} procesado con éxito")
            except Exception as e:
                logger.error(f"Error procesando estudiante {estudiante}: {str(e)}")
        
        logger.info(f"Respuesta preparada con {len(estudiantes_data)} estudiantes")
        return Response({
            'tutor': {
                'id': tutor.usuario.id,
                'nombre': tutor.usuario.nombre,
                'apellido': tutor.usuario.apellido
            },
            'estudiantes': estudiantes_data,
            'total': len(estudiantes_data)
        })
        
    except Exception as e:
        logger.exception(f"Error en obtener_estudiantes_tutor: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_calificaciones_estudiantes(request, tutor_id):
    """
    Obtiene las calificaciones de todos los estudiantes asignados a un tutor.
    
    Parámetros de filtrado:
    - trimestre_id: Filtra por un trimestre específico
    - materia_id: Filtra por una materia específica
    - año_academico: Filtra por un año académico específico (NUEVO)
    """
    try:
        # Verificar que el tutor existe
        try:
            tutor = Tutor.objects.get(usuario_id=tutor_id)
        except Tutor.DoesNotExist:
            return Response(
                {'error': 'Tutor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener estudiantes asignados al tutor
        estudiantes = tutor.estudiantes.all().select_related('usuario')
        
        if not estudiantes.exists():
            return Response({
                'tutor': {
                    'id': tutor.usuario.id,
                    'nombre': tutor.usuario.nombre,
                    'apellido': tutor.usuario.apellido
                },
                'estudiantes': [],
                'mensaje': 'No hay estudiantes asignados a este tutor'
            })
        
        # Obtener parámetros de filtro
        trimestre_id = request.query_params.get('trimestre_id')
        materia_id = request.query_params.get('materia_id')
        año_academico = request.query_params.get('año_academico')  # Nuevo parámetro
        
        # Preparar ContentTypes para consultas
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Preparar resultado
        resultado = []
        
        # Para cada estudiante
        for estudiante in estudiantes:
            estudiante_data = {
                'id': estudiante.usuario.id,
                'codigo': estudiante.usuario.codigo,
                'nombre': estudiante.usuario.nombre,
                'apellido': estudiante.usuario.apellido,
                'nombre_completo': f"{estudiante.usuario.nombre} {estudiante.usuario.apellido}",
                'curso': {
                    'id': estudiante.curso.id,
                    'nombre': str(estudiante.curso)
                } if estudiante.curso else None,
                'materias': []
            }
            
            # Si el estudiante no tiene curso asignado, continuar con el siguiente
            if not estudiante.curso:
                resultado.append(estudiante_data)
                continue
            
            # Filtrar materias según parámetros
            materias = Materia.objects.filter(curso=estudiante.curso)
            if materia_id:
                materias = materias.filter(id=materia_id)
            
            # Para cada materia
            for materia in materias:
                materia_data = {
                    'id': materia.id,
                    'nombre': materia.nombre,
                    'trimestres': []
                }
                
                # Filtrar trimestres según parámetros
                trimestres = Trimestre.objects.all()
                
                # Aplicar filtro por año académico si se proporciona
                if año_academico:
                    trimestres = trimestres.filter(año_academico=año_academico)
                
                # Aplicar filtro por trimestre_id si se proporciona
                if trimestre_id:
                    trimestres = trimestres.filter(id=trimestre_id)
                
                # Para cada trimestre
                for trimestre in trimestres:
                    trimestre_data = {
                        'id': trimestre.id,
                        'nombre': trimestre.nombre,
                        'año_academico': trimestre.año_academico
                    }
                    
                    # Intentar obtener promedio calculado
                    try:
                        promedio = PromedioTrimestral.objects.get(
                            estudiante=estudiante.usuario,
                            materia=materia,
                            trimestre=trimestre
                        )
                        
                        trimestre_data['promedio'] = float(promedio.promedio_final)
                        trimestre_data['aprobado'] = promedio.aprobado
                        trimestre_data['asistencia'] = float(promedio.porcentaje_asistencia)
                        
                    except PromedioTrimestral.DoesNotExist:
                        # Calcular el promedio en tiempo real
                        
                        # Obtener evaluaciones para la materia en este trimestre
                        evaluaciones_entregable = EvaluacionEntregable.objects.filter(
                            materia=materia, 
                            trimestre=trimestre
                        )
                        
                        evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
                            materia=materia,
                            trimestre=trimestre
                        )
                        
                        # Variables para cálculos
                        suma_ponderada = Decimal('0.0')
                        total_porcentaje = Decimal('0.0')
                        calificaciones_encontradas = 0
                        
                        # Procesar evaluaciones entregables
                        for evaluacion in evaluaciones_entregable:
                            try:
                                calificacion = Calificacion.objects.get(
                                    content_type=entregable_ct,
                                    object_id=evaluacion.id,
                                    estudiante=estudiante.usuario
                                )
                                
                                nota_estudiante = calificacion.calcular_nota_con_penalizacion()
                                porcentaje_eval = Decimal(str(evaluacion.porcentaje_nota_final))
                                
                                nota_ponderada = nota_estudiante * (porcentaje_eval / Decimal('100.0'))
                                suma_ponderada += nota_ponderada
                                total_porcentaje += porcentaje_eval
                                calificaciones_encontradas += 1
                            except Calificacion.DoesNotExist:
                                pass
                        
                        # Procesar evaluaciones de participación
                        for evaluacion in evaluaciones_participacion:
                            try:
                                calificacion = Calificacion.objects.get(
                                    content_type=participacion_ct,
                                    object_id=evaluacion.id,
                                    estudiante=estudiante.usuario
                                )
                                
                                nota_estudiante = calificacion.calcular_nota_con_penalizacion()
                                porcentaje_eval = Decimal(str(evaluacion.porcentaje_nota_final))
                                
                                nota_ponderada = nota_estudiante * (porcentaje_eval / Decimal('100.0'))
                                suma_ponderada += nota_ponderada
                                total_porcentaje += porcentaje_eval
                                calificaciones_encontradas += 1
                            except Calificacion.DoesNotExist:
                                pass
                        
                        # Calcular promedio de evaluaciones
                        promedio_evaluaciones = Decimal('0.0')
                        if calificaciones_encontradas > 0 and total_porcentaje > 0:
                            promedio_evaluaciones = (suma_ponderada / total_porcentaje) * 100
                        
                        # Calcular asistencia
                        asistencias = Asistencia.objects.filter(
                            estudiante=estudiante.usuario,
                            materia=materia,
                            fecha__range=[trimestre.fecha_inicio, trimestre.fecha_fin]
                        )
                        
                        total_clases = asistencias.count()
                        asistencias_presentes = asistencias.filter(presente=True).count()
                        porcentaje_asistencia = Decimal('0.0')
                        
                        if total_clases > 0:
                            porcentaje_asistencia = Decimal(asistencias_presentes) / Decimal(total_clases) * 100
                        
                        # Determinar si el estudiante aprueba el trimestre
                        aprobado = (porcentaje_asistencia >= trimestre.porcentaje_asistencia_minima and 
                                    promedio_evaluaciones >= trimestre.nota_minima_aprobacion)
                        
                        # Agregar a datos del trimestre
                        trimestre_data['promedio'] = float(promedio_evaluaciones)
                        trimestre_data['aprobado'] = aprobado
                        trimestre_data['asistencia'] = float(porcentaje_asistencia)
                        trimestre_data['calculado_tiempo_real'] = True
                    
                    # Añadir datos del trimestre a la materia
                    materia_data['trimestres'].append(trimestre_data)
                
                # Ordenar trimestres por año académico descendente
                materia_data['trimestres'].sort(key=lambda x: (x['año_academico'], x['id']), reverse=True)
                
                # Añadir materia a estudiante
                estudiante_data['materias'].append(materia_data)
            
            # Ordenar materias por nombre
            estudiante_data['materias'].sort(key=lambda x: x['nombre'])
            
            # Añadir estudiante al resultado
            resultado.append(estudiante_data)
        
        # Ordenar estudiantes por apellido, nombre
        resultado.sort(key=lambda x: (x['apellido'], x['nombre']))
        
        return Response({
            'tutor': {
                'id': tutor.usuario.id,
                'nombre': tutor.usuario.nombre,
                'apellido': tutor.usuario.apellido
            },
            'estudiantes': resultado,
            'total_estudiantes': len(resultado)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_calificaciones_estudiante_detalle(request, tutor_id, estudiante_id):
    """
    Obtiene las calificaciones detalladas de un estudiante específico asignado a un tutor.
    """
    try:
        # Verificar que el tutor existe y que el estudiante está asignado a él
        try:
            tutor = Tutor.objects.get(usuario_id=tutor_id)
        except Tutor.DoesNotExist:
            return Response(
                {'error': 'Tutor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el estudiante existe
        try:
            estudiante = Estudiante.objects.get(usuario_id=estudiante_id)
        except Estudiante.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el estudiante está asignado al tutor
        if not tutor.estudiantes.filter(usuario_id=estudiante_id).exists():
            return Response(
                {'error': 'Este estudiante no está asignado a este tutor'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener parámetros de filtro
        materia_id = request.query_params.get('materia_id')
        trimestre_id = request.query_params.get('trimestre_id')
        tipo_evaluacion_id = request.query_params.get('tipo_evaluacion_id')
        año_academico = request.query_params.get('año_academico')  # NUEVO PARÁMETRO
        
        # ContentTypes para consultas
        entregable_ct = ContentType.objects.get_for_model(EvaluacionEntregable)
        participacion_ct = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        # Filtrar calificaciones
        calificaciones = Calificacion.objects.filter(estudiante=estudiante.usuario)
        
        # Preparar datos del estudiante
        estudiante_data = {
            'id': estudiante.usuario.id,
            'codigo': estudiante.usuario.codigo,
            'nombre': estudiante.usuario.nombre,
            'apellido': estudiante.usuario.apellido,
            'curso': {
                'id': estudiante.curso.id,
                'nombre': str(estudiante.curso)
            } if estudiante.curso else None,
            'materias': []
        }
        
        # Si el estudiante no tiene curso, devolver datos básicos
        if not estudiante.curso:
            return Response({
                'tutor': {
                    'id': tutor.usuario.id,
                    'nombre': tutor.usuario.nombre,
                    'apellido': tutor.usuario.apellido
                },
                'estudiante': estudiante_data,
                'mensaje': 'El estudiante no tiene curso asignado'
            })
        
        # Filtrar materias según parámetros
        materias = Materia.objects.filter(curso=estudiante.curso)
        if materia_id:
            materias = materias.filter(id=materia_id)
        
        # Para cada materia
        for materia in materias:
            materia_data = {
                'id': materia.id,
                'nombre': materia.nombre,
                'profesor': None,
                'evaluaciones': []
            }
            
            # Añadir información del profesor si existe
            if hasattr(materia, 'profesor') and materia.profesor:
                materia_data['profesor'] = {
                    'id': materia.profesor.id,
                    'nombre': materia.profesor.nombre,
                    'apellido': materia.profesor.apellido,
                    'nombre_completo': f"{materia.profesor.nombre} {materia.profesor.apellido}"
                }
            
            # Filtrar evaluaciones según parámetros
            filtros_evaluacion = {'materia': materia}
            
            if trimestre_id:
                filtros_evaluacion['trimestre_id'] = trimestre_id
                
            if tipo_evaluacion_id:
                filtros_evaluacion['tipo_evaluacion_id'] = tipo_evaluacion_id
            
            # NUEVO: Filtrar por año académico
            if año_academico:
                filtros_evaluacion['trimestre__año_academico'] = año_academico
            
            # Obtener evaluaciones
            evaluaciones_entregable = EvaluacionEntregable.objects.filter(
                **filtros_evaluacion
            ).select_related('tipo_evaluacion', 'trimestre')
            
            evaluaciones_participacion = EvaluacionParticipacion.objects.filter(
                **filtros_evaluacion
            ).select_related('tipo_evaluacion', 'trimestre')
            
            # Procesar evaluaciones entregables
            for evaluacion in evaluaciones_entregable:
                # Intentar obtener la calificación
                try:
                    calificacion = Calificacion.objects.get(
                        content_type=entregable_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante.usuario
                    )
                    
                    calificacion_data = {
                        'id': calificacion.id,
                        'nota': float(calificacion.nota),
                        'nota_final': float(calificacion.calcular_nota_con_penalizacion()),
                        'porcentaje': float(evaluacion.porcentaje_nota_final),
                        'fecha_entrega': calificacion.fecha_entrega,
                        'finalizada': calificacion.finalizada,
                        'observaciones': calificacion.observaciones,
                        'retroalimentacion': calificacion.retroalimentacion
                    }
                except Calificacion.DoesNotExist:
                    calificacion_data = None
                
                # Datos de la evaluación
                evaluacion_data = {
                    'id': evaluacion.id,
                    'titulo': evaluacion.titulo,
                    'descripcion': evaluacion.descripcion,
                    'tipo': 'entregable',
                    'tipo_evaluacion': {
                        'id': evaluacion.tipo_evaluacion.id,
                        'nombre': evaluacion.tipo_evaluacion.nombre
                    } if evaluacion.tipo_evaluacion else None,
                    'fecha_asignacion': evaluacion.fecha_asignacion,
                    'fecha_entrega': evaluacion.fecha_entrega,
                    'fecha_limite': evaluacion.fecha_limite,
                    'trimestre': {
                        'id': evaluacion.trimestre.id,
                        'nombre': evaluacion.trimestre.nombre,
                        'año_academico': evaluacion.trimestre.año_academico
                    } if evaluacion.trimestre else None,
                    'nota_maxima': float(evaluacion.nota_maxima),
                    'calificacion': calificacion_data
                }
                
                materia_data['evaluaciones'].append(evaluacion_data)
            
            # Procesar evaluaciones de participación
            for evaluacion in evaluaciones_participacion:
                # Intentar obtener la calificación
                try:
                    calificacion = Calificacion.objects.get(
                        content_type=participacion_ct,
                        object_id=evaluacion.id,
                        estudiante=estudiante.usuario
                    )
                    
                    calificacion_data = {
                        'id': calificacion.id,
                        'nota': float(calificacion.nota),
                        'nota_final': float(calificacion.calcular_nota_con_penalizacion()),
                        'porcentaje': float(evaluacion.porcentaje_nota_final),
                        'finalizada': calificacion.finalizada,
                        'observaciones': calificacion.observaciones,
                        'retroalimentacion': calificacion.retroalimentacion
                    }
                except Calificacion.DoesNotExist:
                    calificacion_data = None
                
                # Datos de la evaluación
                evaluacion_data = {
                    'id': evaluacion.id,
                    'titulo': evaluacion.titulo,
                    'descripcion': evaluacion.descripcion,
                    'tipo': 'participacion',
                    'tipo_evaluacion': {
                        'id': evaluacion.tipo_evaluacion.id,
                        'nombre': evaluacion.tipo_evaluacion.nombre
                    } if evaluacion.tipo_evaluacion else None,
                    'fecha_registro': evaluacion.fecha_registro,
                    'trimestre': {
                        'id': evaluacion.trimestre.id,
                        'nombre': evaluacion.trimestre.nombre,
                        'año_academico': evaluacion.trimestre.año_academico
                    } if evaluacion.trimestre else None,
                    'calificacion': calificacion_data
                }
                
                materia_data['evaluaciones'].append(evaluacion_data)
            
            # Ordenar evaluaciones por fecha (primero las más recientes)
            materia_data['evaluaciones'].sort(
                key=lambda x: x.get('fecha_entrega', x.get('fecha_registro', '2000-01-01')),
                reverse=True
            )
            
            # Añadir materia a estudiante
            estudiante_data['materias'].append(materia_data)
        
        # Ordenar materias por nombre
        estudiante_data['materias'].sort(key=lambda x: x['nombre'])
        
        return Response({
            'tutor': {
                'id': tutor.usuario.id,
                'nombre': tutor.usuario.nombre,
                'apellido': tutor.usuario.apellido
            },
            'estudiante': estudiante_data
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])  # Considera cambiar a IsAuthenticated en producción
def asignar_estudiantes_tutor(request, tutor_id):
    """
    Asigna uno o varios estudiantes a un tutor específico.
    
    Parámetros esperados en el cuerpo de la petición:
    {
        "estudiantes": [1, 2, 3]  // Lista de IDs de estudiantes a asignar
    }
    
    También se pueden usar los siguientes parámetros opcionales:
    {
        "reemplazar_existentes": true/false,  // Si es true, elimina asignaciones previas
        "curso_id": 5  // Para asignar todos los estudiantes de un curso
    }
    """
    logger.info(f"Iniciando asignar_estudiantes_tutor para tutor_id: {tutor_id}")
    
    try:
        # Verificar que el tutor existe
        try:
            # Verificar primero si el usuario existe
            try:
                usuario = Usuario.objects.get(id=tutor_id)
                logger.info(f"Usuario encontrado: {usuario.nombre} {usuario.apellido}")
                
                # Verificar si el rol es de tutor
                if usuario.rol and usuario.rol.nombre == 'Tutor':
                    # Intentar obtener el tutor
                    try:
                        tutor = Tutor.objects.get(usuario_id=tutor_id)
                        logger.info(f"Tutor encontrado: {tutor}")
                    except Tutor.DoesNotExist:
                        # El usuario tiene rol de tutor pero no existe en la tabla Tutor
                        # Crear el registro automáticamente
                        logger.warning(f"Usuario {usuario.nombre} {usuario.apellido} tiene rol Tutor pero no existe registro en tabla Tutor. Creando...")
                        tutor = Tutor.objects.create(usuario=usuario)
                        logger.info(f"Tutor creado automáticamente: {tutor}")
                else:
                    # El usuario no tiene rol de tutor
                    rol_nombre = usuario.rol.nombre if usuario.rol else "Sin rol asignado"
                    logger.error(f"El usuario {usuario.nombre} {usuario.apellido} no tiene rol de Tutor. Rol actual: {rol_nombre}")
                    return Response(
                        {'error': f'El usuario no es un Tutor. Rol actual: {rol_nombre}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
            except Usuario.DoesNotExist:
                logger.error(f"No existe un usuario con id={tutor_id}")
                return Response(
                    {'error': f'No existe un usuario con id={tutor_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as e:
            logger.error(f"Error al verificar tutor: {str(e)}")
            return Response(
                {'error': f'Error al verificar tutor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Obtener datos del request
        reemplazar_existentes = request.data.get('reemplazar_existentes', False)
        estudiantes_ids = request.data.get('estudiantes', [])
        curso_id = request.data.get('curso_id')
        
        # Verificar si tenemos al menos una forma de asignar estudiantes
        if not estudiantes_ids and curso_id is None:
            logger.error("No se proporcionaron IDs de estudiantes ni curso_id")
            return Response(
                {'error': 'Debe proporcionar una lista de IDs de estudiantes o un ID de curso'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Obtener estudiantes actuales para reportar cambios
        estudiantes_previos = list(tutor.estudiantes.all().values_list('usuario_id', flat=True))
        logger.info(f"Estudiantes asignados previamente: {estudiantes_previos}")
        
        # Si se solicita reemplazar, eliminar todas las asignaciones previas
        if reemplazar_existentes:
            logger.info(f"Eliminando asignaciones previas del tutor {tutor_id}")
            tutor.estudiantes.clear()
        
        # Lista para almacenar los estudiantes que se van a asignar
        estudiantes_a_asignar = []
        estudiantes_no_encontrados = []
        estudiantes_creados = []
        
        # Si se proporciona un curso_id, obtener todos los estudiantes de ese curso
        if curso_id is not None:
            logger.info(f"Obteniendo estudiantes del curso {curso_id}")
            try:
                from Cursos.models import Curso
                curso = Curso.objects.get(id=curso_id)
                
                # Obtener usuarios con rol de estudiante en este curso
                usuarios_estudiantes = Usuario.objects.filter(
                    curso=curso, 
                    rol__nombre='Estudiante'
                )
                
                for usuario_est in usuarios_estudiantes:
                    try:
                        estudiante = Estudiante.objects.get(usuario=usuario_est)
                    except Estudiante.DoesNotExist:
                        # Crear registro de estudiante si no existe
                        estudiante = Estudiante.objects.create(usuario=usuario_est)
                        estudiantes_creados.append(estudiante.usuario.id)
                        logger.info(f"Creado registro de Estudiante para usuario {usuario_est.id}: {usuario_est.nombre} {usuario_est.apellido}")
                    
                    estudiantes_a_asignar.append(estudiante)
                
                logger.info(f"Se procesaron {len(estudiantes_a_asignar)} estudiantes del curso {curso_id}")
                    
            except Exception as e:
                logger.error(f"Error al obtener estudiantes del curso {curso_id}: {str(e)}")
                return Response(
                    {'error': f'Error al obtener estudiantes del curso: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        # Procesar lista de IDs de estudiantes
        if estudiantes_ids:
            logger.info(f"Procesando lista de IDs de estudiantes: {estudiantes_ids}")
            for est_id in estudiantes_ids:
                try:
                    # Primero intentamos obtener el registro de Estudiante
                    estudiante = Estudiante.objects.get(usuario_id=est_id)
                    estudiantes_a_asignar.append(estudiante)
                    logger.info(f"Estudiante encontrado con ID {est_id}")
                except Estudiante.DoesNotExist:
                    # Si no existe, verificamos si el usuario existe y tiene rol estudiante
                    try:
                        usuario_est = Usuario.objects.get(id=est_id)
                        
                        if usuario_est.rol and usuario_est.rol.nombre == 'Estudiante':
                            # Crear el registro de estudiante
                            estudiante = Estudiante.objects.create(usuario=usuario_est)
                            estudiantes_a_asignar.append(estudiante)
                            estudiantes_creados.append(est_id)
                            logger.info(f"Creado registro de Estudiante para usuario {est_id}: {usuario_est.nombre} {usuario_est.apellido}")
                        else:
                            # El usuario existe pero no tiene rol de estudiante
                            rol_nombre = usuario_est.rol.nombre if usuario_est.rol else "Sin rol"
                            logger.warning(f"Usuario {est_id} tiene rol {rol_nombre}, no Estudiante")
                            estudiantes_no_encontrados.append({
                                'id': est_id,
                                'motivo': f"El usuario tiene rol {rol_nombre}, no Estudiante"
                            })
                    except Usuario.DoesNotExist:
                        # El usuario no existe
                        estudiantes_no_encontrados.append({
                            'id': est_id,
                            'motivo': "Usuario no encontrado"
                        })
                        logger.warning(f"Usuario con ID {est_id} no encontrado")
        
        # Si no se encontraron estudiantes para asignar
        if not estudiantes_a_asignar and estudiantes_no_encontrados:
            logger.error("No se encontró ningún estudiante para asignar")
            return Response({
                'error': 'No se encontró ningún estudiante para asignar',
                'estudiantes_no_encontrados': estudiantes_no_encontrados
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Asignar estudiantes al tutor
        for estudiante in estudiantes_a_asignar:
            tutor.estudiantes.add(estudiante)
            logger.info(f"Estudiante {estudiante.usuario.nombre} {estudiante.usuario.apellido} (ID:{estudiante.usuario.id}) asignado al tutor {tutor.usuario.nombre} {tutor.usuario.apellido}")
        
        # Obtener estudiantes actuales después de la asignación
        estudiantes_actuales = list(tutor.estudiantes.all().values_list('usuario_id', flat=True))
        
        # Preparar respuesta detallada
        estudiantes_asignados = []
        for estudiante in tutor.estudiantes.all().select_related('usuario'):
            estudiantes_asignados.append({
                'id': estudiante.usuario.id,
                'codigo': estudiante.usuario.codigo,
                'nombre': estudiante.usuario.nombre,
                'apellido': estudiante.usuario.apellido,
                'curso': {
                    'id': estudiante.curso.id,
                    'nombre': str(estudiante.curso)
                } if estudiante.curso else None,
                'recien_asignado': estudiante.usuario.id not in estudiantes_previos,
                'recien_creado': estudiante.usuario.id in estudiantes_creados
            })
        
        return Response({
            'tutor': {
                'id': tutor.usuario.id,
                'nombre': tutor.usuario.nombre,
                'apellido': tutor.usuario.apellido
            },
            'estudiantes': estudiantes_asignados,
            'total_estudiantes': len(estudiantes_asignados),
            'estudiantes_nuevos': len(set(estudiantes_actuales) - set(estudiantes_previos)),
            'estudiantes_creados': len(estudiantes_creados),
            'estudiantes_no_encontrados': estudiantes_no_encontrados
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error en asignar_estudiantes_tutor: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )