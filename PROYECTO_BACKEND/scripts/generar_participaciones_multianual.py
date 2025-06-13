import csv
import os
import random
import sys
from datetime import datetime, timedelta

# Añadir ruta para importaciones
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# Configuración de trimestres para 2022-2025 con IDs correctos
TRIMESTRES = {
    # 2022
    4: ("Primer Trimestre 2022", "2022-02-01", "2022-04-30", 2022),
    5: ("Segundo Trimestre 2022", "2022-05-01", "2022-08-31", 2022),
    6: ("Tercer Trimestre 2022", "2022-10-01", "2022-12-20", 2022),
    # 2023
    7: ("Primer Trimestre 2023", "2023-02-01", "2023-04-30", 2023),
    8: ("Segundo Trimestre 2023", "2023-05-01", "2023-08-31", 2023),
    9: ("Tercer Trimestre 2023", "2023-10-01", "2023-12-20", 2023),
    # 2024
    10: ("Primer Trimestre 2024", "2024-02-01", "2024-04-30", 2024),
    11: ("Segundo Trimestre 2024", "2024-05-01", "2024-08-31", 2024),
    12: ("Tercer Trimestre 2024", "2024-10-01", "2024-12-20", 2024),
    # 2025 (solo primer trimestre)
    1: ("Primer Trimestre 2025", "2025-02-01", "2025-05-31", 2025)
}

# Descripción de criterios de participación
CRITERIOS_PARTICIPACION = [
    "Se evaluará: 1) Calidad de las intervenciones, 2) Frecuencia de participación, 3) Relevancia de los aportes",
    "Criterios: 1) Participación activa, 2) Contribución al debate, 3) Habilidad para formular preguntas",
    "Evaluación basada en: 1) Pertinencia de comentarios, 2) Capacidad de síntesis, 3) Análisis crítico",
    "Se valorará: 1) Iniciativa en el diálogo, 2) Respeto a opiniones diversas, 3) Claridad de expresión"
]

# Datos de los estudiantes con sus respectivos cursos
ESTUDIANTES = [
    {"codigo": "2221", "nombre": "Ernesto", "apellido": "Solis", "curso_id": 6},
    {"codigo": "2253", "nombre": "Maria", "apellido": "Huanca", "curso_id": 7},
    {"codigo": "2287", "nombre": "Marcelo", "apellido": "Limachi", "curso_id": 8}
]

# Leer materias desde materias_por_curso.csv
def obtener_materias():
    materias_cursos = []
    try:
        with open("../csv/materias_por_curso.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                materias_cursos.append({
                    "nombre": row["nombre"], 
                    "curso_id": int(row["curso_id"])
                })
    except Exception as e:
        print(f"Error al leer el archivo materias_por_curso.csv: {e}")
        # Si hay error, proporcionamos datos por defecto
        for curso_id in [6, 7, 8]:
            materias_cursos.extend([
                {"nombre": "Matemáticas", "curso_id": curso_id},
                {"nombre": "Lenguaje", "curso_id": curso_id},
                {"nombre": "Ciencias Sociales", "curso_id": curso_id}
            ])
    return materias_cursos

def generar_fecha_registro(trimestre_id):
    """Genera una fecha de registro dentro del período del trimestre"""
    inicio = datetime.strptime(TRIMESTRES[trimestre_id][1], "%Y-%m-%d")
    fin = datetime.strptime(TRIMESTRES[trimestre_id][2], "%Y-%m-%d")
    
    # Calculamos días entre inicio y fin
    dias_trimestre = (fin - inicio).days
    
    # Elegimos un día aleatorio dentro del trimestre
    dia_aleatorio = random.randint(0, dias_trimestre)
    fecha = inicio + timedelta(days=dia_aleatorio)
    
    return fecha.strftime("%Y-%m-%d")

def generar_calificacion_participacion(anio):
    """Genera una calificación de participación según el año, con progresión"""
    if anio == 2022:
        return round(random.uniform(50.0, 80.0), 1)
    elif anio == 2023:
        return round(random.uniform(55.0, 85.0), 1)
    elif anio == 2024:
        return round(random.uniform(60.0, 90.0), 1)
    else:  # 2025
        return round(random.uniform(65.0, 95.0), 1)

def generar_participaciones():
    materias = obtener_materias()
    participaciones = []
    
    # Filtrar materias por curso de estudiantes
    materias_por_curso = {}
    for materia in materias:
        curso_id = materia["curso_id"]
        if curso_id not in materias_por_curso:
            materias_por_curso[curso_id] = []
        materias_por_curso[curso_id].append(materia["nombre"])
    
    # Imprimir materias encontradas para cursos de estudiantes
    for estudiante in ESTUDIANTES:
        curso_id = estudiante["curso_id"]
        materias_curso = materias_por_curso.get(curso_id, [])
        print(f"Estudiante {estudiante['nombre']} {estudiante['apellido']} (Curso {curso_id}): {len(materias_curso)} materias")
    
    # Generar participaciones para cada estudiante, por cada materia, por cada trimestre
    for estudiante in ESTUDIANTES:
        curso_id = estudiante["curso_id"]
        materias_estudiante = materias_por_curso.get(curso_id, [])
        
        if not materias_estudiante:
            print(f"No se encontraron materias para el curso {curso_id} del estudiante {estudiante['nombre']} {estudiante['apellido']}")
            continue
            
        for trimestre_id, datos_trimestre in TRIMESTRES.items():
            nombre_trimestre, fecha_inicio, fecha_fin, anio = datos_trimestre
            
            for materia in materias_estudiante:
                # Generamos entre 3 y 6 participaciones por materia por trimestre
                num_participaciones = random.randint(3, 6)
                
                for i in range(1, num_participaciones + 1):
                    # Título de la participación
                    titulo = f"PARTICIPACION {i}"
                    
                    # Fecha de registro dentro del trimestre
                    fecha_registro = generar_fecha_registro(trimestre_id)
                    
                    # Porcentaje aleatorio entre 1 y 3
                    porcentaje = random.uniform(1.0, 3.0)
                    porcentaje = round(porcentaje, 1)
                    
                    # Criterios de participación aleatorios
                    criterios = random.choice(CRITERIOS_PARTICIPACION)
                    
                    # Descripción combinada con criterios
                    descripcion = f"Participación {i} en clase de {materia} - {nombre_trimestre}. {criterios}"
                    
                    # Calificación con progresión según el año
                    calificacion = generar_calificacion_participacion(anio)
                    
                    participaciones.append({
                        "estudiante_codigo": estudiante["codigo"],
                        "estudiante_nombre": f"{estudiante['nombre']} {estudiante['apellido']}",
                        "materia": materia,
                        "curso_id": curso_id,
                        "tipo_evaluacion_id": 3,  # ID fijo para participación
                        "trimestre_id": trimestre_id,
                        "titulo": titulo,
                        "descripcion": descripcion,
                        "fecha_registro": fecha_registro,
                        "porcentaje_nota_final": porcentaje,
                        "calificacion": calificacion,
                        "anio": anio
                    })
    
    return participaciones

def guardar_participaciones_csv(participaciones, archivo_salida):
    """Guarda las participaciones en un archivo CSV"""
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        # Definir los campos para el CSV
        campos = [
            "estudiante_codigo", "estudiante_nombre", "materia", "curso_id", 
            "tipo_evaluacion_id", "trimestre_id", "titulo", "descripcion", 
            "fecha_registro", "porcentaje_nota_final", "calificacion", "anio"
        ]
        
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        
        for participacion in participaciones:
            writer.writerow(participacion)

def estadisticas_participaciones(participaciones):
    """Genera estadísticas de las participaciones creadas"""
    total_por_anio = {2022: 0, 2023: 0, 2024: 0, 2025: 0}
    total_por_estudiante = {est["codigo"]: 0 for est in ESTUDIANTES}
    total_por_trimestre = {trimestre_id: 0 for trimestre_id in TRIMESTRES.keys()}
    
    for p in participaciones:
        anio = p["anio"]
        total_por_anio[anio] += 1
        
        estudiante_codigo = p["estudiante_codigo"]
        total_por_estudiante[estudiante_codigo] += 1
        
        trimestre_id = p["trimestre_id"]
        total_por_trimestre[trimestre_id] += 1
    
    print("\nESTADÍSTICAS DE PARTICIPACIONES:")
    print("-------------------------------")
    
    print("\nTotal por año:")
    for anio, total in total_por_anio.items():
        print(f"  {anio}: {total} participaciones")
    
    print("\nTotal por estudiante:")
    for estudiante in ESTUDIANTES:
        codigo = estudiante["codigo"]
        nombre_completo = f"{estudiante['nombre']} {estudiante['apellido']}"
        total = total_por_estudiante[codigo]
        print(f"  {nombre_completo} ({codigo}): {total} participaciones")
    
    print("\nTotal por trimestre:")
    for trimestre_id, datos in TRIMESTRES.items():
        nombre_trimestre = datos[0]
        anio = datos[3]
        total = total_por_trimestre[trimestre_id]
        print(f"  {nombre_trimestre} ({anio}) [ID: {trimestre_id}]: {total} participaciones")

if __name__ == "__main__":
    # Verificar que existe el directorio csv
    csv_dir = "../csv"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    
    # Generar las participaciones
    participaciones = generar_participaciones()
    
    # Guardar en CSV
    archivo_salida = os.path.join(csv_dir, 'participaciones_2022_2025.csv')
    guardar_participaciones_csv(participaciones, archivo_salida)
    
    # Mostrar estadísticas
    print(f"\nSe han generado {len(participaciones)} participaciones para los años 2022-2025")
    print(f"Archivo guardado en: {archivo_salida}")
    
    estadisticas_participaciones(participaciones)