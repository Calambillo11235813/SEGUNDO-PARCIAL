import csv
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Configuración del primer trimestre 2022
PRIMER_TRIMESTRE_2022 = {
    "numero": 1,
    "nombre": "Primer Trimestre 2022",
    "año_academico": 2022,
    "fecha_inicio": "2022-02-01",
    "fecha_fin": "2022-04-30",
    "trimestre_id": 4  # ID según tu base de datos
}

# Configuración de probabilidades para 2022 (menor que 2023)
PROBABILIDAD_PRESENTE = 0.62  # 62% de asistencia (6% menos que 2023)
PROBABILIDAD_AUSENTE = 0.38   # 38% de ausencia
PROBABILIDAD_JUSTIFICADA = 0.08  # 8% de las ausencias son justificadas

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

def obtener_trimestre_2022():
    """Lee el archivo trimestre.csv y busca el primer trimestre 2022"""
    try:
        with open("trimestre.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (int(row["numero"]) == 1 and 
                    int(row["año_academico"]) == 2022):
                    return {
                        "numero": int(row["numero"]),
                        "nombre": row["nombre"],
                        "año_academico": int(row["año_academico"]),
                        "fecha_inicio": row["fecha_inicio"],
                        "fecha_fin": row["fecha_fin"],
                        "trimestre_id": 4  # ID del primer trimestre 2022
                    }
        print("⚠️  No se encontró el primer trimestre 2022")
        return PRIMER_TRIMESTRE_2022
    except FileNotFoundError:
        print("⚠️  No se encontró trimestre.csv, usando configuración por defecto")
        return PRIMER_TRIMESTRE_2022
    except Exception as e:
        print(f"❌ Error leyendo trimestre: {e}")
        return PRIMER_TRIMESTRE_2022

def generar_fechas_clases(fecha_inicio, fecha_fin):
    """
    Genera fechas de clases (excluyendo fines de semana y Semana Santa 2022)
    Retorna lista de fechas de lunes a viernes
    """
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    # Semana Santa 2022: 11-18 de abril
    semana_santa_inicio = datetime(2022, 4, 11)
    semana_santa_fin = datetime(2022, 4, 18)
    
    fechas_clases = []
    fecha_actual = inicio
    
    while fecha_actual <= fin:
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            # Excluir Semana Santa
            if not (semana_santa_inicio <= fecha_actual <= semana_santa_fin):
                fechas_clases.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)
    
    return fechas_clases

def generar_patron_asistencia_estudiante_2022(total_clases):
    """
    Genera un patrón de asistencia para 2022
    Menor rendimiento que años posteriores (período inicial/adaptación)
    """
    asistencias = []
    
    # Perfiles para 2022 (año de menor rendimiento)
    perfil = random.choice([
        'excelente',    # 75-85% asistencia (menor que años posteriores)
        'bueno',        # 65-75% asistencia
        'regular',      # 55-65% asistencia
        'problemático', # 40-55% asistencia
        'irregular'     # 25-40% asistencia (más común en 2022)
    ])
    
    # Pesos diferentes para 2022 (más estudiantes con problemas)
    perfil = random.choices(
        ['excelente', 'bueno', 'regular', 'problemático', 'irregular'],
        weights=[15, 20, 25, 25, 15]  # Más peso en categorías bajas
    )[0]
    
    if perfil == 'excelente':
        prob_presente = 0.80
    elif perfil == 'bueno':
        prob_presente = 0.70
    elif perfil == 'regular':
        prob_presente = 0.60
    elif perfil == 'problemático':
        prob_presente = 0.47
    else:  # irregular
        prob_presente = 0.32
    
    # Generar rachas más cortas y erráticas para 2022
    i = 0
    while i < total_clases:
        if random.random() < prob_presente:
            # Rachas de asistencia muy cortas en 2022
            racha_presente = random.randint(1, min(3, total_clases - i))
            for _ in range(racha_presente):
                if i < total_clases:
                    asistencias.append(True)
                    i += 1
        else:
            # Rachas de ausencia más largas en 2022
            racha_ausente = random.randint(1, min(5, total_clases - i))
            for _ in range(racha_ausente):
                if i < total_clases:
                    asistencias.append(False)
                    i += 1
    
    return asistencias

def generar_asistencias_trimestre():
    """
    Función principal que genera todas las asistencias del primer trimestre 2022
    """
    print("🚀 Iniciando generación de asistencias para el Primer Trimestre 2022")
    
    # Cargar datos
    estudiantes = leer_estudiantes()
    if not estudiantes:
        return []
    
    materias_por_curso = leer_materias_por_curso()
    if not materias_por_curso:
        return []
    
    trimestre = obtener_trimestre_2022()
    print(f"📅 Trimestre: {trimestre['nombre']}")
    print(f"📅 Período: {trimestre['fecha_inicio']} a {trimestre['fecha_fin']}")
    print(f"📉 Año inicial - menor asistencia base")
    print(f"🌸 Incluye manejo de Semana Santa 2022")
    
    # Generar fechas de clases
    fechas_clases = generar_fechas_clases(
        trimestre['fecha_inicio'], 
        trimestre['fecha_fin']
    )
    print(f"📚 Total de días de clase: {len(fechas_clases)} (excluyendo Semana Santa)")
    
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
                
                # Generar patrón de asistencia para 2022
                patron_asistencia = generar_patron_asistencia_estudiante_2022(len(fechas_clases))
                
                # Para cada fecha de clase
                for i, fecha in enumerate(fechas_clases):
                    presente = patron_asistencia[i] if i < len(patron_asistencia) else True
                    
                    # Si está ausente, determinar si está justificado
                    justificada = False
                    if not presente:
                        justificada = random.random() < PROBABILIDAD_JUSTIFICADA
                    
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
    
    print(f"\n📊 ESTADÍSTICAS PRIMER TRIMESTRE 2022:")
    print(f"   Total registros: {total:,}")
    print(f"   Presentes: {presentes:,} ({presentes/total*100:.1f}%)")
    print(f"   Ausentes: {ausentes:,} ({ausentes/total*100:.1f}%)")
    if ausentes > 0:
        print(f"   Justificadas: {justificadas:,} ({justificadas/ausentes*100:.1f}% de ausencias)")
        print(f"   💡 Año inicial: Base menor que años posteriores")
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
    print("🎓 GENERADOR DE ASISTENCIAS - PRIMER TRIMESTRE 2022")
    print("📉 Año inicial - menor rendimiento base")
    print("🌸 Incluye manejo de Semana Santa")
    print("📊 Base: 62% asistencia promedio")
    print("=" * 70)
    
    # Generar asistencias
    asistencias = generar_asistencias_trimestre()
    
    if asistencias:
        # Calcular estadísticas
        calcular_estadisticas(asistencias)
        
        # Guardar archivo
        archivo_salida = os.path.join(os.path.dirname(__file__), 'primer_trimestre_2022.csv')
        guardar_asistencias_csv(asistencias, archivo_salida)
        
        print(f"\n🎉 ¡Proceso completado exitosamente!")
        print(f"📁 Archivo generado: primer_trimestre_2022.csv")
        print(f"📊 Total registros: {len(asistencias):,}")
        print(f"📈 Línea base establecida para progresión 2022→2023→2024")
        
    else:
        print("❌ No se pudieron generar asistencias")
    
    print("=" * 70)