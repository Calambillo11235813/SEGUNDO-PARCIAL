from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date
from ..models import Evaluacion, TipoEvaluacion, Materia
from Usuarios.models import Usuario

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
    
    Request body:
    {
        "materia_id": 1,
        "tipo_evaluacion_id": 1,
        "titulo": "Examen Parcial 1",
        "descripcion": "Examen sobre los primeros 3 capítulos",
        "fecha_asignacion": "2025-06-01",
        "fecha_entrega": "2025-06-15",
        "fecha_limite": "2025-06-17",
        "nota_maxima": 100.0,
        "nota_minima_aprobacion": 51.0,
        "porcentaje_nota_final": 25.0,
        "permite_entrega_tardia": true,
        "penalizacion_tardio": 10.0
    }
    """
    try:
        data = request.data
        
        # Validaciones básicas
        campos_requeridos = ['materia_id', 'tipo_evaluacion_id', 'titulo', 'fecha_asignacion', 'fecha_entrega', 'porcentaje_nota_final']
        for campo in campos_requeridos:
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
        
        # Validar fechas
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
        
        # Crear evaluación
        evaluacion = Evaluacion.objects.create(
            materia=materia,
            tipo_evaluacion=tipo_evaluacion,
            titulo=data['titulo'],
            descripcion=data.get('descripcion', ''),
            fecha_asignacion=fecha_asignacion,
            fecha_entrega=fecha_entrega,
            fecha_limite=fecha_limite,
            nota_maxima=nota_maxima,
            nota_minima_aprobacion=nota_minima_aprobacion,
            porcentaje_nota_final=data['porcentaje_nota_final'],
            permite_entrega_tardia=data.get('permite_entrega_tardia', False),
            penalizacion_tardio=data.get('penalizacion_tardio', 0.0),
            publicado=data.get('publicado', False)
        )
        
        return Response({
            'mensaje': f'Evaluación "{evaluacion.titulo}" creada correctamente',
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'tipo': evaluacion.tipo_evaluacion.get_nombre_display(),
                'materia': evaluacion.materia.nombre,
                'fecha_entrega': evaluacion.fecha_entrega,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
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
        
        # Obtener evaluaciones
        evaluaciones = Evaluacion.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion').order_by('-fecha_asignacion')
        
        evaluaciones_data = []
        for evaluacion in evaluaciones:
            evaluaciones_data.append({
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'descripcion': evaluacion.descripcion,
                'tipo_evaluacion': {
                    'id': evaluacion.tipo_evaluacion.id,
                    'nombre': evaluacion.tipo_evaluacion.nombre,
                    'nombre_display': evaluacion.tipo_evaluacion.get_nombre_display()
                },
                'fecha_asignacion': evaluacion.fecha_asignacion,
                'fecha_entrega': evaluacion.fecha_entrega,
                'fecha_limite': evaluacion.fecha_limite,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
                'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
                'permite_entrega_tardia': evaluacion.permite_entrega_tardia,
                'penalizacion_tardio': float(evaluacion.penalizacion_tardio),
                'publicado': evaluacion.publicado,
                'esta_vencido': evaluacion.esta_vencido,
                'puede_entregar_tardio': evaluacion.puede_entregar_tardio,
                'total_calificaciones': evaluacion.calificaciones.count()
            })
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
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
        try:
            evaluacion = Evaluacion.objects.select_related(
                'materia', 'tipo_evaluacion'
            ).get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
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
            'fecha_asignacion': evaluacion.fecha_asignacion,
            'fecha_entrega': evaluacion.fecha_entrega,
            'fecha_limite': evaluacion.fecha_limite,
            'nota_maxima': float(evaluacion.nota_maxima),
            'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
            'porcentaje_nota_final': float(evaluacion.porcentaje_nota_final),
            'permite_entrega_tardia': evaluacion.permite_entrega_tardia,
            'penalizacion_tardio': float(evaluacion.penalizacion_tardio),
            'publicado': evaluacion.publicado,
            'esta_vencido': evaluacion.esta_vencido,
            'puede_entregar_tardio': evaluacion.puede_entregar_tardio,
            'total_calificaciones': evaluacion.calificaciones.count()
        })
    
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
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data
        
        # Actualizar campos básicos
        if 'titulo' in data:
            evaluacion.titulo = data['titulo']
        if 'descripcion' in data:
            evaluacion.descripcion = data['descripcion']
        if 'nota_maxima' in data:
            evaluacion.nota_maxima = data['nota_maxima']
        if 'nota_minima_aprobacion' in data:
            evaluacion.nota_minima_aprobacion = data['nota_minima_aprobacion']
        if 'porcentaje_nota_final' in data:
            evaluacion.porcentaje_nota_final = data['porcentaje_nota_final']
        if 'publicado' in data:
            evaluacion.publicado = data['publicado']
        
        # Validar rango de notas
        if evaluacion.nota_minima_aprobacion > evaluacion.nota_maxima:
            return Response(
                {'error': 'La nota mínima de aprobación no puede ser mayor que la nota máxima'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar fechas si se proporcionan
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
        
        evaluacion.save()
        
        return Response({
            'mensaje': f'Evaluación "{evaluacion.titulo}" actualizada correctamente',
            'evaluacion': {
                'id': evaluacion.id,
                'titulo': evaluacion.titulo,
                'fecha_entrega': evaluacion.fecha_entrega,
                'nota_maxima': float(evaluacion.nota_maxima),
                'nota_minima_aprobacion': float(evaluacion.nota_minima_aprobacion),
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
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {'error': 'Evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si tiene calificaciones
        if evaluacion.calificaciones.exists():
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
        
        return Response({
            'id': tipo.id,
            'nombre': tipo.nombre,
            'nombre_display': tipo.get_nombre_display(),
            'descripcion': tipo.descripcion,
            'activo': tipo.activo,
            'created_at': tipo.created_at,
            'updated_at': tipo.updated_at,
            'evaluaciones_count': Evaluacion.objects.filter(tipo_evaluacion=tipo).count()
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
            evaluaciones_activas = Evaluacion.objects.filter(
                tipo_evaluacion=tipo, 
                activo=True
            ).count()
            
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
        evaluaciones = Evaluacion.objects.filter(tipo_evaluacion=tipo).count()
        
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
