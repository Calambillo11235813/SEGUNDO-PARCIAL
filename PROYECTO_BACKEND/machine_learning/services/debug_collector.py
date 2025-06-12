import logging
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from Usuarios.models import Usuario
from Cursos.models import Calificacion, Asistencia, Trimestre, EvaluacionEntregable, EvaluacionParticipacion
from Permisos.models import Rol
from decimal import Decimal

logger = logging.getLogger(__name__)

class DebugCollectorServiceCorregido:
    """Servicio para debuggear problemas con GenericForeignKey corregido"""
    
    def __init__(self, dataset):
        self.dataset = dataset
    
    def debug_completo(self):
        """Debug completo del proceso de recolección"""
        print("🔍 INICIANDO DEBUG COMPLETO CORREGIDO")
        print("=" * 50)
        
        # 1. Verificar estudiantes
        self._debug_estudiantes()
        
        # 2. Verificar trimestres
        self._debug_trimestres()
        
        # 3. Verificar estructura de calificaciones
        self._debug_estructura_calificaciones()
        
        # 4. Verificar un estudiante específico
        self._debug_estudiante_especifico_corregido()
        
        # 5. Probar procesamiento manual
        self._probar_procesamiento_manual_corregido()
    
    def _debug_estudiantes(self):
        """Debug de estudiantes disponibles"""
        print("\n1️⃣ DEBUG: ESTUDIANTES")
        print("-" * 30)
        
        estudiantes = Usuario.objects.filter(
            rol__nombre='Estudiante',
            is_active=True
        )
        
        print(f"Total estudiantes: {estudiantes.count()}")
        
        # Mostrar primeros 3 estudiantes
        for i, est in enumerate(estudiantes[:3]):
            print(f"   {i+1}. {est.codigo}: {est.get_full_name()}")
    
    def _debug_trimestres(self):
        """Debug de trimestres en rango"""
        print("\n2️⃣ DEBUG: TRIMESTRES")
        print("-" * 30)
        
        trimestres = Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        ).order_by('año_academico', 'numero')
        
        print(f"Trimestres en rango {self.dataset.año_inicio}-{self.dataset.año_fin}: {trimestres.count()}")
        
        for t in trimestres:
            print(f"   - {t.nombre} {t.año_academico} (ID: {t.id})")
    
    def _debug_estructura_calificaciones(self):
        """Debug de la estructura de calificaciones"""
        print("\n3️⃣ DEBUG: ESTRUCTURA DE CALIFICACIONES")
        print("-" * 30)
        
        # Verificar ContentTypes
        ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
        ct_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
        
        print(f"ContentType EvaluacionEntregable: {ct_entregable.id}")
        print(f"ContentType EvaluacionParticipacion: {ct_participacion.id}")
        
        # Contar calificaciones por tipo
        cal_entregables = Calificacion.objects.filter(content_type=ct_entregable).count()
        cal_participaciones = Calificacion.objects.filter(content_type=ct_participacion).count()
        
        print(f"Calificaciones de entregables: {cal_entregables:,}")
        print(f"Calificaciones de participaciones: {cal_participaciones:,}")
        
        # Mostrar muestra de calificaciones
        print("\n📝 Muestra de calificaciones:")
        for cal in Calificacion.objects.all()[:3]:
            print(f"   ID: {cal.id}, Tipo: {cal.content_type.model}, Object ID: {cal.object_id}")
    
    def _debug_estudiante_especifico_corregido(self):
        """Debug detallado de un estudiante con método corregido"""
        print("\n4️⃣ DEBUG: ESTUDIANTE ESPECÍFICO (CORREGIDO)")
        print("-" * 30)
        
        estudiante = Usuario.objects.filter(rol__nombre='Estudiante').first()
        print(f"Estudiante: {estudiante.get_full_name()}")
        
        # Trimestres en rango
        trimestres = Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        )
        
        for trimestre in trimestres:
            print(f"\n   📅 {trimestre.nombre} {trimestre.año_academico} (ID: {trimestre.id})")
            
            # Calificaciones de entregables en este trimestre
            entregables_count = self._contar_calificaciones_entregables(estudiante, trimestre)
            print(f"      📝 Calificaciones entregables: {entregables_count}")
            
            # Calificaciones de participaciones en este trimestre
            participaciones_count = self._contar_calificaciones_participaciones(estudiante, trimestre)
            print(f"      🗣️ Calificaciones participaciones: {participaciones_count}")
            
            # Asistencias en este trimestre
            asistencias_count = Asistencia.objects.filter(
                estudiante=estudiante,
                trimestre=trimestre
            ).count()
            print(f"      📅 Asistencias: {asistencias_count}")
            
            total_calificaciones = entregables_count + participaciones_count
            print(f"      🎯 Total calificaciones: {total_calificaciones}")
    
    def _contar_calificaciones_entregables(self, estudiante, trimestre):
        """Contar calificaciones de entregables para un estudiante en un trimestre"""
        try:
            # Obtener IDs de evaluaciones entregables del trimestre
            evaluaciones_ids = list(
                EvaluacionEntregable.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if not evaluaciones_ids:
                return 0
            
            # Contar calificaciones de esas evaluaciones
            ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
            count = Calificacion.objects.filter(
                estudiante=estudiante,
                content_type=ct_entregable,
                object_id__in=evaluaciones_ids
            ).count()
            
            return count
            
        except Exception as e:
            print(f"         ❌ Error contando entregables: {str(e)}")
            return 0
    
    def _contar_calificaciones_participaciones(self, estudiante, trimestre):
        """Contar calificaciones de participaciones para un estudiante en un trimestre"""
        try:
            # Obtener IDs de evaluaciones de participación del trimestre
            evaluaciones_ids = list(
                EvaluacionParticipacion.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if not evaluaciones_ids:
                return 0
            
            # Contar calificaciones de esas evaluaciones
            ct_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
            count = Calificacion.objects.filter(
                estudiante=estudiante,
                content_type=ct_participacion,
                object_id__in=evaluaciones_ids
            ).count()
            
            return count
            
        except Exception as e:
            print(f"         ❌ Error contando participaciones: {str(e)}")
            return 0
    
    def _probar_procesamiento_manual_corregido(self):
        """Probar procesamiento manual corregido"""
        print("\n5️⃣ DEBUG: PROCESAMIENTO MANUAL CORREGIDO")
        print("-" * 30)
        
        estudiante = Usuario.objects.filter(rol__nombre='Estudiante').first()
        trimestres = list(Trimestre.objects.filter(
            año_academico__gte=self.dataset.año_inicio,
            año_academico__lte=self.dataset.año_fin
        ).order_by('año_academico', 'numero'))
        
        print(f"Procesando: {estudiante.get_full_name()}")
        print(f"Trimestres disponibles: {len(trimestres)}")
        
        if len(trimestres) < 2:
            print("❌ No hay suficientes trimestres para crear registros")
            return
        
        # Intentar procesar primer trimestre
        trimestre_actual = trimestres[0]
        trimestre_siguiente = trimestres[1]
        
        print(f"\nProcesando: {trimestre_actual} -> {trimestre_siguiente}")
        
        # Calcular features corregido
        features = self._calcular_features_corregido(estudiante, trimestre_actual)
        target = self._calcular_target_corregido(estudiante, trimestre_siguiente)
        
        print(f"Features: {features}")
        print(f"Target: {target}")
        
        if features and target is not None and features.get('tiene_datos'):
            print("✅ Registro válido generado")
        else:
            print("❌ No se puede generar registro válido")
    
    def _calcular_features_corregido(self, estudiante, trimestre):
        """Versión corregida de cálculo de features"""
        try:
            print(f"   🔍 Calculando features para {trimestre}")
            
            # Obtener calificaciones de entregables
            calificaciones_entregables = self._obtener_calificaciones_entregables(estudiante, trimestre)
            
            # Obtener calificaciones de participaciones
            calificaciones_participaciones = self._obtener_calificaciones_participaciones(estudiante, trimestre)
            
            # Combinar todas las calificaciones
            todas_calificaciones = calificaciones_entregables + calificaciones_participaciones
            
            print(f"   📝 Calificaciones entregables: {len(calificaciones_entregables)}")
            print(f"   🗣️ Calificaciones participaciones: {len(calificaciones_participaciones)}")
            print(f"   📊 Total calificaciones: {len(todas_calificaciones)}")
            
            # Calcular promedio
            if todas_calificaciones:
                promedio = sum(todas_calificaciones) / len(todas_calificaciones)
            else:
                promedio = 0.0
            
            # Obtener asistencias
            asistencias = Asistencia.objects.filter(
                estudiante=estudiante,
                trimestre=trimestre
            )
            
            total_asistencias = asistencias.count()
            presentes = asistencias.filter(presente=True).count()
            
            print(f"   📅 Asistencias: {presentes}/{total_asistencias}")
            
            porcentaje_asistencia = 0.0
            if total_asistencias > 0:
                porcentaje_asistencia = (presentes / total_asistencias) * 100
            
            # Verificar si tiene datos
            tiene_datos = len(todas_calificaciones) > 0 or total_asistencias > 0
            
            features = {
                'promedio_notas': Decimal(str(promedio)),
                'porcentaje_asistencia': Decimal(str(porcentaje_asistencia)),
                'promedio_participaciones': Decimal(str(sum(calificaciones_participaciones) / len(calificaciones_participaciones) if calificaciones_participaciones else promedio)),
                'materias_cursadas': max(1, len(todas_calificaciones) // 3),
                'evaluaciones_completadas': len(todas_calificaciones),
                'tiene_datos': tiene_datos
            }
            
            print(f"   ✅ Features calculadas: {tiene_datos}")
            return features
            
        except Exception as e:
            print(f"   ❌ Error calculando features: {str(e)}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _obtener_calificaciones_entregables(self, estudiante, trimestre):
        """Obtener calificaciones de evaluaciones entregables"""
        try:
            # Obtener IDs de evaluaciones entregables del trimestre
            evaluaciones_ids = list(
                EvaluacionEntregable.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if not evaluaciones_ids:
                return []
            
            # Obtener calificaciones
            ct_entregable = ContentType.objects.get_for_model(EvaluacionEntregable)
            calificaciones = Calificacion.objects.filter(
                estudiante=estudiante,
                content_type=ct_entregable,
                object_id__in=evaluaciones_ids
            )
            
            return [float(cal.nota) for cal in calificaciones]
            
        except Exception as e:
            print(f"      ❌ Error obteniendo entregables: {str(e)}")
            return []
    
    def _obtener_calificaciones_participaciones(self, estudiante, trimestre):
        """Obtener calificaciones de evaluaciones de participación"""
        try:
            # Obtener IDs de evaluaciones de participación del trimestre
            evaluaciones_ids = list(
                EvaluacionParticipacion.objects.filter(trimestre=trimestre)
                .values_list('id', flat=True)
            )
            
            if not evaluaciones_ids:
                return []
            
            # Obtener calificaciones
            ct_participacion = ContentType.objects.get_for_model(EvaluacionParticipacion)
            calificaciones = Calificacion.objects.filter(
                estudiante=estudiante,
                content_type=ct_participacion,
                object_id__in=evaluaciones_ids
            )
            
            return [float(cal.nota) for cal in calificaciones]
            
        except Exception as e:
            print(f"      ❌ Error obteniendo participaciones: {str(e)}")
            return []
    
    def _calcular_target_corregido(self, estudiante, trimestre):
        """Versión corregida de cálculo de target"""
        try:
            print(f"   🎯 Calculando target para {trimestre}")
            
            # Obtener todas las calificaciones del trimestre
            calificaciones_entregables = self._obtener_calificaciones_entregables(estudiante, trimestre)
            calificaciones_participaciones = self._obtener_calificaciones_participaciones(estudiante, trimestre)
            
            todas_calificaciones = calificaciones_entregables + calificaciones_participaciones
            
            print(f"   📝 Calificaciones target: {len(todas_calificaciones)}")
            
            if todas_calificaciones:
                target = sum(todas_calificaciones) / len(todas_calificaciones)
                print(f"   ✅ Target calculado: {target:.2f}")
                return Decimal(str(target))
            
            print(f"   ❌ No hay calificaciones para target")
            return None
            
        except Exception as e:
            print(f"   ❌ Error calculando target: {str(e)}")
            return None