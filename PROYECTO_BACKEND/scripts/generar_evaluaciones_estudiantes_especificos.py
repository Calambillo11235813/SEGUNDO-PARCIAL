import csv
from datetime import datetime, timedelta
import os

# Datos de los estudiantes (reducido a 2)
estudiantes = [
    {"codigo": "2221", "nombre": "Ernesto", "apellido": "Solis", "curso_id": 6},
    {"codigo": "2253", "nombre": "Maria", "apellido": "Huanca", "curso_id": 7}
]

# Verificar que existe el directorio csv
csv_dir = "../csv"
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# Leer materias por curso desde el archivo CSV
materias_por_curso = {}
with open("../csv/materias_por_curso.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        curso_id = int(row["curso_id"])
        if curso_id not in materias_por_curso:
            materias_por_curso[curso_id] = []
        materias_por_curso[curso_id].append(row["nombre"])

# Mostrar cantidad de materias por curso
for curso_id, materias in materias_por_curso.items():
    print(f"Curso {curso_id}: {len(materias)} materias")

# Parámetros para evaluaciones con IDs correctos de los trimestres
# IDs según la consulta proporcionada
trimestres_por_anio = {
    2022: [
        (4, "2022-02-01"),  # Primer Trimestre 2022
        (5, "2022-05-01"),  # Segundo Trimestre 2022
        (6, "2022-10-01"),  # Tercer Trimestre 2022
    ],
    2023: [
        (7, "2023-02-01"),  # Primer Trimestre 2023
        (8, "2023-05-01"),  # Segundo Trimestre 2023
        (9, "2023-10-01"),  # Tercer Trimestre 2023
    ]
}

nota_maxima = 100.0
nota_minima_aprobacion = 51.0
porcentaje_nota_final_parcial = 20.0
porcentaje_nota_final_practico = 5.0
permite_entrega_tardia = True
penalizacion_tardio = 10.0

# Generar evaluaciones para los estudiantes específicos
evaluaciones = []

for anio, trimestres in trimestres_por_anio.items():
    for estudiante in estudiantes:
        curso_id = estudiante["curso_id"]
        if curso_id not in materias_por_curso:
            print(f"No hay materias definidas para el curso {curso_id}")
            continue
        
        materias = materias_por_curso[curso_id]
        print(f"Generando evaluaciones para {estudiante['nombre']} {estudiante['apellido']} - Curso {curso_id} - {len(materias)} materias")
        
        # Usar todas las materias (sin límite)
        for materia in materias:
            for trimestre_id, fecha_base_str in trimestres:
                fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")
                
                # 3 parciales por materia y trimestre
                for n in range(1, 4):
                    fecha_asignacion = (fecha_base + timedelta(days=10*n)).strftime("%Y-%m-%d")
                    fecha_entrega = (fecha_base + timedelta(days=10*n + 5)).strftime("%Y-%m-%d")
                    
                    evaluaciones.append({
                        "estudiante_codigo": estudiante["codigo"],
                        "estudiante_nombre": f"{estudiante['nombre']} {estudiante['apellido']}",
                        "materia": materia,
                        "curso_id": curso_id,
                        "tipo_evaluacion_id": 1,  # 1 para parciales
                        "trimestre_id": trimestre_id,
                        "titulo": f"PARCIAL {n}",
                        "descripcion": f"Parcial {n} de {materia} - {anio}",
                        "fecha_asignacion": fecha_asignacion,
                        "fecha_entrega": fecha_entrega,
                        "nota_maxima": nota_maxima,
                        "nota_minima_aprobacion": nota_minima_aprobacion,
                        "porcentaje_nota_final": porcentaje_nota_final_parcial,
                        "permite_entrega_tardia": permite_entrega_tardia,
                        "penalizacion_tardio": penalizacion_tardio
                    })
                
                # 6 prácticos por materia y trimestre
                for n in range(1, 7):
                    fecha_asignacion = (fecha_base + timedelta(days=3*n)).strftime("%Y-%m-%d")
                    fecha_entrega = (fecha_base + timedelta(days=3*n + 4)).strftime("%Y-%m-%d")
                    
                    evaluaciones.append({
                        "estudiante_codigo": estudiante["codigo"],
                        "estudiante_nombre": f"{estudiante['nombre']} {estudiante['apellido']}",
                        "materia": materia,
                        "curso_id": curso_id,
                        "tipo_evaluacion_id": 2,  # 2 para prácticos
                        "trimestre_id": trimestre_id,
                        "titulo": f"PRÁCTICO {n}",
                        "descripcion": f"Práctico {n} de {materia} - {anio}",
                        "fecha_asignacion": fecha_asignacion,
                        "fecha_entrega": fecha_entrega,
                        "nota_maxima": nota_maxima,
                        "nota_minima_aprobacion": nota_minima_aprobacion,
                        "porcentaje_nota_final": porcentaje_nota_final_practico,
                        "permite_entrega_tardia": permite_entrega_tardia,
                        "penalizacion_tardio": penalizacion_tardio
                    })

# Guardar en CSV
output_file = "../csv/evaluaciones_estudiantes.csv"
fieldnames = [
    "estudiante_codigo", "estudiante_nombre", "materia", "curso_id", "tipo_evaluacion_id",
    "trimestre_id", "titulo", "descripcion", "fecha_asignacion", "fecha_entrega",
    "nota_maxima", "nota_minima_aprobacion", "porcentaje_nota_final",
    "permite_entrega_tardia", "penalizacion_tardio"
]

with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(evaluaciones)

print(f"\nSe han generado {len(evaluaciones)} evaluaciones para los 2 estudiantes")
print(f"Archivo guardado como: {output_file}")

# Calcular estadísticas por estudiante, materia y tipo
estadisticas = {}

for e in evaluaciones:
    estudiante = e["estudiante_codigo"]
    materia = e["materia"]
    tipo = "Parcial" if e["tipo_evaluacion_id"] == 1 else "Práctico"
    
    if estudiante not in estadisticas:
        estadisticas[estudiante] = {"materias": set(), "parciales": 0, "practicos": 0}
    
    estadisticas[estudiante]["materias"].add(materia)
    
    if tipo == "Parcial":
        estadisticas[estudiante]["parciales"] += 1
    else:
        estadisticas[estudiante]["practicos"] += 1

print("\n=== ESTADÍSTICAS ===")
for estudiante_codigo, stats in estadisticas.items():
    print(f"Estudiante {estudiante_codigo}:")
    print(f"  Total materias: {len(stats['materias'])}")
    print(f"  Total parciales: {stats['parciales']}")
    print(f"  Total prácticos: {stats['practicos']}")
    print(f"  Total evaluaciones: {stats['parciales'] + stats['practicos']}")