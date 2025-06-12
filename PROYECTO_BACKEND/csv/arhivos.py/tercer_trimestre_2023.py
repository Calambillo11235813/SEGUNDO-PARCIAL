import csv
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Configuración del tercer trimestre 2023
TERCER_TRIMESTRE_2023 = {
    "numero": 3,
    "nombre": "Tercer Trimestre 2023",
    "año_academico": 2023,
    "fecha_inicio": "2023-10-01",
    "fecha_fin": "2023-12-20",
    "trimestre_id": 9  # ID según tu base de datos
}

# Configuración de probabilidades para tercer trimestre 2023
PROBABILIDAD_PRESENTE = 0.72  # 72% de asistencia (mejora continua)
PROBABILIDAD_AUSENTE = 0.28   # 28% de ausencia
PROBABILIDAD_JUSTIFICADA = 0.16  # 16% de las ausencias son justificadas

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
        return dict(materias_por_curso)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo materias_por_curso.csv")
        return {}
    except Exception as e:
        print(f"❌ Error leyendo materias: {e}")
        return {}

def obtener_trimestre_2023():
    """Lee el archivo trimestre.csv y busca el tercer trimestre 2023"""
    try:
        with open("trimestre.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (int(row["numero"]) == 3 and 
                    int(row["año_academico"]) == 2023):
                    return {
                        "numero": int(row["numero"]),
                        "nombre": row["nombre"],
                        "año_academico": int(row["año_academico"]),
                        "fecha_inicio": row["fecha_inicio"],
                        "fecha_fin": row["fecha_fin"],
                        "trimestre_id": 9  # ID del tercer trimestre 2023
                    }
        print("⚠️  No se encontró el tercer trimestre 2023")
        return TERCER_TRIMESTRE_2023
    except FileNotFoundError:
        print("⚠️  No se encontró trimestre.csv, usando configuración por defecto")
        return TERCER_TRIMESTRE_2023
    except Exception as e:
        print(f"❌ Error leyendo trimestre: {e}")
        return TERCER_TRIMESTRE_2023

def generar_fechas_clases(fecha_inicio, fecha_fin):
    """
    Genera fechas de clases (excluyendo fines de semana y vacaciones navideñas)
    Retorna lista de fechas de lunes a viernes
    """
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    # Días especiales del tercer trimestre 2023
    vacaciones_navidad_inicio = datetime(2023, 12, 21)
    dias_especiales = [
        datetime(2023, 11, 1),   # Día de Todos los Santos
        datetime(2023, 11, 2),   # Día de los Muertos
        datetime(2023, 12, 24),  # Nochebuena
        datetime(2023, 12, 25),  # Navidad
    ]
    
    fechas_clases = []
    fecha_actual = inicio
    
    while fecha_actual <= fin:
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            # Excluir vacaciones navideñas y días especiales
            if (fecha_actual < vacaciones_navidad_inicio and 
                fecha_actual not in dias_especiales):
                fechas_clases.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)
    
    return fechas_clases

def generar_patron_asistencia_estudiante_tercer_trimestre_2023(total_clases):
    """
    Genera un patrón de asistencia para tercer trimestre 2023
    Mayor madurez que primeros trimestres pero menor que 2024
    """
    asistencias = []
    
    # Perfiles para tercer trimestre 2023
    perfil = random.choice([
        'excelente',    # 88-98% asistencia
        'bueno',        # 78-88% asistencia
        'regular',      # 68-78% asistencia
        'problemático', # 55-68% asistencia
        'irregular'     # 45-60% asistencia
    ])
    
    if perfil == 'excelente':
        prob_presente = 0.93
    elif perfil == 'bueno':
        prob_presente = 0.83
    elif perfil == 'regular':
        prob_presente = 0.73
    elif perfil == 'problemático':
        prob_presente = 0.61
    else:  # irregular
        prob_presente = 0.52
    
    # Generar rachas realistas para tercer trimestre
    i = 0
    while i < total_clases:
        # Factor de compromiso final del año
        factor_final = 1.0
        if i > total_clases * 0.75:  # Últimas 25% de clases
            factor_final = 1.05  # Ligero aumento por compromiso de fin de año
        
        prob_presente_ajustada = min(0.98, prob_presente * factor_final)
        
        if random.random() < prob_presente_ajustada:
            # Rachas de asistencia más largas por madurez
            racha_presente = random.randint(1, min(6, total_clases - i))
            for _ in range(racha_presente):
                if i < total_clases:
                    asistencias.append(True)
                    i += 1
        else:
            # Rachas de ausencia más cortas
            racha_ausente = random.randint(1, min(2, total_clases - i))
            for _ in range(racha_ausente):
                if i < total_clases:
                    asistencias.append(False)
                    i += 1
    
    return asistencias

def generar_asistencias_trimestre():
    """
    Función principal que genera todas las asistencias del tercer trimestre 2023
    """
    print("🚀 Iniciando generación de asistencias para el Tercer Trimestre 2023")
    
    # Cargar datos
    estudiantes = leer_estudiantes()
    if not estudiantes:
        return []
    
    materias_por_curso = leer_materias_por_curso()
    if not materias_por_curso:
        return []
    
    trimestre = obtener_trimestre_2023()
    print(f"📅 Trimestre: {trimestre['nombre']}")
    print(f"📅 Período: {trimestre['fecha_inicio']} a {trimestre['fecha_fin']}")
    print(f"🎄 Incluye período navideño 2023")
    
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
        
        # Obtener materias del curso
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
                patron_asistencia = generar_patron_asistencia_estudiante_tercer_trimestre_2023(len(fechas_clases))
                
                # Para cada fecha de clase
                for i, fecha in enumerate(fechas_clases):
                    presente = patron_asistencia[i] if i < len(patron_asistencia) else True
                    
                    # Si está ausente, determinar si está justificado
                    justificada = False
                    if not presente:
                        # Mayor probabilidad de justificación en diciembre por compromisos familiares
                        prob_justificada = PROBABILIDAD_JUSTIFICADA
                        if fecha.startswith("2023-12"):
                            prob_justificada = min(0.22, PROBABILIDAD_JUSTIFICADA + 0.06)
                        
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
    
    print(f"\n📊 ESTADÍSTICAS TERCER TRIMESTRE 2023:")
    print(f"   Total registros: {total:,}")
    print(f"   Presentes: {presentes:,} ({presentes/total*100:.1f}%)")
    print(f"   Ausentes: {ausentes:,} ({ausentes/total*100:.1f}%)")
    if ausentes > 0:
        print(f"   Justificadas: {justificadas:,} ({justificadas/ausentes*100:.1f}% de ausencias)")
        print(f"   💡 Progresión anual 2023: 68% → 70% → 72%")
    else:
        print(f"   Justificadas: 0 (0% de ausencias)")

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
    print("🎓 GENERADOR DE ASISTENCIAS - TERCER TRIMESTRE 2023")
    print("🎄 Período navideño | Madurez de fin de año")
    print("📈 Culminación del progreso anual 2023")
    print("=" * 70)
    
    # Generar asistencias
    asistencias = generar_asistencias_trimestre()
    
    if asistencias:
        # Calcular estadísticas
        calcular_estadisticas(asistencias)
        
        # Guardar archivo
        archivo_salida = os.path.join(os.path.dirname(__file__), 'tercer_trimestre_2023.csv')
        guardar_asistencias_csv(asistencias, archivo_salida)
        
        print(f"\n🎉 ¡Proceso completado exitosamente!")
        print(f"📁 Archivo generado: tercer_trimestre_2023.csv")
        print(f"📊 Total registros: {len(asistencias):,}")
        
        print(f"\n📈 PROGRESIÓN COMPLETA 2023:")
        print(f"   1er Trimestre: 68% asistencia (adaptación)")
        print(f"   2do Trimestre: 70% asistencia (+2%)")  
        print(f"   3er Trimestre: 72% asistencia (+2%)")
        print(f"   🎯 Mejora total año 2023: +4 puntos")
        
    else:
        print("❌ No se pudieron generar asistencias")
    
    print("=" * 70)