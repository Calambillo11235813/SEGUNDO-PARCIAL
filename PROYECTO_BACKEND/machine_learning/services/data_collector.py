import pandas as pd
from django.db.models import Avg, Count, Q
from Usuarios.models import Usuario, Estudiante  # ✅ IMPORTACIÓN CORRECTA
from Cursos.models import Calificacion, Asistencia, EvaluacionParticipacion, Trimestre, Materia, EvaluacionEntregable
from machine_learning.models import DatasetAcademico, RegistroEstudianteML
from decimal import Decimal
import logging
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)

class DataCollectorService:
    """Servicio para recolección y limpieza de datos académicos"""
    
    def __init__(self):
        self.dataset = None
        
    def crear_dataset(self, nombre, descripcion, año_inicio, año_fin):
        """Crear un nuevo dataset para ML"""
        self.dataset = DatasetAcademico.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            año_inicio=año_inicio,
            año_fin=año_fin
        )
        return self.dataset
    
    def recolectar_datos_estudiantes(self):
        """Recolectar datos históricos de estudiantes"""
        logger.info("Iniciando recolección de datos de estudiantes...")
        
        # ✅ CORREGIR: Usar la nueva relación ForeignKey en lugar de ManyToMany
        from Permisos.models import Rol
        try:
            rol_estudiante = Rol.objects.get(nombre='Estudiante')
            # ✅ CAMBIO: usar usuarios_rol en lugar de usuarios
            estudiantes = Usuario.objects.filter(
                rol=rol_estudiante,  # ✅ CAMBIO: usar 'rol' en lugar de 'roles'
                is_active=True
            )
        except Rol.DoesNotExist:
            # Fallback: usar todos los usuarios activos
            logger.warning("Rol 'Estudiante' no encontrado, usando todos los usuarios activos")
            estudiantes = Usuario.objects.filter(is_active=True)
        
        # Obtener trimestres en el rango del dataset
        trimestres = Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        ).order_by('año_academico', 'numero')
        
        if not trimestres.exists():
            raise ValueError(f"No hay trimestres en el rango {self.dataset.año_inicio}-{self.dataset.año_fin}")
        
        datos_procesados = []
        total_estudiantes = estudiantes.count()
        
        logger.info(f"Procesando {total_estudiantes} estudiantes en {trimestres.count()} trimestres")
        
        for idx, estudiante in enumerate(estudiantes):
            if idx % 10 == 0:  # Log cada 10 estudiantes
                logger.info(f"Procesando estudiante {idx+1}/{total_estudiantes}: {estudiante.get_full_name()}")
                
            datos_estudiante = self._procesar_estudiante(estudiante, trimestres)
            datos_procesados.extend(datos_estudiante)
        
        logger.info(f"Recolección completada: {len(datos_procesados)} registros")
        return datos_procesados
    
    def _procesar_estudiante(self, estudiante, trimestres):
        """Procesar datos de un estudiante individual"""
        registros = []
        trimestres_lista = list(trimestres)
        
        # Necesitamos al menos 2 trimestres para crear un registro (actual + siguiente)
        for i in range(len(trimestres_lista) - 1):
            trimestre_actual = trimestres_lista[i]
            trimestre_siguiente = trimestres_lista[i + 1]
            
            # Calcular features del trimestre actual
            features = self._calcular_features_trimestre(estudiante, trimestre_actual)
            
            # Calcular target del trimestre siguiente
            target = self._calcular_rendimiento_futuro(estudiante, trimestre_siguiente)
            
            # Solo agregar si tenemos datos válidos
            if features and target is not None and features['tiene_datos']:
                registro = {
                    'estudiante': estudiante,
                    'trimestre': trimestre_actual,
                    'promedio_notas_anterior': features['promedio_notas'],
                    'porcentaje_asistencia': features['porcentaje_asistencia'],
                    'promedio_participaciones': features['promedio_participaciones'],
                    'materias_cursadas': features['materias_cursadas'],
                    'evaluaciones_completadas': features['evaluaciones_completadas'],
                    'rendimiento_futuro': target
                }
                registros.append(registro)
        
        return registros
    
    def _calcular_features_trimestre(self, estudiante, trimestre):
        """Calcular features de entrada para un trimestre"""
        try:
            # Promedio de calificaciones (usando el modelo correcto)
            calificaciones = Calificacion.objects.filter(
                estudiante=estudiante,
                evaluacion__isnull=False  # Asegurar que tiene evaluación asociada
            )
            
            # Filtrar por trimestre a través de la evaluación
            calificaciones_trimestre = []
            for cal in calificaciones:
                if hasattr(cal.evaluacion, 'trimestre') and cal.evaluacion.trimestre == trimestre:
                    calificaciones_trimestre.append(cal.nota)
            
            if calificaciones_trimestre:
                promedio_notas = sum(calificaciones_trimestre) / len(calificaciones_trimestre)
            else:
                promedio_notas = Decimal('0.0')
            
            # Porcentaje de asistencia
            asistencias_trimestre = Asistencia.objects.filter(
                estudiante=estudiante,
                trimestre=trimestre
            )
            
            total_asistencias = asistencias_trimestre.count()
            asistencias_presentes = asistencias_trimestre.filter(presente=True).count()
            
            porcentaje_asistencia = Decimal('0.0')
            if total_asistencias > 0:
                porcentaje_asistencia = Decimal((asistencias_presentes / total_asistencias) * 100)
            
            # Promedio de participaciones (evaluaciones de tipo participación)
            participaciones = []
            for cal in calificaciones:
                if (hasattr(cal.evaluacion, 'tipo_evaluacion') and 
                    cal.evaluacion.tipo_evaluacion and
                    cal.evaluacion.tipo_evaluacion.nombre == 'PARTICIPACION' and
                    hasattr(cal.evaluacion, 'trimestre') and 
                    cal.evaluacion.trimestre == trimestre):
                    participaciones.append(cal.nota)
            
            if participaciones:
                promedio_participaciones = sum(participaciones) / len(participaciones)
            else:
                promedio_participaciones = Decimal('0.0')
            
            # Contar materias cursadas (a través de calificaciones)
            materias_ids = set()
            for cal in calificaciones:
                if (hasattr(cal.evaluacion, 'materia') and 
                    hasattr(cal.evaluacion, 'trimestre') and 
                    cal.evaluacion.trimestre == trimestre):
                    materias_ids.add(cal.evaluacion.materia.id)
            
            materias_cursadas = len(materias_ids)
            
            # Contar evaluaciones completadas
            evaluaciones_completadas = len(calificaciones_trimestre)
            
            # Verificar si tiene datos suficientes
            tiene_datos = (
                evaluaciones_completadas > 0 or 
                total_asistencias > 0 or 
                materias_cursadas > 0
            )
            
            return {
                'promedio_notas': Decimal(str(promedio_notas)),
                'porcentaje_asistencia': porcentaje_asistencia,
                'promedio_participaciones': Decimal(str(promedio_participaciones)),
                'materias_cursadas': materias_cursadas,
                'evaluaciones_completadas': evaluaciones_completadas,
                'tiene_datos': tiene_datos
            }
            
        except Exception as e:
            logger.error(f"Error calculando features para {estudiante.get_full_name()}: {str(e)}")
            return None
    
    def _calcular_rendimiento_futuro(self, estudiante, trimestre):
        """Calcular el rendimiento futuro (target variable)"""
        try:
            # Similar lógica que _calcular_features_trimestre pero para el trimestre siguiente
            calificaciones = Calificacion.objects.filter(
                estudiante=estudiante,
                evaluacion__isnull=False
            )
            
            calificaciones_trimestre = []
            for cal in calificaciones:
                if hasattr(cal.evaluacion, 'trimestre') and cal.evaluacion.trimestre == trimestre:
                    calificaciones_trimestre.append(cal.nota)
            
            if calificaciones_trimestre:
                return Decimal(str(sum(calificaciones_trimestre) / len(calificaciones_trimestre)))
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculando target para {estudiante.get_full_name()}: {str(e)}")
            return None
    
    def limpiar_y_normalizar_datos(self, datos_raw):
        """Limpiar y normalizar datos para entrenamiento"""
        logger.info("Iniciando limpieza y normalización de datos...")
        
        if not datos_raw:
            raise ValueError("No hay datos para limpiar")
        
        # Convertir a DataFrame para procesamiento
        df_data = []
        for dato in datos_raw:
            df_data.append({
                'promedio_notas_anterior': float(dato['promedio_notas_anterior']),
                'porcentaje_asistencia': float(dato['porcentaje_asistencia']),
                'promedio_participaciones': float(dato['promedio_participaciones']),
                'materias_cursadas': dato['materias_cursadas'],
                'evaluaciones_completadas': dato['evaluaciones_completadas'],
                'rendimiento_futuro': float(dato['rendimiento_futuro']),
                'estudiante': dato['estudiante'],
                'trimestre': dato['trimestre']
            })
        
        df = pd.DataFrame(df_data)
        
        logger.info(f"Datos originales: {len(df)} registros")
        
        # Eliminar registros con valores nulos
        df_limpio = df.dropna()
        logger.info(f"Después de eliminar nulos: {len(df_limpio)} registros")
        
        # Eliminar outliers (valores fuera de rangos lógicos)
        df_limpio = df_limpio[
            (df_limpio['promedio_notas_anterior'] >= 0) & 
            (df_limpio['promedio_notas_anterior'] <= 100) &
            (df_limpio['porcentaje_asistencia'] >= 0) & 
            (df_limpio['porcentaje_asistencia'] <= 100) &
            (df_limpio['promedio_participaciones'] >= 0) & 
            (df_limpio['promedio_participaciones'] <= 100) &
            (df_limpio['rendimiento_futuro'] >= 0) & 
            (df_limpio['rendimiento_futuro'] <= 100) &
            (df_limpio['materias_cursadas'] > 0) &
            (df_limpio['evaluaciones_completadas'] >= 0)
        ]
        
        logger.info(f"Después de eliminar outliers: {len(df_limpio)} registros")
        
        # Validar que hay suficientes datos después de la limpieza
        if len(df_limpio) < 10:  # Reducimos el mínimo para testing
            raise ValueError(f"Datos insuficientes después de la limpieza: {len(df_limpio)} registros")
        
        logger.info(f"Datos limpiados: {len(df_limpio)} registros válidos de {len(df)} originales")
        
        return df_limpio.to_dict('records')
    
    def guardar_dataset_procesado(self, datos_limpios):
        """Guardar dataset procesado en la base de datos"""
        logger.info("Guardando dataset procesado...")
        
        registros_batch = []
        for dato in datos_limpios:
            registro = RegistroEstudianteML(
                dataset=self.dataset,
                estudiante=dato['estudiante'],
                trimestre=dato['trimestre'],
                promedio_notas_anterior=Decimal(str(dato['promedio_notas_anterior'])),
                porcentaje_asistencia=Decimal(str(dato['porcentaje_asistencia'])),
                promedio_participaciones=Decimal(str(dato['promedio_participaciones'])),
                materias_cursadas=dato['materias_cursadas'],
                evaluaciones_completadas=dato['evaluaciones_completadas'],
                rendimiento_futuro=Decimal(str(dato['rendimiento_futuro']))
            )
            registros_batch.append(registro)
            
            # Guardar en lotes para optimizar
            if len(registros_batch) >= 100:  # Lotes más pequeños para testing
                RegistroEstudianteML.objects.bulk_create(registros_batch, ignore_conflicts=True)
                registros_batch = []
        
        # Guardar registros restantes
        if registros_batch:
            RegistroEstudianteML.objects.bulk_create(registros_batch, ignore_conflicts=True)
        
        # Actualizar contador en dataset
        self.dataset.total_registros = len(datos_limpios)
        self.dataset.save()
        
        logger.info(f"Dataset guardado: {len(datos_limpios)} registros")
        return self.dataset
    
    def _obtener_calificaciones_estudiante_trimestre_corregido(self, estudiante, trimestre):
        """Método corregido para obtener calificaciones usando ContentType"""
        from Cursos.models import EvaluacionParticipacion
        
        calificaciones = []
        
        try:
            # Calificaciones de evaluaciones entregables
            evaluaciones_entregables_ids = list(
                EvaluacionEntregable.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if evaluaciones_entregables_ids:
                ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
                calificaciones_entregables = Calificacion.objects.filter(
                    estudiante=estudiante,
                    content_type=ct_entregable,
                    object_id__in=evaluaciones_entregables_ids
                )
                calificaciones.extend([float(cal.nota) for cal in calificaciones_entregables])
            
            # Calificaciones de evaluaciones de participación
            evaluaciones_participacion_ids = list(
                EvaluacionParticipacion.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if evaluaciones_participacion_ids:
                ct_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
                calificaciones_participacion = Calificacion.objects.filter(
                    estudiante=estudiante,
                    content_type=ct_participacion,
                    object_id__in=evaluaciones_participacion_ids
                )
                calificaciones.extend([float(cal.nota) for cal in calificaciones_participacion])
            
            return calificaciones
            
        except Exception as e:
            logger.error(f"Error obteniendo calificaciones para {estudiante.get_full_name()}: {str(e)}")
            return []

    def _procesar_estudiante_corregido(self, estudiante, trimestres):
        """Versión corregida del procesamiento de estudiante"""
        registros_generados = []
        
        # Necesitamos al menos 2 trimestres para hacer predicciones
        if len(trimestres) < 2:
            return registros_generados
        
        for i in range(len(trimestres) - 1):
            trimestre_actual = trimestres[i]
            trimestre_siguiente = trimestres[i + 1]
            
            try:
                # Calcular features del trimestre actual
                features = self._calcular_features_trimestre_corregido(estudiante, trimestre_actual)
                
                # Calcular target del trimestre siguiente
                target = self._calcular_target_trimestre_corregido(estudiante, trimestre_siguiente)
                
                # Verificar que tenemos datos válidos
                if features and features.get('tiene_datos') and target is not None:
                    registro = {
                        'estudiante': estudiante,
                        'trimestre': trimestre_actual,
                        'promedio_notas_anterior': features['promedio_notas'],
                        'porcentaje_asistencia': features['porcentaje_asistencia'],
                        'promedio_participaciones': features['promedio_participaciones'],
                        'materias_cursadas': features['materias_cursadas'],
                        'evaluaciones_completadas': features['evaluaciones_completadas'],
                        'rendimiento_futuro': target
                    }
                    
                    registros_generados.append(registro)
                    
            except Exception as e:
                logger.warning(f"Error procesando {estudiante.get_full_name()} en {trimestre_actual}: {str(e)}")
                continue
        
        return registros_generados

    def _calcular_features_trimestre_corregido(self, estudiante, trimestre):
        """Calcular features de un trimestre específico - versión corregida"""
        
        # Obtener calificaciones usando método corregido
        calificaciones = self._obtener_calificaciones_estudiante_trimestre_corregido(estudiante, trimestre)
        
        # Calcular promedio de notas
        promedio_notas = Decimal('0.0')
        if calificaciones:
            promedio_notas = Decimal(str(sum(calificaciones) / len(calificaciones)))
        
        # Obtener asistencias
        asistencias = Asistencia.objects.filter(
            estudiante=estudiante,
            trimestre=trimestre
        )
        
        total_asistencias = asistencias.count()
        asistencias_presentes = asistencias.filter(presente=True).count()
        
        porcentaje_asistencia = Decimal('0.0')
        if total_asistencias > 0:
            porcentaje_asistencia = Decimal(str((asistencias_presentes / total_asistencias) * 100))
        
        # Calcular otras métricas
        materias_cursadas = max(1, len(calificaciones) // 3)  # Estimación
        evaluaciones_completadas = len(calificaciones)
        
        # Promedio de participaciones (simplificado como el promedio general)
        promedio_participaciones = promedio_notas
        
        # Verificar si tiene datos suficientes
        tiene_datos = len(calificaciones) > 0 or total_asistencias > 0
        
        return {
            'promedio_notas': promedio_notas,
            'porcentaje_asistencia': porcentaje_asistencia,
            'promedio_participaciones': promedio_participaciones,
            'materias_cursadas': materias_cursadas,
            'evaluaciones_completadas': evaluaciones_completadas,
            'tiene_datos': tiene_datos
        }

    def _calcular_target_trimestre_corregido(self, estudiante, trimestre):
        """Calcular target (rendimiento futuro) - versión corregida"""
        
        # Obtener calificaciones del trimestre objetivo
        calificaciones = self._obtener_calificaciones_estudiante_trimestre_corregido(estudiante, trimestre)
        
        if calificaciones:
            promedio = sum(calificaciones) / len(calificaciones)
            return Decimal(str(promedio))
        
        return None

    # Actualizar el método principal para usar la versión corregida
    def recolectar_datos_estudiantes_corregido(self, limite_estudiantes=None):
        """Versión corregida de recolección de datos con parámetro de límite"""
        logger.info("Iniciando recolección de datos corregida...")
        
        from Permisos.models import Rol
        try:
            rol_estudiante = Rol.objects.get(nombre='Estudiante')
            estudiantes = Usuario.objects.filter(
                rol=rol_estudiante,
                is_active=True
            )
        except Rol.DoesNotExist:
            logger.warning("Rol 'Estudiante' no encontrado, usando todos los usuarios activos")
            estudiantes = Usuario.objects.filter(is_active=True)
    
        # Obtener trimestres en el rango del dataset
        trimestres = Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        ).order_by('año_academico', 'numero')
        
        if not trimestres.exists():
            raise ValueError(f"No hay trimestres en el rango {self.dataset.año_inicio}-{self.dataset.año_fin}")
        
        datos_procesados = []
        total_estudiantes = estudiantes.count()
        
        # ✅ NUEVO: Usar todos los estudiantes o un límite específico
        if limite_estudiantes is None:
            limite = total_estudiantes
        else:
            limite = min(limite_estudiantes, total_estudiantes)
    
        logger.info(f"Procesando {limite} estudiantes de {total_estudiantes} disponibles en {trimestres.count()} trimestres")
        logger.info(f"Registros esperados aproximadamente: {limite * (trimestres.count() - 1)}")
        
        # Procesar estudiantes
        for idx, estudiante in enumerate(estudiantes[:limite]):
            # Log de progreso cada 25 estudiantes
            if idx % 25 == 0:
                logger.info(f"Procesando estudiante {idx+1}/{limite}: {estudiante.get_full_name()}")
                
            datos_estudiante = self._procesar_estudiante_corregido(estudiante, list(trimestres))
            datos_procesados.extend(datos_estudiante)
            
            # Mostrar progreso cada 50 estudiantes
            if idx % 50 == 0 and idx > 0:
                logger.info(f"   📊 Registros generados hasta ahora: {len(datos_procesados)}")
                logger.info(f"   📈 Promedio registros/estudiante: {len(datos_procesados)/(idx+1):.1f}")
            
            # Pausa cada 100 estudiantes para evitar sobrecarga
            if idx % 100 == 0 and idx > 0:
                import time
                time.sleep(0.1)  # Pausa breve
        
        logger.info(f"Recolección corregida completada: {len(datos_procesados)} registros de {limite} estudiantes")
        return datos_procesados

    def recolectar_datos_masivos_optimizado(self, batch_size=50):
        """Método optimizado para recolección masiva de datos en lotes"""
        logger.info("Iniciando recolección masiva optimizada...")
        
        from Permisos.models import Rol
        try:
            rol_estudiante = Rol.objects.get(nombre='Estudiante')
            estudiantes = Usuario.objects.filter(
                rol=rol_estudiante,
                is_active=True
            ).order_by('id')  # Orden consistente
        except Rol.DoesNotExist:
            logger.warning("Rol 'Estudiante' no encontrado, usando todos los usuarios activos")
            estudiantes = Usuario.objects.filter(is_active=True).order_by('id')
        
        # Obtener trimestres
        trimestres = list(Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        ).order_by('año_academico', 'numero'))
        
        if not trimestres:
            raise ValueError(f"No hay trimestres en el rango {self.dataset.año_inicio}-{self.dataset.año_fin}")
        
        total_estudiantes = estudiantes.count()
        total_batches = (total_estudiantes + batch_size - 1) // batch_size
        
        logger.info(f"Procesando {total_estudiantes} estudiantes en {total_batches} lotes de {batch_size}")
        logger.info(f"Trimestres disponibles: {len(trimestres)}")
        
        todos_los_datos = []
        
        # Procesar en lotes
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_estudiantes)
            
            estudiantes_batch = estudiantes[start_idx:end_idx]
            
            logger.info(f"\n📦 Procesando lote {batch_num + 1}/{total_batches}")
            logger.info(f"   Estudiantes: {start_idx + 1} - {end_idx}")
            
            datos_batch = []
            
            for estudiante in estudiantes_batch:
                try:
                    datos_estudiante = self._procesar_estudiante_corregido(estudiante, trimestres)
                    datos_batch.extend(datos_estudiante)
                except Exception as e:
                    logger.warning(f"Error procesando {estudiante.get_full_name()}: {str(e)}")
                    continue
            
            todos_los_datos.extend(datos_batch)
            
            logger.info(f"   ✅ Lote completado: {len(datos_batch)} registros")
            logger.info(f"   📊 Total acumulado: {len(todos_los_datos)} registros")
            
            # Pausa entre lotes para evitar sobrecarga
            if batch_num < total_batches - 1:
                import time
                time.sleep(0.2)
        
        logger.info(f"\n🎉 Recolección masiva completada:")
        logger.info(f"   Total estudiantes procesados: {total_estudiantes}")
        logger.info(f"   Total registros generados: {len(todos_los_datos)}")
        logger.info(f"   Promedio registros/estudiante: {len(todos_los_datos)/total_estudiantes:.1f}")
        
        return todos_los_datos