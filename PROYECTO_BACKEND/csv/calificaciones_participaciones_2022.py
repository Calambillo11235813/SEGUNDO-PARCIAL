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

# Leer participaciones
participaciones = []
with open("participaciones_2022.csv", newline='', encoding="utf-8") as f:
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
            "criterios_participacion": row["criterios_participacion"],
            "escala_calificacion": row["escala_calificacion"],
            "porcentaje_nota_final": float(row["porcentaje_nota_final"]),
        })

# Generar calificaciones
with open("calificaciones_participaciones_2022.csv", "w", newline='', encoding="utf-8") as f:
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
        "escala_calificacion",
        "criterios_participacion",
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
            # Determinar la nota según la escala de calificación
            if participacion["escala_calificacion"] == "NUMERICA":
                # Generar nota aleatoria con mayor probabilidad de notas altas
                # Distribución que favorece notas aprobatorias pero realistas
                base_nota = random.choice([
                    random.uniform(60, 100),  # Nota alta (70%)
                    random.uniform(40, 59)    # Nota media (20%)
                ] if random.random() < 0.9 else [random.uniform(0, 39)])  # Nota baja (10%)
                
                nota = round(base_nota, 2)
                nota_final = nota  # No hay penalización en participaciones
            
            else:  # CUALITATIVA
                # Generar calificación cualitativa
                calif_cualitativa = random.choices(
                    ["MB", "B", "R", "M"],  # Muy Bueno, Bueno, Regular, Malo
                    weights=[60, 25, 10, 5],  # Probabilidades (más peso a mejores calificaciones)
                    k=1
                )[0]
                
                # Convertir calificación cualitativa a numérica para almacenamiento
                if calif_cualitativa == "MB":
                    nota = round(random.uniform(90, 100), 2)
                elif calif_cualitativa == "B":
                    nota = round(random.uniform(75, 89), 2)
                elif calif_cualitativa == "R":
                    nota = round(random.uniform(51, 74), 2)
                else:  # "M"
                    nota = round(random.uniform(0, 50), 2)
                
                nota_final = nota
            
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
                "escala_calificacion": participacion["escala_calificacion"],
                "criterios_participacion": participacion["criterios_participacion"],
                "porcentaje_nota_final": participacion["porcentaje_nota_final"],
                "fecha_calificacion": fecha_calificacion_str,
                "finalizada": True
            })

print("Archivo calificaciones_participaciones_2022.csv generado correctamente con notas para cada estudiante y participación.")
print(f"Total de estudiantes procesados: {len(estudiantes)}")
print(f"Total de participaciones procesadas: {len(participaciones)}")
print(f"Total de registros generados: aproximadamente {len(estudiantes) * len(participaciones)} calificaciones")