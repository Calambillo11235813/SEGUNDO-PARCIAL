from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Prefetch, Q
from Usuarios.models import Usuario
from ..models import Curso, Materia, Evaluacion, Calificacion, Asistencia, TipoEvaluacion

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
        
        # Obtener materias del curso
        materias = Materia.objects.filter(curso=curso)
        
        # Preparar la respuesta
        estudiante_data = {
            'id': estudiante_usuario.id,
            'nombre': estudiante_usuario.nombre,
            'apellido': estudiante_usuario.apellido,
            'codigo': estudiante_usuario.codigo,
            'curso': {
                'id': curso.id,
                'nombre': str(curso),
                'nivel': {
                    'id': curso.nivel.id,
                    'nombre': curso.nivel.nombre
                } if curso.nivel else None,
                'materias': [{
                    'id': materia.id,
                    'nombre': materia.nombre
                } for materia in materias]
            }
        }
        
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
        
        # Obtener evaluaciones
        evaluaciones = Evaluacion.objects.filter(filtros_evaluacion).select_related('tipo_evaluacion', 'materia', 'trimestre')
        
        # Preparar la respuesta
        resultado = []
        
        for evaluacion in evaluaciones:
            # Intentar obtener la calificación del estudiante para esta evaluación
            try:
                calificacion = Calificacion.objects.get(evaluacion=evaluacion, estudiante=estudiante)
                calificacion_data = {
                    'id': calificacion.id,
                    'nota': calificacion.nota,
                    'nota_final': calificacion.nota_final,
                    'entrega_tardia': calificacion.entrega_tardia,
                    'penalizacion_aplicada': calificacion.penalizacion_aplicada,
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
                'nota_maxima': evaluacion.nota_maxima,
                'nota_minima_aprobacion': evaluacion.nota_minima_aprobacion,
                'porcentaje_nota_final': evaluacion.porcentaje_nota_final,
                'permite_entrega_tardia': evaluacion.permite_entrega_tardia,
                'penalizacion_tardio': evaluacion.penalizacion_tardio,
                'activo': evaluacion.activo,
                'publicado': evaluacion.publicado,
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