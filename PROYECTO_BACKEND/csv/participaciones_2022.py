import csv
import os
import random
from datetime import datetime, timedelta

# Configuración de trimestres para 2022
TRIMESTRES = {
    # Trimestre ID: (nombre, fecha_inicio, fecha_fin)
    4: ("Primer Trimestre 2022", "2022-02-01", "2022-04-30"),
    5: ("Segundo Trimestre 2022", "2022-05-01", "2022-08-31"),
    6: ("Tercer Trimestre 2022", "2022-09-01", "2022-12-15")
}

# Descripción de criterios de participación
CRITERIOS_PARTICIPACION = [
    "Se evaluará: 1) Calidad de las intervenciones, 2) Frecuencia de participación, 3) Relevancia de los aportes",
    "Criterios: 1) Participación activa, 2) Contribución al debate, 3) Habilidad para formular preguntas",
    "Evaluación basada en: 1) Pertinencia de comentarios, 2) Capacidad de síntesis, 3) Análisis crítico",
    "Se valorará: 1) Iniciativa en el diálogo, 2) Respeto a opiniones diversas, 3) Claridad de expresión"
]

# Leer materias desde materias_por_curso.csv (igual que en generar_evaluaciones_practicos_2022.py)
def obtener_materias():
    materias_cursos = []
    with open("materias_por_curso.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            materias_cursos.append({
                "nombre": row["nombre"], 
                "curso_id": int(row["curso_id"])
            })
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

def generar_participaciones():
    materias = obtener_materias()
    evaluaciones = []
    
    for materia in materias:
        for trimestre_id in TRIMESTRES.keys():
            # Generamos 4 participaciones por materia por trimestre
            for i in range(1, 5):
                # Título de la participación
                titulo = f"PARTICIPACION {i}"
                
                # Fecha de registro dentro del trimestre
                fecha_registro = generar_fecha_registro(trimestre_id)
                
                # Porcentaje constante de 2.5
                porcentaje = 2.5
                
                # Criterios de participación aleatorios
                criterios = random.choice(CRITERIOS_PARTICIPACION)
                
                # Escala de calificación (mayormente numérica)
                escala = "NUMERICA" if random.random() < 0.9 else "CUALITATIVA"
                
                evaluaciones.append({
                    "materia": materia["nombre"],
                    "curso_id": materia["curso_id"],
                    "tipo_evaluacion_id": 3,  # ID fijo para participación
                    "trimestre_id": trimestre_id,
                    "titulo": titulo,
                    "descripcion": f"Participación en {materia['nombre']} - {TRIMESTRES[trimestre_id][0]}",
                    "porcentaje_nota_final": porcentaje,
                    "fecha_registro": fecha_registro,
                    "criterios_participacion": criterios,
                    "escala_calificacion": escala
                })
    
    return evaluaciones

def guardar_participaciones_csv(evaluaciones, archivo_salida):
    """Guarda las evaluaciones de participación en un archivo CSV"""
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        # Definir los campos que queremos en el CSV
        campos = [
            "materia", "curso_id", "tipo_evaluacion_id", "trimestre_id", 
            "titulo", "descripcion", "porcentaje_nota_final", "fecha_registro", 
            "criterios_participacion", "escala_calificacion"
        ]
        
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        
        for evaluacion in evaluaciones:
            writer.writerow(evaluacion)

if __name__ == "__main__":
    # Generar las participaciones
    participaciones = generar_participaciones()
    
    # Guardar en CSV
    archivo_salida = os.path.join(os.path.dirname(__file__), 'participaciones_2022.csv')
    guardar_participaciones_csv(participaciones, archivo_salida)
    
    print(f"Se han generado {len(participaciones)} evaluaciones de participación para el año 2022")
    print(f"Archivo guardado en: {archivo_salida}")
    print(f"Total de materias procesadas: {len(obtener_materias())}")
    print(f"Total de trimestres: {len(TRIMESTRES)}")