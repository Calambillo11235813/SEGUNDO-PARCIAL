import csv
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Configuración del tercer trimestre 2024
TERCER_TRIMESTRE_2024 = {
    "numero": 3,
    "nombre": "Tercer Trimestre 2024",
    "año_academico": 2024,
    "fecha_inicio": "2024-10-01",
    "fecha_fin": "2024-12-20",
    "trimestre_id": 12  # ID según tu base de datos
}

# Configuración de probabilidades para tercer trimestre
# Generalmente la asistencia se mantiene o mejora ligeramente al final del año
PROBABILIDAD_PRESENTE = 0.74  # 74% de asistencia (mejora gradual)
PROBABILIDAD_AUSENTE = 0.26   # 26% de ausencia
PROBABILIDAD_JUSTIFICADA = 0.20  # 20% de las ausencias son justificadas (mayor responsabilidad)

def leer_estudiantes():
    """Lee el archivo estudiantes.csv y retorna lista de estudiantes"""
    estudiantes = []
    try:
        with open("estudiantes.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                estudiantes.append({
                    "codigo": int(row["codigo"]),
                    "nombre": row["nombre"],
                    "apellido": row["apellido"],
                    "curso": int(row["curso"])
                })
        print(f"✅ Leídos {len(estudiantes)} estudiantes")
        return estudiantes
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo estudiantes.csv")
        return []
    except Exception as e:
        print(f"❌ Error leyendo estudiantes: {e}")
        return []

def leer_materias_por_curso():
    """Lee el archivo materias_por_curso.csv y retorna diccionario de materias por curso"""
    materias_por_curso = defaultdict(list)
    try:
        with open("materias_por_curso.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                curso_id = int(row["curso_id"])
                materia_nombre = row["nombre"]
                materias_por_curso[curso_id].append(materia_nombre)
        
        print(f"✅ Leídas materias para {len(materias_por_curso)} cursos")
        
        # Mostrar materias por curso para verificación
        for curso_id, materias in sorted(materias_por_curso.items()):
            print(f"   Curso {curso_id}: {len(materias)} materias ({', '.join(materias[:3])}{'...' if len(materias) > 3 else ''})")
        
        return dict(materias_por_curso)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo materias_por_curso.csv")
        return {}
    except Exception as e:
        print(f"❌ Error leyendo materias: {e}")
        return {}

def obtener_trimestre_2024():
    """Lee el archivo trimestre.csv y busca el tercer trimestre 2024"""
    try:
        with open("trimestre.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (int(row["numero"]) == 3 and 
                    int(row["año_academico"]) == 2024):
                    return {
                        "numero": int(row["numero"]),
                        "nombre": row["nombre"],
                        "año_academico": int(row["año_academico"]),
                        "fecha_inicio": row["fecha_inicio"],
                        "fecha_fin": row["fecha_fin"],
                        "trimestre_id": 12  # ID del tercer trimestre 2024
                    }
        print("⚠️  No se encontró el tercer trimestre 2024")
        return TERCER_TRIMESTRE_2024
    except FileNotFoundError:
        print("⚠️  No se encontró trimestre.csv, usando configuración por defecto")
        return TERCER_TRIMESTRE_2024
    except Exception as e:
        print(f"❌ Error leyendo trimestre: {e}")
        return TERCER_TRIMESTRE_2024

def generar_fechas_clases(fecha_inicio, fecha_fin):
    """
    Genera fechas de clases (excluyendo fines de semana y vacaciones navideñas)
    Retorna lista de fechas de lunes a viernes
    """
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    # Definir períodos especiales del tercer trimestre
    # Vacaciones navideñas (ejemplo: 21 diciembre en adelante)
    vacaciones_navidad_inicio = datetime(2024, 12, 21)
    
    # Días especiales que podrían afectar (día de muertos, etc.)
    dias_especiales = [
        datetime(2024, 11, 1),   # Día de Todos los Santos
        datetime(2024, 11, 2),   # Día de los Muertos
        datetime(2024, 12, 24),  # Nochebuena
        datetime(2024, 12, 25),  # Navidad
    ]
    
    fechas_clases = []
    fecha_actual = inicio
    
    while fecha_actual <= fin:
        # Solo días de semana (0=lunes, 6=domingo)
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            # Excluir vacaciones navideñas y días especiales
            if (fecha_actual < vacaciones_navidad_inicio and 
                fecha_actual not in dias_especiales):
                fechas_clases.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)
    
    return fechas_clases

def generar_patron_asistencia_estudiante_tercer_trimestre(total_clases):
    """
    Genera un patrón de asistencia realista para el tercer trimestre
    Los estudiantes tienden a mantener o mejorar su asistencia al final del año
    pero pueden tener algunas ausencias por estrés de fin de año
    """
    asistencias = []
    
    # Perfiles para tercer trimestre (con ligera mejora pero también variabilidad)
    perfil = random.choice([
        'excelente',    # 92-99% asistencia (consistencia alta)
        'bueno',        # 82-92% asistencia (mejora sostenida)
        'regular',      # 72-82% asistencia (estabilidad)
        'problemático', # 58-72% asistencia (mejora mínima)
        'estresado'     # 50-70% asistencia (nuevo perfil por presión de fin de año)
    ])
    
    if perfil == 'excelente':
        prob_presente = 0.95  # Alta consistencia
    elif perfil == 'bueno':
        prob_presente = 0.87  # Mejora sostenida
    elif perfil == 'regular':
        prob_presente = 0.77  # Estabilidad
    elif perfil == 'problemático':
        prob_presente = 0.65  # Mejora mínima
    else:  # estresado
        prob_presente = 0.60  # Afectado por presión de fin de año
    
    # Generar rachas realistas para tercer trimestre
    i = 0
    while i < total_clases:
        # Factor de estrés hacia el final del trimestre
        factor_final = 1.0
        if i > total_clases * 0.8:  # Últimas 20% de clases
            factor_final = 0.95  # Ligera reducción por estrés de evaluaciones finales
        
        prob_presente_ajustada = prob_presente * factor_final
        
        if random.random() < prob_presente_ajustada:
            # Racha de asistencias (1-7 días, puede ser más larga por compromiso final)
            racha_presente = random.randint(1, min(7, total_clases - i))
            for _ in range(racha_presente):
                if i < total_clases:
                    asistencias.append(True)
                    i += 1
        else:
            # Racha de ausencias (1-3 días)
            racha_ausente = random.randint(1, min(3, total_clases - i))
            for _ in range(racha_ausente):
                if i < total_clases:
                    asistencias.append(False)
                    i += 1
    
    return asistencias

def generar_asistencias_trimestre():
    """
    Función principal que genera todas las asistencias del tercer trimestre 2024
    """
    print("🚀 Iniciando generación de asistencias para el Tercer Trimestre 2024")
    
    # Cargar datos
    estudiantes = leer_estudiantes()
    if not estudiantes:
        return []
    
    materias_por_curso = leer_materias_por_curso()
    if not materias_por_curso:
        return []
    
    trimestre = obtener_trimestre_2024()
    print(f"📅 Trimestre: {trimestre['nombre']}")
    print(f"📅 Período: {trimestre['fecha_inicio']} a {trimestre['fecha_fin']}")
    print(f"🎄 Incluye período navideño y días especiales")
    
    # Generar fechas de clases
    fechas_clases = generar_fechas_clases(
        trimestre['fecha_inicio'], 
        trimestre['fecha_fin']
    )
    print(f"📚 Total de días de clase: {len(fechas_clases)} (excluyendo feriados)")
    
    # Agrupar estudiantes por curso
    estudiantes_por_curso = defaultdict(list)
    for estudiante in estudiantes:
        estudiantes_por_curso[estudiante['curso']].append(estudiante)
    
    print(f"🏫 Cursos encontrados: {list(estudiantes_por_curso.keys())}")
    
    asistencias_generadas = []
    total_asistencias = 0
    
    # Para cada curso
    for curso_id, estudiantes_curso in estudiantes_por_curso.items():
        print(f"\n📖 Procesando Curso {curso_id} ({len(estudiantes_curso)} estudiantes)")
        
        # Obtener materias del curso desde el CSV
        materias = materias_por_curso.get(curso_id, [])
        if not materias:
            print(f"   ⚠️  No se encontraron materias para el curso {curso_id}, saltando...")
            continue
            
        print(f"   📚 Materias ({len(materias)}): {', '.join(materias)}")
        
        # Para cada materia del curso
        for materia in materias:
            print(f"   📝 Generando asistencias para '{materia}'")
            
            # Para cada estudiante del curso
            for estudiante in estudiantes_curso:
                
                # Generar patrón de asistencia para tercer trimestre
                patron_asistencia = generar_patron_asistencia_estudiante_tercer_trimestre(len(fechas_clases))
                
                # Para cada fecha de clase
                for i, fecha in enumerate(fechas_clases):
                    presente = patron_asistencia[i] if i < len(patron_asistencia) else True
                    
                    # Si está ausente, determinar si está justificado
                    # Mayor probabilidad de justificación en tercer trimestre (más madurez)
                    justificada = False
                    if not presente:
                        # En diciembre, mayor probabilidad de justificación por compromisos familiares
                        prob_justificada = PROBABILIDAD_JUSTIFICADA
                        if fecha.startswith("2024-12"):
                            prob_justificada = min(0.25, PROBABILIDAD_JUSTIFICADA + 0.05)
                        
                        justificada = random.random() < prob_justificada
                    
                    asistencia = {
                        "estudiante_codigo": estudiante['codigo'],
                        "estudiante_nombre": f"{estudiante['nombre']} {estudiante['apellido']}",
                        "materia": materia,
                        "curso_id": curso_id,
                        "trimestre_id": trimestre['trimestre_id'],
                        "fecha": fecha,
                        "presente": presente,
                        "justificada": justificada
                    }
                    
                    asistencias_generadas.append(asistencia)
                    total_asistencias += 1
            
            # Progreso por materia
            if total_asistencias % 1000 == 0:
                print(f"      📊 Progreso: {total_asistencias:,} registros generados...")
    
    print(f"\n✅ Generación completada: {total_asistencias:,} registros de asistencia")
    return asistencias_generadas

def calcular_estadisticas(asistencias):
    """Calcula estadísticas de las asistencias generadas"""
    total = len(asistencias)
    presentes = sum(1 for a in asistencias if a['presente'])
    ausentes = total - presentes
    justificadas = sum(1 for a in asistencias if a['justificada'])
    
    print(f"\n📊 ESTADÍSTICAS TERCER TRIMESTRE 2024:")
    print(f"   Total registros: {total:,}")
    print(f"   Presentes: {presentes:,} ({presentes/total*100:.1f}%)")
    print(f"   Ausentes: {ausentes:,} ({ausentes/total*100:.1f}%)")
    if ausentes > 0:
        print(f"   Justificadas: {justificadas:,} ({justificadas/ausentes*100:.1f}% de ausencias)")
        print(f"   💡 Mejora esperada: +2% vs segundo trimestre")
    else:
        print(f"   Justificadas: 0 (0% de ausencias)")
    
    # Estadísticas por curso
    cursos_stats = defaultdict(lambda: {'total': 0, 'presentes': 0})
    for asistencia in asistencias:
        curso = asistencia['curso_id']
        cursos_stats[curso]['total'] += 1
        if asistencia['presente']:
            cursos_stats[curso]['presentes'] += 1
    
    print(f"\n📈 ESTADÍSTICAS POR CURSO:")
    for curso, stats in sorted(cursos_stats.items()):
        if stats['total'] > 0:
            porcentaje = stats['presentes'] / stats['total'] * 100
            print(f"   Curso {curso}: {porcentaje:.1f}% asistencia ({stats['presentes']:,}/{stats['total']:,})")
    
    # Estadísticas por materia (top 10)
    materias_stats = defaultdict(lambda: {'total': 0, 'presentes': 0})
    for asistencia in asistencias:
        materia = asistencia['materia']
        materias_stats[materia]['total'] += 1
        if asistencia['presente']:
            materias_stats[materia]['presentes'] += 1
    
    print(f"\n📚 ESTADÍSTICAS POR MATERIA (Top 10):")
    materias_ordenadas = sorted(
        materias_stats.items(), 
        key=lambda x: x[1]['total'], 
        reverse=True
    )[:10]
    
    for materia, stats in materias_ordenadas:
        if stats['total'] > 0:
            porcentaje = stats['presentes'] / stats['total'] * 100
            print(f"   {materia}: {porcentaje:.1f}% asistencia ({stats['presentes']:,}/{stats['total']:,})")
    
    # Estadísticas por mes
    print(f"\n📅 ESTADÍSTICAS POR MES:")
    meses_stats = defaultdict(lambda: {'total': 0, 'presentes': 0})
    meses_nombres = {
        '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
    }
    
    for asistencia in asistencias:
        mes = asistencia['fecha'].split('-')[1]
        meses_stats[mes]['total'] += 1
        if asistencia['presente']:
            meses_stats[mes]['presentes'] += 1
    
    for mes, stats in sorted(meses_stats.items()):
        if stats['total'] > 0:
            porcentaje = stats['presentes'] / stats['total'] * 100
            nombre_mes = meses_nombres.get(mes, f"Mes {mes}")
            print(f"   {nombre_mes}: {porcentaje:.1f}% asistencia ({stats['presentes']:,}/{stats['total']:,})")
    
    # Análisis especial del período navideño
    print(f"\n🎄 ANÁLISIS PERÍODO NAVIDEÑO:")
    diciembre_stats = meses_stats.get('12', {'total': 0, 'presentes': 0})
    if diciembre_stats['total'] > 0:
        porcentaje_dic = diciembre_stats['presentes'] / diciembre_stats['total'] * 100
        print(f"   Diciembre (pre-navidad): {porcentaje_dic:.1f}% asistencia")
        
        # Comparar con otros meses
        octubre_stats = meses_stats.get('10', {'total': 0, 'presentes': 0})
        if octubre_stats['total'] > 0:
            porcentaje_oct = octubre_stats['presentes'] / octubre_stats['total'] * 100
            diferencia = porcentaje_dic - porcentaje_oct
            print(f"   Variación Oct vs Dic: {diferencia:+.1f}%")

def guardar_asistencias_csv(asistencias, archivo_salida):
    """Guarda las asistencias en archivo CSV"""
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        campos = [
            "estudiante_codigo", "estudiante_nombre", "materia", "curso_id",
            "trimestre_id", "fecha", "presente", "justificada"
        ]
        
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        
        for asistencia in asistencias:
            writer.writerow(asistencia)
    
    print(f"💾 Archivo guardado: {archivo_salida}")

if __name__ == "__main__":
    print("=" * 70)
    print("🎓 GENERADOR DE ASISTENCIAS - TERCER TRIMESTRE 2024")
    print("📚 Usando datos reales de materias_por_curso.csv")
    print("🎄 Incluye manejo de período navideño y días especiales")
    print("📈 Patrones de asistencia con madurez de fin de año")
    print("=" * 70)
    
    # Generar asistencias
    asistencias = generar_asistencias_trimestre()
    
    if asistencias:
        # Calcular estadísticas
        calcular_estadisticas(asistencias)
        
        # Guardar archivo
        archivo_salida = os.path.join(os.path.dirname(__file__), 'tercer_trimestre_2024.csv')
        guardar_asistencias_csv(asistencias, archivo_salida)
        
        print(f"\n🎉 ¡Proceso completado exitosamente!")
        print(f"📁 Archivo generado: tercer_trimestre_2024.csv")
        print(f"📊 Total registros: {len(asistencias):,}")
        
        # Información adicional
        total_estudiantes = len(set(a['estudiante_codigo'] for a in asistencias))
        total_materias = len(set(a['materia'] for a in asistencias))
        total_cursos = len(set(a['curso_id'] for a in asistencias))
        
        print(f"\n📈 RESUMEN FINAL TERCER TRIMESTRE:")
        print(f"   👥 Estudiantes: {total_estudiantes}")
        print(f"   📚 Materias: {total_materias}")
        print(f"   🏫 Cursos: {total_cursos}")
        print(f"   📅 Días de clase: {len(set(a['fecha'] for a in asistencias))}")
        print(f"   🎄 Días especiales excluidos: Nov 1-2, Dic 21+")
        print(f"   📊 Tendencia anual: Mejora progresiva del 70% → 74%")
        
        # Progresión anual
        print(f"\n📊 PROGRESIÓN ANUAL ESPERADA:")
        print(f"   1er Trimestre: 70% asistencia base")
        print(f"   2do Trimestre: 72% asistencia (+2%)")  
        print(f"   3er Trimestre: 74% asistencia (+2%)")
        print(f"   🎯 Mejora total anual: +4 puntos porcentuales")
        
    else:
        print("❌ No se pudieron generar asistencias")
    
    print("=" * 70)