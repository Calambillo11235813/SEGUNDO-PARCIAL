import os
import csv
import sys
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Añadir ruta para importaciones Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# Datos de trimestres
TRIMESTRES = {
    # 2022
    4: {"nombre": "Primer Trimestre 2022", "fecha_inicio": "2022-02-01", "fecha_fin": "2022-04-30", "año": 2022},
    5: {"nombre": "Segundo Trimestre 2022", "fecha_inicio": "2022-05-01", "fecha_fin": "2022-08-31", "año": 2022},
    6: {"nombre": "Tercer Trimestre 2022", "fecha_inicio": "2022-10-01", "fecha_fin": "2022-12-20", "año": 2022},
    # 2023
    7: {"nombre": "Primer Trimestre 2023", "fecha_inicio": "2023-02-01", "fecha_fin": "2023-04-30", "año": 2023},
    8: {"nombre": "Segundo Trimestre 2023", "fecha_inicio": "2023-05-01", "fecha_fin": "2023-08-31", "año": 2023},
    9: {"nombre": "Tercer Trimestre 2023", "fecha_inicio": "2023-10-01", "fecha_fin": "2023-12-20", "año": 2023},
    # 2024
    10: {"nombre": "Primer Trimestre 2024", "fecha_inicio": "2024-02-01", "fecha_fin": "2024-04-30", "año": 2024},
    11: {"nombre": "Segundo Trimestre 2024", "fecha_inicio": "2024-05-01", "fecha_fin": "2024-08-31", "año": 2024},
    12: {"nombre": "Tercer Trimestre 2024", "fecha_inicio": "2024-10-01", "fecha_fin": "2024-12-20", "año": 2024},
    # 2025 (solo primer trimestre)
    1: {"nombre": "Primer Trimestre 2025", "fecha_inicio": "2025-02-01", "fecha_fin": "2025-05-31", "año": 2025}
}

# Configuración de probabilidades realistas con progresión positiva por año
PROBABILIDAD_POR_AÑO = {
    2022: {"presente": 0.70, "ausente": 0.30, "justificada": 0.40},  # 70% asistencia, 40% de ausencias justificadas
    2023: {"presente": 0.75, "ausente": 0.25, "justificada": 0.50},  # 75% asistencia, 50% de ausencias justificadas
    2024: {"presente": 0.82, "ausente": 0.18, "justificada": 0.60},  # 82% asistencia, 60% de ausencias justificadas
    2025: {"presente": 0.88, "ausente": 0.12, "justificada": 0.70}   # 88% asistencia, 70% de ausencias justificadas
}

# Datos de los estudiantes
ESTUDIANTES = [
    {"codigo": "2221", "nombre": "Ernesto", "apellido": "Solis", "curso_id": 6},
    {"codigo": "2253", "nombre": "Maria", "apellido": "Huanca", "curso_id": 7}
]

def leer_materias_por_curso():
    """Lee el archivo materias_por_curso.csv y retorna diccionario de materias por curso"""
    materias_por_curso = defaultdict(list)
    try:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "materias_por_curso.csv")
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                curso_id = int(row["curso_id"])
                materia_nombre = row["nombre"]
                materias_por_curso[curso_id].append(materia_nombre)
        
        print(f"✅ Leídas materias para {len(materias_por_curso)} cursos")
        
        # Mostrar materias por curso para verificación
        for curso_id, materias in sorted(materias_por_curso.items()):
            if curso_id in [6, 7]:  # Solo mostrar para nuestros estudiantes
                print(f"   Curso {curso_id}: {len(materias)} materias ({', '.join(materias[:3])}{'...' if len(materias) > 3 else ''})")
        
        return dict(materias_por_curso)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo materias_por_curso.csv")
        print(f"Ruta buscada: {csv_path}")
        # Proporcionar algunos datos por defecto
        default_materias = {
            6: ["Matemáticas", "Lenguaje", "Ciencias Sociales", "Ciencias Naturales"],
            7: ["Matemáticas", "Lenguaje", "Ciencias Sociales", "Ciencias Naturales"]
        }
        print("Usando materias por defecto:")
        for curso_id, materias in default_materias.items():
            print(f"   Curso {curso_id}: {len(materias)} materias ({', '.join(materias)})")
        return default_materias
    except Exception as e:
        print(f"❌ Error leyendo materias: {e}")
        return {
            6: ["Matemáticas", "Lenguaje", "Ciencias Sociales", "Ciencias Naturales"],
            7: ["Matemáticas", "Lenguaje", "Ciencias Sociales", "Ciencias Naturales"]
        }

def generar_fechas_clases(fecha_inicio, fecha_fin):
    """
    Genera fechas de clases (excluyendo fines de semana)
    Retorna lista de fechas de lunes a viernes
    """
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    fechas_clases = []
    fecha_actual = inicio
    
    while fecha_actual <= fin:
        # Solo días de semana (0=lunes, 6=domingo)
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            fechas_clases.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)
    
    return fechas_clases

def generar_patron_asistencia_estudiante(total_clases, año):
    """
    Genera un patrón de asistencia realista para un estudiante
    Considera tendencias y rachas de asistencia/ausencia
    """
    asistencias = []
    
    # Obtener probabilidades según el año
    prob_presente = PROBABILIDAD_POR_AÑO[año]["presente"]
    prob_justificada = PROBABILIDAD_POR_AÑO[año]["justificada"]
    
    # Generar rachas realistas
    i = 0
    while i < total_clases:
        if random.random() < prob_presente:
            # Racha de asistencias (1-8 días)
            racha_presente = random.randint(1, min(8, total_clases - i))
            for _ in range(racha_presente):
                if i < total_clases:
                    asistencias.append({"presente": True, "justificada": False})
                    i += 1
        else:
            # Racha de ausencias (1-3 días)
            racha_ausente = random.randint(1, min(3, total_clases - i))
            for _ in range(racha_ausente):
                if i < total_clases:
                    justificada = random.random() < prob_justificada
                    asistencias.append({"presente": False, "justificada": justificada})
                    i += 1
    
    return asistencias

def generar_asistencias_por_trimestre(estudiantes, materias_por_curso, trimestre_id, trimestre_info):
    """Genera asistencias para un trimestre específico"""
    print(f"\n🗓️  Generando asistencias para {trimestre_info['nombre']}")
    
    # Generar fechas de clases para este trimestre
    fechas_clases = generar_fechas_clases(
        trimestre_info['fecha_inicio'], 
        trimestre_info['fecha_fin']
    )
    
    print(f"   📅 Período: {trimestre_info['fecha_inicio']} a {trimestre_info['fecha_fin']}")
    print(f"   📚 Total de días de clase: {len(fechas_clases)}")
    
    asistencias_generadas = []
    
    # Para cada estudiante
    for estudiante in estudiantes:
        curso_id = estudiante['curso_id']
        
        # Obtener materias del estudiante
        materias = materias_por_curso.get(curso_id, [])
        if not materias:
            print(f"   ⚠️  No se encontraron materias para el curso {curso_id} del estudiante {estudiante['nombre']} {estudiante['apellido']}")
            continue
        
        print(f"   👤 Generando para {estudiante['nombre']} {estudiante['apellido']} - {len(materias)} materias")
        
        # Para cada materia del estudiante
        for materia in materias:
            # Generar patrón de asistencia para esta materia
            patron_asistencia = generar_patron_asistencia_estudiante(
                len(fechas_clases), 
                trimestre_info['año']
            )
            
            # Para cada fecha de clase
            for i, fecha in enumerate(fechas_clases):
                # Obtener estado de asistencia
                estado = patron_asistencia[i]
                
                asistencia = {
                    "estudiante_codigo": estudiante['codigo'],
                    "estudiante_nombre": f"{estudiante['nombre']} {estudiante['apellido']}",
                    "materia": materia,
                    "curso_id": curso_id,
                    "trimestre_id": trimestre_id,
                    "fecha": fecha,
                    "presente": estado['presente'],
                    "justificada": estado['justificada']
                }
                
                asistencias_generadas.append(asistencia)
    
    print(f"   ✅ Generadas {len(asistencias_generadas)} asistencias para este trimestre")
    return asistencias_generadas

def guardar_asistencias_csv(asistencias, archivo_salida):
    """Guarda las asistencias en archivo CSV"""
    directorio = os.path.dirname(archivo_salida)
    if not os.path.exists(directorio):
        os.makedirs(directorio)
        
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

def calcular_estadisticas(asistencias):
    """Calcula estadísticas de las asistencias generadas"""
    if not asistencias:
        print("❌ No hay asistencias para calcular estadísticas")
        return
        
    total = len(asistencias)
    presentes = sum(1 for a in asistencias if a['presente'])
    ausentes = total - presentes
    justificadas = sum(1 for a in asistencias if not a['presente'] and a['justificada'])
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total registros: {total:,}")
    print(f"   Presentes: {presentes:,} ({presentes/total*100:.1f}%)")
    print(f"   Ausentes: {ausentes:,} ({ausentes/total*100:.1f}%)")
    if ausentes > 0:
        print(f"   Justificadas: {justificadas:,} ({justificadas/ausentes*100:.1f}% de ausencias)")
    else:
        print(f"   Justificadas: 0 (0% de ausencias)")
    
    # Estadísticas por año
    stats_por_año = defaultdict(lambda: {"total": 0, "presentes": 0, "ausentes": 0, "justificadas": 0})
    
    for asistencia in asistencias:
        trimestre_id = asistencia["trimestre_id"]
        año = TRIMESTRES[trimestre_id]["año"]
        
        stats = stats_por_año[año]
        stats["total"] += 1
        
        if asistencia["presente"]:
            stats["presentes"] += 1
        else:
            stats["ausentes"] += 1
            if asistencia["justificada"]:
                stats["justificadas"] += 1
    
    print(f"\n📈 ESTADÍSTICAS POR AÑO:")
    for año in sorted(stats_por_año.keys()):
        stats = stats_por_año[año]
        porcentaje_asistencia = stats["presentes"] / stats["total"] * 100 if stats["total"] > 0 else 0
        porcentaje_justificadas = stats["justificadas"] / stats["ausentes"] * 100 if stats["ausentes"] > 0 else 0
        
        print(f"   {año}: {porcentaje_asistencia:.1f}% asistencia | " 
              f"{stats['presentes']:,}/{stats['total']:,} presencias | "
              f"{porcentaje_justificadas:.1f}% ausencias justificadas")
    
    # Estadísticas por estudiante
    print(f"\n👨‍🎓 ESTADÍSTICAS POR ESTUDIANTE:")
    estudiantes_stats = defaultdict(lambda: {"total": 0, "presentes": 0, "ausentes": 0, "justificadas": 0})
    
    for asistencia in asistencias:
        est_codigo = asistencia["estudiante_codigo"]
        est_nombre = asistencia["estudiante_nombre"]
        
        stats = estudiantes_stats[(est_codigo, est_nombre)]
        stats["total"] += 1
        
        if asistencia["presente"]:
            stats["presentes"] += 1
        else:
            stats["ausentes"] += 1
            if asistencia["justificada"]:
                stats["justificadas"] += 1
    
    for (codigo, nombre), stats in sorted(estudiantes_stats.items()):
        porcentaje_asistencia = stats["presentes"] / stats["total"] * 100 if stats["total"] > 0 else 0
        porcentaje_justificadas = stats["justificadas"] / stats["ausentes"] * 100 if stats["ausentes"] > 0 else 0
        
        print(f"   {nombre} ({codigo}): {porcentaje_asistencia:.1f}% asistencia | "
              f"{stats['presentes']:,}/{stats['total']:,} presencias | "
              f"{porcentaje_justificadas:.1f}% ausencias justificadas")

def generar_asistencias_multianuales():
    """Función principal que genera todas las asistencias para múltiples años"""
    print("=" * 70)
    print("🎓 GENERADOR DE ASISTENCIAS MULTIANUALES (2022-2025)")
    print("=" * 70)
    
    # Cargar materias por curso
    materias_por_curso = leer_materias_por_curso()
    
    # Todas las asistencias generadas
    asistencias_totales = []
    
    # Generar asistencias para cada trimestre
    for trimestre_id, trimestre_info in sorted(TRIMESTRES.items()):
        asistencias_trimestre = generar_asistencias_por_trimestre(
            ESTUDIANTES,
            materias_por_curso,
            trimestre_id,
            trimestre_info
        )
        
        asistencias_totales.extend(asistencias_trimestre)
    
    # Calcular estadísticas
    calcular_estadisticas(asistencias_totales)
    
    # Guardar archivo
    archivo_salida = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv", "asistencias_multianuales.csv")
    guardar_asistencias_csv(asistencias_totales, archivo_salida)
    
    print(f"\n🎉 ¡Proceso completado exitosamente!")
    print(f"📁 Archivo generado: asistencias_multianuales.csv")
    print(f"📊 Total registros: {len(asistencias_totales):,}")
    
    # Información adicional
    total_estudiantes = len(set(a['estudiante_codigo'] for a in asistencias_totales))
    total_materias = len(set(a['materia'] for a in asistencias_totales))
    total_cursos = len(set(a['curso_id'] for a in asistencias_totales))
    total_trimestres = len(set(a['trimestre_id'] for a in asistencias_totales))
    
    print(f"\n📈 RESUMEN FINAL:")
    print(f"   👥 Estudiantes: {total_estudiantes}")
    print(f"   📚 Materias: {total_materias}")
    print(f"   🏫 Cursos: {total_cursos}")
    print(f"   🗓️ Trimestres: {total_trimestres}")
    print(f"   📅 Días de clase: {len(set(a['fecha'] for a in asistencias_totales))}")
    
    print("=" * 70)
    
    return asistencias_totales

if __name__ == "__main__":
    generar_asistencias_multianuales()