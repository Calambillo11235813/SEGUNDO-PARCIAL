from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Materia, TipoEvaluacion, ConfiguracionEvaluacionMateria

@api_view(['GET'])
@permission_classes([AllowAny])
def get_configuracion_evaluacion_materia(request, materia_id):
    """
    Obtiene la configuración de tipos de evaluación para una materia específica.
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
        
        # Obtener configuraciones activas
        configuraciones = ConfiguracionEvaluacionMateria.objects.filter(
            materia=materia,
            activo=True
        ).select_related('tipo_evaluacion')
        
        # Calcular porcentaje disponible
        porcentaje_asignado = sum(config.porcentaje for config in configuraciones)
        porcentaje_disponible = max(0, 100 - porcentaje_asignado)
        
        # Preparar datos de respuesta
        configuraciones_data = []
        for config in configuraciones:
            configuraciones_data.append({
                'id': config.id,
                'tipo_evaluacion': {
                    'id': config.tipo_evaluacion.id,
                    'nombre': config.tipo_evaluacion.nombre,
                    'nombre_display': config.tipo_evaluacion.get_nombre_display()
                },
                'porcentaje': float(config.porcentaje)
            })
        
        return Response({
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'curso': str(materia.curso)
            },
            'configuraciones': configuraciones_data,
            'porcentaje_asignado': float(porcentaje_asignado),
            'porcentaje_disponible': float(porcentaje_disponible)
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_configuracion_evaluacion(request):
    """
    Crea o actualiza una configuración de tipo de evaluación para una materia.
    
    Request body:
    {
        "materia_id": 1,
        "tipo_evaluacion_id": 1,
        "porcentaje": 60.0
    }
    """
    try:
        from decimal import Decimal
        data = request.data
        
        # Validaciones básicas
        campos_requeridos = ['materia_id', 'tipo_evaluacion_id', 'porcentaje']
        for campo in campos_requeridos:
            if not data.get(campo) and data.get(campo) != 0:
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar porcentaje
        porcentaje = Decimal(str(data['porcentaje']))
        if porcentaje < Decimal('0') or porcentaje > Decimal('100'):
            return Response(
                {'error': 'El porcentaje debe estar entre 0 y 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar materia y tipo de evaluación
        try:
            materia = Materia.objects.get(id=data['materia_id'])
            tipo_evaluacion = TipoEvaluacion.objects.get(id=data['tipo_evaluacion_id'])
        except (Materia.DoesNotExist, TipoEvaluacion.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Calcular porcentaje actual asignado
        configuraciones = ConfiguracionEvaluacionMateria.objects.filter(
            materia=materia,
            activo=True
        ).exclude(tipo_evaluacion=tipo_evaluacion)
        
        porcentaje_actual = sum(config.porcentaje for config in configuraciones)
        
        # Validar que no exceda 100%
        if porcentaje_actual + porcentaje > Decimal('100'):
            return Response({
                'error': f'La suma de porcentajes excedería el 100%. Porcentaje disponible: {Decimal("100") - porcentaje_actual}%',
                'porcentaje_disponible': float(Decimal('100') - porcentaje_actual)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Crear o actualizar configuración
        with transaction.atomic():
            config, created = ConfiguracionEvaluacionMateria.objects.update_or_create(
                materia=materia,
                tipo_evaluacion=tipo_evaluacion,
                defaults={
                    'porcentaje': porcentaje,
                    'activo': True,
                    'created_by': request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                }
            )
        
        # Preparar respuesta
        return Response({
            'mensaje': f"Configuración {'creada' if created else 'actualizada'} correctamente",
            'configuracion': {
                'id': config.id,
                'materia': materia.nombre,
                'tipo_evaluacion': tipo_evaluacion.get_nombre_display(),
                'porcentaje': float(porcentaje),
                'porcentaje_restante': float(Decimal('100') - (porcentaje_actual + porcentaje))
            }
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    except ValidationError as ve:
        return Response(
            {'error': str(ve)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_configuracion_evaluacion(request, config_id):
    """
    Elimina una configuración de tipo de evaluación para una materia.
    """
    try:
        try:
            config = ConfiguracionEvaluacionMateria.objects.get(id=config_id)
        except ConfiguracionEvaluacionMateria.DoesNotExist:
            return Response(
                {'error': 'Configuración de evaluación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Verificar si existen evaluaciones que usen esta configuración
        evaluaciones_count = config.materia.evaluaciones.filter(
            tipo_evaluacion=config.tipo_evaluacion,
            activo=True
        ).count()
        
        if evaluaciones_count > 0:
            return Response({
                'error': f'No se puede eliminar la configuración porque existen {evaluaciones_count} evaluaciones que dependen de ella',
                'evaluaciones_relacionadas': evaluaciones_count
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Eliminar configuración
        materia_nombre = config.materia.nombre
        tipo_nombre = config.tipo_evaluacion.get_nombre_display()
        config.delete()
        
        return Response({
            'mensaje': f'Configuración de {tipo_nombre} para {materia_nombre} eliminada correctamente'
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )