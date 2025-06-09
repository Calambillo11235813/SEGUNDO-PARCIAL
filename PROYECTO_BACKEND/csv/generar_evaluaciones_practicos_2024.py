import csv
from datetime import datetime, timedelta

# Leer materias y cursos desde el archivo materia_por_curso.csv
materias_cursos = []
with open("materias_por_curso.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        materias_cursos.append({"nombre": row["nombre"], "curso_id": int(row["curso_id"])})

# Parámetros fijos
nota_maxima = 100.0
nota_minima_aprobacion = 51.0
porcentaje_nota_final_parcial = 20.0
porcentaje_nota_final_practico = 5.0
permite_entrega_tardia = True
penalizacion_tardio = 10.0

# Fechas base por trimestre para el año 2022
trimestres = [
    (10, "2024-03-01"),  # Primer trimestre
    (11, "2024-06-01"),  # Segundo trimestre
    (12, "2024-10-01"),  # Tercer trimestre
]

with open("evaluaciones_practicos_2024.csv", "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = [
        "materia","curso_id","tipo_evaluacion_id","trimestre_id","titulo","descripcion",
        "fecha_asignacion","fecha_entrega","nota_maxima","nota_minima_aprobacion",
        "porcentaje_nota_final","permite_entrega_tardia","penalizacion_tardio"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for mc in materias_cursos:
        for trimestre_id, fecha_base_str in trimestres:
            fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")
            # 3 parciales/exámenes
            for n in range(1, 4):
                fecha_asignacion = (fecha_base + timedelta(days=10*n)).strftime("%Y-%m-%d")
                fecha_entrega = (fecha_base + timedelta(days=10*n + 5)).strftime("%Y-%m-%d")
                writer.writerow({
                    "materia": mc["nombre"],
                    "curso_id": mc["curso_id"],
                    "tipo_evaluacion_id": 1,
                    "trimestre_id": trimestre_id,
                    "titulo": f"PARCIAL {n}",
                    "descripcion": f"Parcial {n} de {mc['nombre']}",
                    "fecha_asignacion": fecha_asignacion,
                    "fecha_entrega": fecha_entrega,
                    "nota_maxima": nota_maxima,
                    "nota_minima_aprobacion": nota_minima_aprobacion,
                    "porcentaje_nota_final": porcentaje_nota_final_parcial,
                    "permite_entrega_tardia": permite_entrega_tardia,
                    "penalizacion_tardio": penalizacion_tardio
                })
            # 6 practicos
            for n in range(1, 7):
                fecha_asignacion = (fecha_base + timedelta(days=3*n)).strftime("%Y-%m-%d")
                fecha_entrega = (fecha_base + timedelta(days=3*n + 4)).strftime("%Y-%m-%d")
                writer.writerow({
                    "materia": mc["nombre"],
                    "curso_id": mc["curso_id"],
                    "tipo_evaluacion_id": 2,
                    "trimestre_id": trimestre_id,
                    "titulo": f"PRÁCTICO {n}",
                    "descripcion": f"Práctico {n} de {mc['nombre']}",
                    "fecha_asignacion": fecha_asignacion,
                    "fecha_entrega": fecha_entrega,
                    "nota_maxima": nota_maxima,
                    "nota_minima_aprobacion": nota_minima_aprobacion,
                    "porcentaje_nota_final": porcentaje_nota_final_practico,
                    "permite_entrega_tardia": permite_entrega_tardia,
                    "penalizacion_tardio": penalizacion_tardio
                })

print("Archivo evaluaciones_practicos_2024.csv generado con 3 parciales y 6 prácticos por materia y curso para cada trimestre.")