# En Cursos/controllers/asistencia_controllers.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # Cambiar por permisos adecuados en producción
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from ..models import Asistencia, Materia
from Usuarios.models import Usuario

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_asistencia(request):
    """
    Registra la asistencia de un estudiante para una materia específica.
    
    Request body:
    {
        "materia_id": 1,
        "estudiante_id": 2,
        "fecha": "2025-05-25",  # Opcional, usa la fecha actual por defecto
        "presente": true,
        "justificada": false
    }
    """
    try:
        data = request.data
        materia_id = data.get('materia_id')
        estudiante_id = data.get('estudiante_id')
        fecha_str = data.get('fecha')
        presente = data.get('presente', True)
        justificada = data.get('justificada', False)
       
        
        # Validaciones básicas
        if not materia_id or not estudiante_id:
            return Response(
                {'error': 'Se requiere materia_id y estudiante_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener la materia
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': f'No existe materia con id {materia_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener el estudiante
        try:
            estudiante = Usuario.objects.get(id=estudiante_id)
            # Verificar que sea un estudiante (ajustar según tu modelo)
            if not hasattr(estudiante, 'rol') or estudiante.rol.nombre != 'Estudiante':
                return Response(
                    {'error': 'El usuario especificado no es un estudiante'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'No existe estudiante con id {estudiante_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el estudiante pertenezca al curso de la materia
        if estudiante.curso != materia.curso:
            return Response(
                {'error': 'El estudiante no pertenece al curso de esta materia'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # También verificar que el estudiante tenga un curso asignado
        if not estudiante.curso:
            return Response(
                {'error': 'El estudiante no tiene un curso asignado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesar fecha (usar fecha actual si no se proporciona)
        fecha = timezone.now().date()
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Crear o actualizar la asistencia (sin el campo observacion/ausente)
        asistencia, created = Asistencia.objects.update_or_create(
            estudiante=estudiante,
            materia=materia,
            fecha=fecha,
            defaults={
                'presente': presente,
                'justificada': justificada
            }
        )
        
        # Preparar respuesta
        return Response({
            'id': asistencia.id,
            'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
            'materia': materia.nombre,
            'curso': str(materia.curso),
            'fecha': fecha,
            'presente': presente,
            'justificada': justificada,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_asistencias_masivo(request):
    """
    Registra asistencias de múltiples estudiantes para una materia en una fecha específica.
    
    Request body:
    {
        "materia_id": 1,
        "fecha": "2025-05-25",  # Opcional
        "asistencias": [
            {"estudiante_id": 1, "presente": true},
            {"estudiante_id": 2, "presente": false, "justificada": true}
        ]
    }
    """
    try:
        data = request.data
        materia_id = data.get('materia_id')
        fecha_str = data.get('fecha')
        asistencias_data = data.get('asistencias', [])
        
        # Validaciones básicas
        if not materia_id:
            return Response(
                {'error': 'Se requiere materia_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not asistencias_data:
            return Response(
                {'error': 'No se proporcionaron datos de asistencia'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener la materia
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': f'No existe materia con id {materia_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Procesar fecha
        fecha = timezone.now().date()
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Registrar asistencias en una transacción
        resultados = []
        with transaction.atomic():
            for asistencia_data in asistencias_data:
                estudiante_id = asistencia_data.get('estudiante_id')
                presente = asistencia_data.get('presente', True)
                justificada = asistencia_data.get('justificada', False)
                # Eliminada la referencia a observacion/ausente
                
                # Obtener estudiante
                try:
                    estudiante = Usuario.objects.get(id=estudiante_id)
                    # Verificar que sea estudiante
                    if not hasattr(estudiante, 'rol') or estudiante.rol.nombre != 'Estudiante':
                        resultados.append({
                            'estudiante_id': estudiante_id,
                            'error': 'El usuario no es un estudiante',
                            'success': False
                        })
                        continue
                except Usuario.DoesNotExist:
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'error': 'Estudiante no encontrado',
                        'success': False
                    })
                    continue
                
                # Verificar que pertenezca al curso
                if not estudiante.curso:
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'error': 'El estudiante no tiene un curso asignado',
                        'success': False
                    })
                    continue

                if estudiante.curso != materia.curso:
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'error': 'El estudiante no pertenece al curso de esta materia',
                        'success': False
                    })
                    continue
                
                # Crear o actualizar asistencia
                try:
                    asistencia, created = Asistencia.objects.update_or_create(
                        estudiante=estudiante,
                        materia=materia,
                        fecha=fecha,
                        defaults={
                            'presente': presente,
                            'justificada': justificada
                        }
                    )
                    
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
                        'presente': presente,
                        'justificada': justificada,
                        'created': created,
                        'success': True
                    })
                except Exception as e:
                    resultados.append({
                        'estudiante_id': estudiante_id,
                        'error': str(e),
                        'success': False
                    })
        
        # Preparar respuesta
        return Response({
            'materia': materia.nombre,
            'curso': str(materia.curso),
            'fecha': fecha,
            'resultados': resultados
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_asistencias_por_materia(request, materia_id):
    """
    Obtiene las asistencias de una materia, opcionalmente filtradas por fecha.
    
    Query params:
    - fecha: YYYY-MM-DD (opcional, para una fecha específica)
    - desde: YYYY-MM-DD (opcional, fecha inicio)
    - hasta: YYYY-MM-DD (opcional, fecha fin)
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': f'No existe materia con id {materia_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Construir filtros de fecha
        filtros = {'materia': materia}
        
        fecha = request.query_params.get('fecha')
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        
        if fecha:
            try:
                filtros['fecha'] = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if desde:
                try:
                    filtros['fecha__gte'] = datetime.strptime(desde, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha desde inválido. Usar YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if hasta:
                try:
                    filtros['fecha__lte'] = datetime.strptime(hasta, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Formato de fecha hasta inválido. Usar YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Obtener asistencias
        asistencias = Asistencia.objects.filter(**filtros)
        
        # Organizar por fecha
        resultado_por_fecha = {}
        for asistencia in asistencias:
            fecha_str = asistencia.fecha.strftime('%Y-%m-%d')
            if fecha_str not in resultado_por_fecha:
                resultado_por_fecha[fecha_str] = []
            
            resultado_por_fecha[fecha_str].append({
                'id': asistencia.id,
                'estudiante_id': asistencia.estudiante.id,
                'estudiante': f"{asistencia.estudiante.nombre} {asistencia.estudiante.apellido}",
                'presente': asistencia.presente,
                'justificada': asistencia.justificada
                # Eliminada la referencia a observacion/ausente
            })
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': {
                    'id': materia.curso.id,
                    'nombre': str(materia.curso)
                }
            },
            'asistencias': resultado_por_fecha
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_estudiantes_por_materia(request, materia_id):
    """
    Obtiene la lista de estudiantes que deberían asistir a una materia,
    basándose en los estudiantes asignados al curso de la materia.
    """
    try:
        # Verificar que la materia existe
        try:
            materia = Materia.objects.get(id=materia_id)
        except Materia.DoesNotExist:
            return Response(
                {'error': f'No existe materia con id {materia_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener curso asociado a la materia
        curso = materia.curso
        
        # Obtener estudiantes del curso usando la nueva relación
        estudiantes = Usuario.objects.filter(curso=curso, rol__nombre='Estudiante')
        
        if not estudiantes.exists():
            return Response({
                'materia': {
                    'id': materia.id, 
                    'nombre': materia.nombre
                },
                'curso': {
                    'id': curso.id,
                    'nombre': str(curso)
                },
                'estudiantes': [],
                'advertencia': 'No hay estudiantes asignados a este curso'
            })
        
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
            'materia': {
                'id': materia.id, 
                'nombre': materia.nombre
            },
            'curso': {
                'id': curso.id,
                'nombre': str(curso)
            },
            'estudiantes': estudiantes_data
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )