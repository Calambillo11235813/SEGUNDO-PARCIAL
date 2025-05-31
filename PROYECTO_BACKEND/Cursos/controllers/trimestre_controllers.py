from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Avg, Count
from datetime import datetime, date
from decimal import Decimal

from ..models import Trimestre, PromedioTrimestral, PromedioAnual, Materia, Evaluacion, Calificacion, Asistencia
from Usuarios.models import Usuario

@api_view(['GET'])
@permission_classes([AllowAny])
def get_trimestres(request):
    """Obtiene todos los trimestres"""
    año = request.GET.get('año')
    activos_solo = request.GET.get('activos', 'false').lower() == 'true'
    
    trimestres = Trimestre.objects.all()
    
    if año:
        trimestres = trimestres.filter(año_academico=año)
    
    if activos_solo:
        trimestres = trimestres.filter(activo=True)
    
    data = []
    for trimestre in trimestres:
        data.append({
            'id': trimestre.id,
            'numero': trimestre.numero,
            'nombre': trimestre.nombre,
            'año_academico': trimestre.año_academico,
            'fecha_inicio': trimestre.fecha_inicio,
            'fecha_fin': trimestre.fecha_fin,
            'fecha_limite_evaluaciones': trimestre.fecha_limite_evaluaciones,
            'fecha_limite_calificaciones': trimestre.fecha_limite_calificaciones,
            'estado': trimestre.estado,
            'esta_activo': trimestre.esta_activo,
            'puede_registrar_evaluaciones': trimestre.puede_registrar_evaluaciones,
            'puede_registrar_calificaciones': trimestre.puede_registrar_calificaciones,
            'nota_minima_aprobacion': float(trimestre.nota_minima_aprobacion),
            'porcentaje_asistencia_minima': float(trimestre.porcentaje_asistencia_minima)
        })
    
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_trimestre(request):
    """
    Crea un nuevo trimestre para cualquier año académico (actual o anteriores)
    
    Se puede utilizar para crear trimestres en años pasados (2023, 2024) o futuros.
    """
    try:
        data = request.data
        
        # Validaciones básicas
        campos_requeridos = ['numero', 'nombre', 'año_academico', 'fecha_inicio', 'fecha_fin']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return Response(
                    {'error': f'El campo {campo} es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar número de trimestre
        if data['numero'] not in [1, 2, 3]:
            return Response(
                {'error': 'El número de trimestre debe ser 1, 2 o 3'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar año académico - Permitir años anteriores, pero con advertencia
        año_actual = date.today().year
        if int(data['año_academico']) < año_actual - 5:  # Limitar a 5 años atrás como medida de seguridad
            return Response(
                {'error': f'El año académico no puede ser anterior a {año_actual - 5}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validar que no exista el trimestre para ese año
        if Trimestre.objects.filter(numero=data['numero'], año_academico=data['año_academico']).exists():
            return Response(
                {'error': f'Ya existe el trimestre {data["numero"]} para el año {data["año_academico"]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar fechas
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
            fecha_limite_eval = datetime.strptime(data.get('fecha_limite_evaluaciones', data['fecha_fin']), '%Y-%m-%d').date()
            fecha_limite_cal = datetime.strptime(data.get('fecha_limite_calificaciones', data['fecha_fin']), '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if fecha_fin <= fecha_inicio:
            return Response(
                {'error': 'La fecha de fin debe ser posterior a la fecha de inicio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar coherencia de año en fechas
        año_trimestre = int(data['año_academico'])
        if fecha_inicio.year != año_trimestre and fecha_fin.year != año_trimestre:
            return Response(
                {'advertencia': f'Las fechas proporcionadas no coinciden con el año académico {año_trimestre}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear trimestre
        trimestre = Trimestre.objects.create(
            numero=data['numero'],
            nombre=data['nombre'],
            año_academico=data['año_academico'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            fecha_limite_evaluaciones=fecha_limite_eval,
            fecha_limite_calificaciones=fecha_limite_cal,
            nota_minima_aprobacion=data.get('nota_minima_aprobacion', 51.0),
            porcentaje_asistencia_minima=data.get('porcentaje_asistencia_minima', 80.0),
            estado=data.get('estado', 'PLANIFICADO'),
            created_by_id=data.get('created_by')
        )
        
        # Determinar si es un año anterior
        mensaje = 'Trimestre creado exitosamente'
        if int(data['año_academico']) < año_actual:
            mensaje += f' (Nota: Se ha creado un trimestre para el año {data["año_academico"]}, que es anterior al año actual)'
        
        return Response({
            'mensaje': mensaje,
            'trimestre': {
                'id': trimestre.id,
                'numero': trimestre.numero,
                'nombre': trimestre.nombre,
                'año_academico': trimestre.año_academico,
                'estado': trimestre.estado,
                'fecha_inicio': trimestre.fecha_inicio,
                'fecha_fin': trimestre.fecha_fin
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_trimestre(request, trimestre_id):
    """Actualiza un trimestre"""
    try:
        trimestre = Trimestre.objects.get(id=trimestre_id)
        data = request.data
        
        # Campos actualizables
        campos_actualizables = ['nombre', 'fecha_inicio', 'fecha_fin', 'fecha_limite_evaluaciones', 
                               'fecha_limite_calificaciones', 'estado', 'nota_minima_aprobacion', 
                               'porcentaje_asistencia_minima']
        
        for campo in campos_actualizables:
            if campo in data:
                if 'fecha' in campo and data[campo]:
                    try:
                        setattr(trimestre, campo, datetime.strptime(data[campo], '%Y-%m-%d').date())
                    except ValueError:
                        return Response(
                            {'error': f'Formato de fecha inválido en {campo}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    setattr(trimestre, campo, data[campo])
        
        trimestre.save()
        
        return Response({
            'mensaje': 'Trimestre actualizado exitosamente',
            'trimestre': {
                'id': trimestre.id,
                'nombre': trimestre.nombre,
                'estado': trimestre.estado
            }
        })
        
    except Trimestre.DoesNotExist:
        return Response(
            {'error': 'Trimestre no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def calcular_promedios_trimestre(request, trimestre_id):
    """
    Calcula automáticamente los promedios de un trimestre
    
    POST /api/cursos/trimestres/{trimestre_id}/calcular-promedios/
    """
    try:
        trimestre = Trimestre.objects.get(id=trimestre_id)
        materias = Materia.objects.all()
        resultados = []
        
        # Filtrar materias si se especifican en la solicitud
        if request.data.get('solo_materias'):
            materias = materias.filter(id__in=request.data['solo_materias'])
        
        with transaction.atomic():
            for materia in materias:
                # Obtener estudiantes del curso de la materia
                estudiantes = Usuario.objects.filter(
                    curso=materia.curso,
                    rol__nombre='Estudiante'
                )
                
                # Filtrar estudiantes si se especifican en la solicitud
                if request.data.get('solo_estudiantes'):
                    estudiantes = estudiantes.filter(id__in=request.data['solo_estudiantes'])
                
                for estudiante in estudiantes:
                    # Obtener evaluaciones del trimestre
                    evaluaciones = Evaluacion.objects.filter(
                        materia=materia,
                        trimestre=trimestre
                    )
                    
                    print(f"Debug - Estudiante: {estudiante.nombre}, Materia: {materia.nombre}")
                    print(f"Debug - Evaluaciones encontradas: {evaluaciones.count()}")
                    
                    if evaluaciones.exists():
                        suma_ponderada = Decimal('0.0')  # ✅ USAR DECIMAL
                        total_porcentaje = Decimal('0.0')  # ✅ USAR DECIMAL
                        calificaciones_encontradas = 0
                        
                        for evaluacion in evaluaciones:
                            try:
                                calificacion = Calificacion.objects.get(
                                    evaluacion=evaluacion,
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
                                print(f"Debug - Nota ponderada: {nota_ponderada}")
                                
                            except Calificacion.DoesNotExist:
                                print(f"Debug - No se encontró calificación para evaluación: {evaluacion.titulo}")
                                continue
                        
                        # ✅ CORRECCIÓN: Cálculo con Decimal
                        if total_porcentaje > 0 and calificaciones_encontradas > 0:
                            if total_porcentaje == Decimal('100.0'):
                                promedio_evaluaciones = suma_ponderada
                            else:
                                # Normalizar proporcionalmente
                                promedio_evaluaciones = (suma_ponderada / total_porcentaje) * Decimal('100.0')
                        else:
                            promedio_evaluaciones = Decimal('0.0')
                            
                        print(f"Debug - Suma ponderada total: {suma_ponderada}")
                        print(f"Debug - Porcentaje total: {total_porcentaje}")
                        print(f"Debug - Promedio final calculado: {promedio_evaluaciones}")
                        
                    else:
                        promedio_evaluaciones = Decimal('0.0')
                        print(f"Debug - No hay evaluaciones para esta materia y trimestre")
                    
                    # Calcular asistencia
                    asistencias_query = Asistencia.objects.filter(
                        estudiante=estudiante,
                        materia=materia,
                        fecha__range=[trimestre.fecha_inicio, trimestre.fecha_fin]
                    )
                    
                    total_clases = asistencias_query.count()
                    asistencias_presentes = asistencias_query.filter(presente=True).count()
                    
                    # ✅ CORRECCIÓN: Usar Decimal para porcentaje de asistencia
                    if total_clases > 0:
                        porcentaje_asistencia = (Decimal(str(asistencias_presentes)) / Decimal(str(total_clases))) * Decimal('100.0')
                    else:
                        porcentaje_asistencia = Decimal('0.0')
                    
                    # Promedio final igual al promedio de evaluaciones
                    promedio_final = promedio_evaluaciones
                    
                    # Determinar si está aprobado
                    nota_minima = Decimal(str(trimestre.nota_minima_aprobacion))
                    porcentaje_minimo = Decimal(str(trimestre.porcentaje_asistencia_minima))
                    aprobado = (promedio_final >= nota_minima and porcentaje_asistencia >= porcentaje_minimo)
                    
                    # Crear o actualizar promedio trimestral
                    promedio_trimestral, created = PromedioTrimestral.objects.update_or_create(
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
        
    except Trimestre.DoesNotExist:
        return Response(
            {'error': 'Trimestre no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def calcular_promedios_anuales(request, año_academico):
    """Calcula promedios anuales para un año académico"""
    try:
        trimestres = Trimestre.objects.filter(año_academico=año_academico).order_by('numero')
        
        if trimestres.count() != 3:
            return Response(
                {'error': f'Se requieren exactamente 3 trimestres para calcular promedios anuales. Encontrados: {trimestres.count()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        materias = Materia.objects.all()
        resultados = []
        
        with transaction.atomic():
            for materia in materias:
                estudiantes = Usuario.objects.filter(
                    curso=materia.curso,
                    rol__nombre='Estudiante'
                )
                
                for estudiante in estudiantes:
                    # Obtener promedios trimestrales
                    promedios_trim = {}
                    asistencias_anuales = []
                    
                    for trimestre in trimestres:
                        try:
                            promedio = PromedioTrimestral.objects.get(
                                estudiante=estudiante,
                                materia=materia,
                                trimestre=trimestre
                            )
                            promedios_trim[f'trimestre_{trimestre.numero}'] = promedio.promedio_final
                            asistencias_anuales.append(promedio.porcentaje_asistencia)
                        except PromedioTrimestral.DoesNotExist:
                            promedios_trim[f'trimestre_{trimestre.numero}'] = None
                    
                    # Calcular promedio anual de asistencia
                    porcentaje_asistencia_anual = sum(asistencias_anuales) / len(asistencias_anuales) if asistencias_anuales else 0.0
                    
                    # Crear o actualizar promedio anual
                    promedio_anual, created = PromedioAnual.objects.update_or_create(
                        estudiante=estudiante,
                        materia=materia,
                        año_academico=año_academico,
                        defaults={
                            'promedio_trimestre_1': promedios_trim.get('trimestre_1'),
                            'promedio_trimestre_2': promedios_trim.get('trimestre_2'),
                            'promedio_trimestre_3': promedios_trim.get('trimestre_3'),
                            'porcentaje_asistencia_anual': porcentaje_asistencia_anual,
                            'calculado_automaticamente': True
                        }
                    )
                    
                    # Calcular promedio final anual
                    promedio_anual.calcular_promedio_anual()
                    
                    resultados.append({
                        'estudiante': f"{estudiante.nombre} {estudiante.apellido}",
                        'materia': materia.nombre,
                        'promedio_anual': float(promedio_anual.promedio_anual),
                        'aprobado_anual': promedio_anual.aprobado_anual,
                        'porcentaje_asistencia_anual': float(porcentaje_asistencia_anual),
                        'created': created
                    })
        
        return Response({
            'mensaje': f'Promedios anuales calculados para {año_academico}',
            'año_academico': año_academico,
            'total_procesados': len(resultados),
            'resultados': resultados
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reporte_trimestral(request, trimestre_id):
    """Genera reporte completo de un trimestre"""
    try:
        trimestre = Trimestre.objects.get(id=trimestre_id)
        materia_id = request.GET.get('materia_id')
        curso_id = request.GET.get('curso_id')
        
        # Filtros
        promedios = PromedioTrimestral.objects.filter(trimestre=trimestre)
        
        if materia_id:
            promedios = promedios.filter(materia_id=materia_id)
        
        if curso_id:
            promedios = promedios.filter(materia__curso_id=curso_id)
        
        # Construir reporte
        datos_reporte = []
        for promedio in promedios.select_related('estudiante', 'materia'):
            datos_reporte.append({
                'estudiante': {
                    'id': promedio.estudiante.id,
                    'nombre': f"{promedio.estudiante.nombre} {promedio.estudiante.apellido}",
                    'codigo': promedio.estudiante.codigo
                },
                'materia': {
                    'id': promedio.materia.id,
                    'nombre': promedio.materia.nombre,
                    'curso': str(promedio.materia.curso)
                },
                'promedio_evaluaciones': float(promedio.promedio_evaluaciones),
                'promedio_final': float(promedio.promedio_final),
                'porcentaje_asistencia': float(promedio.porcentaje_asistencia),
                'total_clases': promedio.total_clases,
                'asistencias': promedio.asistencias,
                'aprobado': promedio.aprobado,
                'observaciones': promedio.observaciones
            })
        
        # Estadísticas generales
        total_estudiantes = promedios.count()
        aprobados = promedios.filter(aprobado=True).count()
        reprobados = total_estudiantes - aprobados
        
        if total_estudiantes > 0:
            promedio_general = promedios.aggregate(Avg('promedio_final'))['promedio_final__avg'] or 0
            asistencia_promedio = promedios.aggregate(Avg('porcentaje_asistencia'))['porcentaje_asistencia__avg'] or 0
        else:
            promedio_general = 0
            asistencia_promedio = 0
        
        return Response({
            'trimestre': {
                'id': trimestre.id,
                'nombre': trimestre.nombre,
                'numero': trimestre.numero,
                'año_academico': trimestre.año_academico,
                'fecha_inicio': trimestre.fecha_inicio,
                'fecha_fin': trimestre.fecha_fin,
                'estado': trimestre.estado
            },
            'estadisticas': {
                'total_estudiantes': total_estudiantes,
                'aprobados': aprobados,
                'reprobados': reprobados,
                'porcentaje_aprobacion': round((aprobados / total_estudiantes * 100), 2) if total_estudiantes > 0 else 0,
                'promedio_general': round(float(promedio_general), 2),
                'asistencia_promedio': round(float(asistencia_promedio), 2)
            },
            'datos': datos_reporte
        })
        
    except Trimestre.DoesNotExist:
        return Response(
            {'error': 'Trimestre no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_reporte_anual_comparativo(request, año_academico):
    """Genera reporte comparativo anual por trimestres"""
    try:
        estudiante_id = request.GET.get('estudiante_id')
        curso_id = request.GET.get('curso_id')
        
        # Obtener trimestres del año
        trimestres = Trimestre.objects.filter(año_academico=año_academico).order_by('numero')
        
        if not trimestres.exists():
            return Response(
                {'error': f'No se encontraron trimestres para el año {año_academico}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtros base
        filtros = {'año_academico': año_academico}
        if estudiante_id:
            filtros['estudiante_id'] = estudiante_id
        if curso_id:
            filtros['materia__curso_id'] = curso_id
        
        promedios_anuales = PromedioAnual.objects.filter(**filtros).select_related('estudiante', 'materia')
        
        datos_comparativo = []
        for promedio in promedios_anuales:
            # Obtener detalles trimestrales
            detalles_trimestrales = []
            for trimestre in trimestres:
                try:
                    prom_trim = PromedioTrimestral.objects.get(
                        estudiante=promedio.estudiante,
                        materia=promedio.materia,
                        trimestre=trimestre
                    )
                    detalles_trimestrales.append({
                        'trimestre': trimestre.numero,
                        'nombre_trimestre': trimestre.nombre,
                        'promedio': float(prom_trim.promedio_final),
                        'asistencia': float(prom_trim.porcentaje_asistencia),
                        'aprobado': prom_trim.aprobado
                    })
                except PromedioTrimestral.DoesNotExist:
                    detalles_trimestrales.append({
                        'trimestre': trimestre.numero,
                        'nombre_trimestre': trimestre.nombre,
                        'promedio': None,
                        'asistencia': None,
                        'aprobado': False
                    })
            
            datos_comparativo.append({
                'estudiante': {
                    'id': promedio.estudiante.id,
                    'nombre': f"{promedio.estudiante.nombre} {promedio.estudiante.apellido}",
                    'codigo': promedio.estudiante.codigo
                },
                'materia': {
                    'id': promedio.materia.id,
                    'nombre': promedio.materia.nombre,
                    'curso': str(promedio.materia.curso)
                },
                'trimestres': detalles_trimestrales,
                'promedio_anual': float(promedio.promedio_anual),
                'asistencia_anual': float(promedio.porcentaje_asistencia_anual),
                'aprobado_anual': promedio.aprobado_anual
            })
        
        return Response({
            'año_academico': año_academico,
            'trimestres': [{'numero': t.numero, 'nombre': t.nombre} for t in trimestres],
            'total_registros': len(datos_comparativo),
            'datos': datos_comparativo
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )