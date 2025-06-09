import csv
import random
from datetime import datetime, timedelta

# Leer estudiantes
estudiantes = []
with open("estudiantes.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        estudiantes.append({
            "codigo": row["codigo"],
            "nombre": row["nombre"],
            "apellido": row["apellido"],
            "curso": int(row["curso"])
        })

# Leer evaluaciones (solo entregables)
evaluaciones = []
with open("evaluaciones_practicos_2024.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Crear un identificador único para cada evaluación
        evaluacion_id = f"{row['materia']}_{row['curso_id']}_{row['titulo']}_{row['trimestre_id']}_{row['tipo_evaluacion_id']}"
        
        evaluaciones.append({
            "id": evaluacion_id,
            "materia": row["materia"],
            "curso_id": int(row["curso_id"]),
            "titulo": row["titulo"],
            "descripcion": row["descripcion"],
            "trimestre_id": row["trimestre_id"],
            "tipo_evaluacion_id": row["tipo_evaluacion_id"],
            "fecha_asignacion": row["fecha_asignacion"],
            "fecha_entrega": row["fecha_entrega"],
            "nota_maxima": float(row["nota_maxima"]),
            "nota_minima_aprobacion": float(row["nota_minima_aprobacion"]),
            "porcentaje_nota_final": float(row["porcentaje_nota_final"]),
        })

# Generar calificaciones
with open("calificaciones_2024.csv", "w", newline='', encoding="utf-8") as f:
    fieldnames = [
        "estudiante_codigo",
        "estudiante_nombre",
        "estudiante_apellido",
        "materia",
        "curso_id",
        "titulo_evaluacion",
        "tipo_evaluacion_id",
        "trimestre_id",
        "nota",
        "nota_final",
        "nota_maxima",
        "nota_minima_aprobacion",
        "porcentaje_nota_final",
        "fecha_calificacion",
        "entrega_tardia",
        "penalizacion_aplicada",
        "finalizada"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for evaluacion in evaluaciones:
        # Generar fecha de calificación basada en la fecha de entrega
        # Tomamos la fecha de entrega y añadimos 1-3 días para la calificación
        fecha_entrega = datetime.strptime(evaluacion["fecha_entrega"], "%Y-%m-%d")
        dias_adicionales = random.randint(1, 3)
        fecha_calificacion = fecha_entrega + timedelta(days=dias_adicionales)
        fecha_calificacion_str = fecha_calificacion.strftime("%Y-%m-%d %H:%M:%S")
        
        # Filtrar estudiantes del curso correspondiente a esta evaluación
        estudiantes_curso = [est for est in estudiantes if est["curso"] == evaluacion["curso_id"]]
        
        for estudiante in estudiantes_curso:
            # Generar nota aleatoria con mayor probabilidad de notas altas
            # Distribución que favorece notas aprobatorias pero realistas
            base_nota = random.choice([
                random.uniform(51, evaluacion["nota_maxima"]),  # Aprobado (70%)
                random.uniform(0, 50)                           # Reprobado (30%)
            ] if random.random() < 0.7 else [random.uniform(0, 50)])
            
            nota = round(base_nota, 2)
            
            # Simular entrega tardía aleatoria para algunos casos (5%)
            entrega_tardia = random.random() < 0.05
            penalizacion = 0.0
            
            if entrega_tardia:
                penalizacion = random.choice([5, 10, 15])  # % de penalización
            
            # Aplicar penalización si corresponde
            nota_final = round(max(0, nota - (nota * penalizacion / 100)), 2)
            
            writer.writerow({
                "estudiante_codigo": estudiante["codigo"],
                "estudiante_nombre": estudiante["nombre"],
                "estudiante_apellido": estudiante["apellido"],
                "materia": evaluacion["materia"],
                "curso_id": evaluacion["curso_id"],
                "titulo_evaluacion": evaluacion["titulo"],
                "tipo_evaluacion_id": evaluacion["tipo_evaluacion_id"],
                "trimestre_id": evaluacion["trimestre_id"],
                "nota": nota,
                "nota_final": nota_final,
                "nota_maxima": evaluacion["nota_maxima"],
                "nota_minima_aprobacion": evaluacion["nota_minima_aprobacion"],
                "porcentaje_nota_final": evaluacion["porcentaje_nota_final"],
                "fecha_calificacion": fecha_calificacion_str,
                "entrega_tardia": entrega_tardia,
                "penalizacion_aplicada": penalizacion,
                "finalizada": True
            })

print("Archivo calificaciones_2024.csv generado correctamente con notas para cada estudiante y evaluación.")
print(f"Total de estudiantes procesados: {len(estudiantes)}")
print(f"Total de evaluaciones procesadas: {len(evaluaciones)}")
print(f"Total de registros generados: aproximadamente {len(estudiantes) * len(evaluaciones)} calificaciones")