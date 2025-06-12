from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from machine_learning.services.data_collector import DataCollectorService
from machine_learning.services.model_trainer import ModelTrainerServiceSimplificado
from machine_learning.services.prediction_service import PredictionService
from machine_learning.models import DatasetAcademico, ModeloML, PrediccionAcademica
from machine_learning.serializers import (
    DatasetAcademicoSerializer, ModeloMLSerializer, 
    PrediccionAcademicaSerializer, PrediccionRequestSerializer,
    PrediccionResponseSerializer
)
from django.utils import timezone
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
        trainer = ModelTrainerServiceSimplificado()
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
        # Validar datos de entrada requeridos
        campos_requeridos = [
            'promedio_notas_anterior',
            'porcentaje_asistencia',
            'promedio_participaciones',
            'materias_cursadas',
            'evaluaciones_completadas'
        ]
        
        datos_entrada = request.data
        
        # Validar que todos los campos estén presentes
        for campo in campos_requeridos:
            if campo not in datos_entrada:
                return Response({
                    'error': f'Campo requerido faltante: {campo}',
                    'campos_requeridos': campos_requeridos
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar tipos de datos
        try:
            datos_validados = {
                'promedio_notas_anterior': float(datos_entrada['promedio_notas_anterior']),
                'porcentaje_asistencia': float(datos_entrada['porcentaje_asistencia']),
                'promedio_participaciones': float(datos_entrada['promedio_participaciones']),
                'materias_cursadas': int(datos_entrada['materias_cursadas']),
                'evaluaciones_completadas': int(datos_entrada['evaluaciones_completadas'])
            }
        except (ValueError, TypeError) as e:
            return Response({
                'error': 'Error en tipos de datos',
                'detalle': f'Verificar que los números sean válidos: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar rangos
        if not (0 <= datos_validados['promedio_notas_anterior'] <= 100):
            return Response({
                'error': 'promedio_notas_anterior debe estar entre 0 y 100'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not (0 <= datos_validados['porcentaje_asistencia'] <= 100):
            return Response({
                'error': 'porcentaje_asistencia debe estar entre 0 y 100'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not (0 <= datos_validados['promedio_participaciones'] <= 100):
            return Response({
                'error': 'promedio_participaciones debe estar entre 0 y 100'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Inicializar servicio de predicción
        prediction_service = PredictionService()
        
        # Realizar predicción usando nuestro método optimizado
        resultado = prediction_service.predecir_rendimiento_estudiante(datos_validados)
        
        # Verificar si hubo error
        if 'error' in resultado:
            return Response({
                'error': resultado['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Guardar predicción en BD (opcional)
        estudiante_codigo = datos_entrada.get('estudiante_codigo')
        if estudiante_codigo:
            try:
                from Usuarios.models import Usuario
                estudiante = Usuario.objects.get(codigo=estudiante_codigo)
                
                # Crear registro de predicción
                PrediccionAcademica.objects.create(
                    estudiante=estudiante,
                    promedio_notas_anterior=datos_validados['promedio_notas_anterior'],
                    porcentaje_asistencia=datos_validados['porcentaje_asistencia'],
                    promedio_participaciones=datos_validados['promedio_participaciones'],
                    materias_cursadas=datos_validados['materias_cursadas'],
                    evaluaciones_completadas=datos_validados['evaluaciones_completadas'],
                    prediccion_numerica=resultado['prediccion_rendimiento'],
                    categoria_predicha=resultado['categoria'],
                    nivel_confianza=resultado['confianza'],
                    nivel_rendimiento=resultado['categoria'].upper(),
                    datos_entrada=datos_validados,
                    recomendaciones=resultado['recomendaciones']
                )
                logger.info(f"Predicción guardada para estudiante {estudiante_codigo}")
            except Usuario.DoesNotExist:
                logger.warning(f"Estudiante {estudiante_codigo} no encontrado")
            except Exception as e:
                logger.error(f"Error guardando predicción: {str(e)}")
        
        # Formatear respuesta
        respuesta_final = {
            'mensaje': 'Predicción realizada exitosamente',
            'datos_entrada': datos_validados,
            'prediccion': {
                'rendimiento_predicho': resultado['prediccion_rendimiento'],
                'categoria': resultado['categoria'],
                'nivel_confianza': resultado['confianza'],
                'recomendaciones': resultado['recomendaciones'],
                'modelo_info': resultado['modelo_info']
            },
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(respuesta_final, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error realizando predicción: {str(e)}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
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

@api_view(['POST'])
@permission_classes([AllowAny])
def predecir_rendimiento_multiple(request):
    """Realizar predicciones para múltiples estudiantes"""
    try:
        estudiantes_data = request.data.get('estudiantes', [])
        
        if not estudiantes_data or not isinstance(estudiantes_data, list):
            return Response({
                'error': 'Se requiere una lista de estudiantes en el campo "estudiantes"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(estudiantes_data) > 50:  # Límite para evitar sobrecarga
            return Response({
                'error': 'Máximo 50 estudiantes por solicitud'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Inicializar servicio
        prediction_service = PredictionService()
        
        # Procesar predicciones
        resultados = []
        errores = []
        
        for i, datos_estudiante in enumerate(estudiantes_data):
            try:
                # Validar datos del estudiante
                campos_requeridos = [
                    'promedio_notas_anterior', 'porcentaje_asistencia',
                    'promedio_participaciones', 'materias_cursadas',
                    'evaluaciones_completadas'
                ]
                
                for campo in campos_requeridos:
                    if campo not in datos_estudiante:
                        raise ValueError(f'Campo {campo} faltante')
                
                # Realizar predicción
                resultado = prediction_service.predecir_rendimiento_estudiante(datos_estudiante)
                
                if 'error' in resultado:
                    errores.append({
                        'estudiante_index': i,
                        'error': resultado['error']
                    })
                else:
                    resultados.append({
                        'estudiante_index': i,
                        'estudiante_id': datos_estudiante.get('id', f'estudiante_{i}'),
                        'prediccion': resultado
                    })
                    
            except Exception as e:
                errores.append({
                    'estudiante_index': i,
                    'error': str(e)
                })
        
        respuesta = {
            'mensaje': f'Procesadas {len(resultados)} predicciones exitosas',
            'total_estudiantes': len(estudiantes_data),
            'predicciones_exitosas': len(resultados),
            'predicciones_con_error': len(errores),
            'resultados': resultados
        }
        
        if errores:
            respuesta['errores'] = errores
        
        return Response(respuesta, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en predicciones múltiples: {str(e)}")
        return Response({
            'error': f'Error procesando predicciones múltiples: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def estado_sistema_ml(request):
    """Obtener estado del sistema de Machine Learning"""
    try:
        # Verificar datasets disponibles
        total_datasets = DatasetAcademico.objects.filter(activo=True).count()
        dataset_masivo = DatasetAcademico.objects.filter(
            total_registros__gte=1000,
            activo=True
        ).order_by('-fecha_creacion').first()
        
        # Verificar modelos entrenados
        total_modelos = ModeloML.objects.filter(activo=True).count()
        mejor_modelo = ModeloML.objects.filter(activo=True).order_by('-r2_score').first()
        
        # Verificar servicio de predicción
        prediction_service = PredictionService()
        servicio_disponible = prediction_service.cargar_mejor_modelo()
        
        # Estadísticas de uso
        total_predicciones = PrediccionAcademica.objects.count()
        predicciones_hoy = PrediccionAcademica.objects.filter(
            fecha_prediccion__date=timezone.now().date()
        ).count()
        
        estado = {
            'sistema_activo': True,
            'timestamp': timezone.now().isoformat(),
            'datasets': {
                'total_activos': total_datasets,
                'dataset_principal': {
                    'nombre': dataset_masivo.nombre if dataset_masivo else None,
                    'registros': dataset_masivo.total_registros if dataset_masivo else 0,
                    'fecha_creacion': dataset_masivo.fecha_creacion.isoformat() if dataset_masivo else None
                } if dataset_masivo else None
            },
            'modelos': {
                'total_activos': total_modelos,
                'mejor_modelo': {
                    'algoritmo': mejor_modelo.algoritmo if mejor_modelo else None,
                    'r2_score': float(mejor_modelo.r2_score) if mejor_modelo else None,
                    'precision': mejor_modelo.precision_porcentaje if mejor_modelo else None,
                    'fecha_entrenamiento': mejor_modelo.fecha_entrenamiento.isoformat() if mejor_modelo else None
                } if mejor_modelo else None
            },
            'servicio_prediccion': {
                'disponible': servicio_disponible,
                'estado': 'activo' if servicio_disponible else 'inactivo'
            },
            'estadisticas_uso': {
                'total_predicciones': total_predicciones,
                'predicciones_hoy': predicciones_hoy
            }
        }
        
        return Response(estado, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {str(e)}")
        return Response({
            'sistema_activo': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)