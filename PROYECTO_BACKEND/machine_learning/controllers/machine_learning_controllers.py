from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from machine_learning.services.data_collector import DataCollectorService
from machine_learning.services.model_trainer import ModelTrainerService
from machine_learning.services.prediction_service import PredictionService
from machine_learning.models import DatasetAcademico, ModeloML, PrediccionAcademica
from machine_learning.serializers import (
    DatasetAcademicoSerializer, ModeloMLSerializer, 
    PrediccionAcademicaSerializer, PrediccionRequestSerializer,
    PrediccionResponseSerializer
)
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_dataset(request):
    """Crear y procesar un nuevo dataset para ML"""
    try:
        # Validar parámetros
        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion', '')
        año_inicio = request.data.get('año_inicio', 2022)
        año_fin = request.data.get('año_fin', 2024)
        
        if not nombre:
            return Response({
                'error': 'El nombre del dataset es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear dataset
        collector = DataCollectorService()
        dataset = collector.crear_dataset(nombre, descripcion, año_inicio, año_fin)
        
        # Recolectar y procesar datos
        datos_raw = collector.recolectar_datos_estudiantes()
        datos_limpios = collector.limpiar_y_normalizar_datos(datos_raw)
        dataset_final = collector.guardar_dataset_procesado(datos_limpios)
        
        serializer = DatasetAcademicoSerializer(dataset_final)
        
        return Response({
            'mensaje': 'Dataset creado exitosamente',
            'dataset': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creando dataset: {str(e)}")
        return Response({
            'error': f'Error creando dataset: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def entrenar_modelos(request, dataset_id):
    """Entrenar todos los modelos ML para un dataset"""
    try:
        # Validar que existe el dataset
        try:
            dataset = DatasetAcademico.objects.get(id=dataset_id)
        except DatasetAcademico.DoesNotExist:
            return Response({
                'error': f'Dataset con ID {dataset_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Entrenar modelos
        trainer = ModelTrainerService()
        resultados = trainer.entrenar_todos_modelos(dataset_id)
        
        # Preparar respuesta
        respuesta = {
            'mensaje': 'Entrenamiento completado',
            'dataset': dataset.nombre,
            'resultados': {}
        }
        
        for algoritmo, resultado in resultados.items():
            if 'error' in resultado:
                respuesta['resultados'][algoritmo] = {
                    'estado': 'error',
                    'mensaje': resultado['error']
                }
            else:
                respuesta['resultados'][algoritmo] = {
                    'estado': 'exitoso',
                    'modelo_id': str(resultado['modelo_db'].id),
                    'metricas': resultado['metricas'],
                    'precision': f"{resultado['metricas']['r2'] * 100:.2f}%"
                }
        
        return Response(respuesta, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error entrenando modelos: {str(e)}")
        return Response({
            'error': f'Error entrenando modelos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def predecir_rendimiento(request):
    """Realizar predicción de rendimiento académico"""
    try:
        # Validar datos de entrada
        serializer = PrediccionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Datos de entrada inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        datos_validados = serializer.validated_data
        
        # Inicializar servicio de predicción
        prediction_service = PredictionService()
        prediction_service.cargar_modelo()
        
        # Realizar predicción
        resultado = prediction_service.predecir_rendimiento(datos_validados)
        
        # Serializar respuesta
        response_serializer = PrediccionResponseSerializer(resultado)
        
        return Response({
            'mensaje': 'Predicción realizada exitosamente',
            'prediccion': response_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error realizando predicción: {str(e)}")
        return Response({
            'error': f'Error realizando predicción: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_modelos(request):
    """Obtener lista de modelos entrenados"""
    try:
        modelos = ModeloML.objects.filter(activo=True).order_by('-fecha_entrenamiento')
        serializer = ModeloMLSerializer(modelos, many=True)
        
        return Response({
            'modelos': serializer.data,
            'total': modelos.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo modelos: {str(e)}")
        return Response({
            'error': f'Error obteniendo modelos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_datasets(request):
    """Obtener lista de datasets disponibles"""
    try:
        datasets = DatasetAcademico.objects.filter(activo=True).order_by('-fecha_creacion')
        serializer = DatasetAcademicoSerializer(datasets, many=True)
        
        return Response({
            'datasets': serializer.data,
            'total': datasets.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo datasets: {str(e)}")
        return Response({
            'error': f'Error obteniendo datasets: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def historial_predicciones(request, estudiante_codigo):
    """Obtener historial de predicciones de un estudiante"""
    try:
        from Usuarios.models import Usuario
        
        # Validar que existe el estudiante
        try:
            estudiante = Usuario.objects.get(codigo=estudiante_codigo)
        except Usuario.DoesNotExist:
            return Response({
                'error': f'Estudiante con código {estudiante_codigo} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener predicciones
        predicciones = PrediccionAcademica.objects.filter(
            estudiante=estudiante
        ).order_by('-fecha_prediccion')[:20]  # Últimas 20 predicciones
        
        serializer = PrediccionAcademicaSerializer(predicciones, many=True)
        
        return Response({
            'estudiante': {
                'codigo': estudiante.codigo,
                'nombre': estudiante.get_full_name()
            },
            'predicciones': serializer.data,
            'total': predicciones.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return Response({
            'error': f'Error obteniendo historial: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def estadisticas_modelo(request, modelo_id):
    """Obtener estadísticas detalladas de un modelo"""
    try:
        # Validar que existe el modelo
        try:
            modelo = ModeloML.objects.get(id=modelo_id)
        except ModeloML.DoesNotExist:
            return Response({
                'error': f'Modelo con ID {modelo_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener métricas detalladas
        metricas_detalladas = None
        if hasattr(modelo, 'metricas_detalladas'):
            metricas_detalladas = modelo.metricas_detalladas
        
        # Estadísticas de predicciones
        total_predicciones = modelo.predicciones.count()
        predicciones_por_nivel = {
            'BAJO': modelo.predicciones.filter(nivel_rendimiento='BAJO').count(),
            'MEDIO': modelo.predicciones.filter(nivel_rendimiento='MEDIO').count(),
            'ALTO': modelo.predicciones.filter(nivel_rendimiento='ALTO').count()
        }
        
        estadisticas = {
            'modelo': {
                'id': str(modelo.id),
                'nombre': modelo.nombre,
                'algoritmo': modelo.algoritmo,
                'fecha_entrenamiento': modelo.fecha_entrenamiento.isoformat(),
                'activo': modelo.activo
            },
            'metricas_basicas': {
                'mae': float(modelo.mae_score) if modelo.mae_score else None,
                'mse': float(modelo.mse_score) if modelo.mse_score else None,
                'r2': float(modelo.r2_score) if modelo.r2_score else None,
                'precision_porcentaje': modelo.precision_porcentaje
            },
            'estadisticas_uso': {
                'total_predicciones': total_predicciones,
                'predicciones_por_nivel': predicciones_por_nivel
            }
        }
        
        if metricas_detalladas:
            estadisticas['metricas_avanzadas'] = {
                'validacion_cruzada': {
                    'mae_cv_mean': float(metricas_detalladas.mae_cv_mean) if metricas_detalladas.mae_cv_mean else None,
                    'mae_cv_std': float(metricas_detalladas.mae_cv_std) if metricas_detalladas.mae_cv_std else None,
                    'r2_cv_mean': float(metricas_detalladas.r2_cv_mean) if metricas_detalladas.r2_cv_mean else None,
                    'r2_cv_std': float(metricas_detalladas.r2_cv_std) if metricas_detalladas.r2_cv_std else None
                },
                'precision_real': float(metricas_detalladas.precision_real) if metricas_detalladas.precision_real else None
            }
        
        return Response(estadisticas, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return Response({
            'error': f'Error obteniendo estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)