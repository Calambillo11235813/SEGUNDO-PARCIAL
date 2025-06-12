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

# Leer participaciones 2023
participaciones = []
with open("participaciones_2023.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Crear un identificador único para cada participación
        participacion_id = f"{row['materia']}_{row['curso_id']}_{row['titulo']}_{row['trimestre_id']}_{row['tipo_evaluacion_id']}"
        
        participaciones.append({
            "id": participacion_id,
            "materia": row["materia"],
            "curso_id": int(row["curso_id"]),
            "titulo": row["titulo"],
            "descripcion": row["descripcion"],
            "trimestre_id": row["trimestre_id"],
            "tipo_evaluacion_id": row["tipo_evaluacion_id"],
            "fecha_registro": row["fecha_registro"],
            "porcentaje_nota_final": float(row["porcentaje_nota_final"]),
        })

# Generar calificaciones
with open("calificaciones_participaciones_2023.csv", "w", newline='', encoding="utf-8") as f:
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
        "porcentaje_nota_final",
        "fecha_calificacion",
        "finalizada"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for participacion in participaciones:
        # Generar fecha de calificación basada en la fecha de registro
        # Tomamos la fecha de registro y añadimos 1-3 días para la calificación
        fecha_registro = datetime.strptime(participacion["fecha_registro"], "%Y-%m-%d")
        dias_adicionales = random.randint(1, 3)
        fecha_calificacion = fecha_registro + timedelta(days=dias_adicionales)
        fecha_calificacion_str = fecha_calificacion.strftime("%Y-%m-%d %H:%M:%S")
        
        # Filtrar estudiantes del curso correspondiente a esta participación
        estudiantes_curso = [est for est in estudiantes if est["curso"] == participacion["curso_id"]]
        
        for estudiante in estudiantes_curso:
            # Distribución que favorece notas aprobatorias pero realistas
            base_nota = random.choice([
                random.uniform(60, 100),  # Nota alta (70%)
                random.uniform(40, 59)    # Nota media (20%)
            ] if random.random() < 0.9 else [random.uniform(0, 39)])  # Nota baja (10%)
            
            nota = round(base_nota, 2)
            nota_final = nota  # No hay penalización en participaciones
            
            writer.writerow({
                "estudiante_codigo": estudiante["codigo"],
                "estudiante_nombre": estudiante["nombre"],
                "estudiante_apellido": estudiante["apellido"],
                "materia": participacion["materia"],
                "curso_id": participacion["curso_id"],
                "titulo_evaluacion": participacion["titulo"],
                "tipo_evaluacion_id": participacion["tipo_evaluacion_id"],
                "trimestre_id": participacion["trimestre_id"],
                "nota": nota,
                "nota_final": nota_final,
                "porcentaje_nota_final": participacion["porcentaje_nota_final"],
                "fecha_calificacion": fecha_calificacion_str,
                "finalizada": True
            })

print("Archivo calificaciones_participaciones_2023.csv generado correctamente con notas para cada estudiante y participación.")
print(f"Total de estudiantes procesados: {len(estudiantes)}")
print(f"Total de participaciones 2023 procesadas: {len(participaciones)}")
print(f"Total de registros generados: aproximadamente {len(estudiantes) * len(participaciones)} calificaciones")