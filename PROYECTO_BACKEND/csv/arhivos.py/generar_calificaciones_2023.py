import csv
import random
import os
from datetime import datetime, timedelta

try:
    import numpy as np # type: ignore
except ImportError:
    import sys
    import subprocess
    print("🔧 Numpy no está instalado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np # type: ignore

def crear_perfil_estudiante():
    """Crea un perfil de rendimiento para un estudiante"""
    # Tipos de perfiles:
    # - Sobresaliente: notas muy altas (85-100)
    # - Bueno: notas altas (70-84)
    # - Medio-alto: notas medias-altas (60-69)
    # - Medio-bajo: notas medias-bajas (51-59)
    # - Bajo: notas bajas (30-50)
    # - Muy bajo: notas muy bajas (0-29)
    
    tipo_perfil = random.choices(
        ['sobresaliente', 'bueno', 'medio-alto', 'medio-bajo', 'bajo', 'muy bajo'], 
        weights=[0.15, 0.25, 0.3, 0.1, 0.15, 0.05],  # Aproximadamente 70% aprobados (>51)
        k=1
    )[0]
    
    if tipo_perfil == 'sobresaliente':
        base_media = random.uniform(85, 95)
        variabilidad = random.uniform(3, 7)
    elif tipo_perfil == 'bueno':
        base_media = random.uniform(70, 84)
        variabilidad = random.uniform(5, 10)
    elif tipo_perfil == 'medio-alto':
        base_media = random.uniform(60, 69)
        variabilidad = random.uniform(7, 12)
    elif tipo_perfil == 'medio-bajo':
        base_media = random.uniform(51, 59)
        variabilidad = random.uniform(8, 15)
    elif tipo_perfil == 'bajo':
        base_media = random.uniform(30, 50)
        variabilidad = random.uniform(10, 20)
    else:  # muy bajo
        base_media = random.uniform(10, 29)
        variabilidad = random.uniform(5, 15)
    
    # Agregar características aleatorias al perfil
    return {
        'tipo': tipo_perfil,
        'base_media': base_media,
        'variabilidad': variabilidad,
        'mejora_con_tiempo': random.uniform(0, 0.2),  # Mejora a lo largo del trimestre
        'rendimiento_por_materia': {},  # Se llenará dinámicamente
        'probabilidad_entrega_tarde': random.uniform(0.01, 0.3) if tipo_perfil not in ['sobresaliente', 'bueno'] else random.uniform(0, 0.05)
    }

def generar_nota_para_estudiante(estudiante_perfil, materia, trimestre_id, fecha_entrega_obj):
    """Genera una calificación basada en el perfil del estudiante"""
    
    # Si no tiene un rendimiento base para esta materia, crear uno
    if materia not in estudiante_perfil['rendimiento_por_materia']:
        # Mayor variación por materia para reflejar mejor el mundo real
        variacion_materia = random.uniform(-15, 15)
        estudiante_perfil['rendimiento_por_materia'][materia] = min(100, max(0, estudiante_perfil['base_media'] + variacion_materia))
    
    # Obtener base de nota para esta materia
    base_nota_materia = estudiante_perfil['rendimiento_por_materia'][materia]
    
    # Aplicar variabilidad individual a esta evaluación
    variabilidad = estudiante_perfil['variabilidad']
    
    # Aplicar factor de mejora según avanza el trimestre
    trimestre_num = int(trimestre_id)
    factor_tiempo = trimestre_num % 4  # 0-3 representa la posición dentro del año
    mejora = estudiante_perfil['mejora_con_tiempo'] * factor_tiempo * 10
    
    # Usar distribución normal truncada para generar nota más realista
    media = min(100, base_nota_materia + mejora)
    
    # Forzar algunas notas altas para estudiantes sobresalientes
    if estudiante_perfil['tipo'] == 'sobresaliente' and random.random() < 0.3:
        # 30% de probabilidad de obtener entre 90-100
        nota = random.uniform(90, 100)
    else:
        # Generación normal con distribución gaussiana
        nota = np.random.normal(media, variabilidad)
    
    # Garantizar algunas notas en el rango 80-90 para estudiantes buenos
    if estudiante_perfil['tipo'] == 'bueno' and random.random() < 0.25:
        nota = random.uniform(80, 90)
    
    # Truncar entre 0-100
    nota = max(0, min(100, nota))
    
    # Truncar a 2 decimales
    nota = round(nota, 2)
    
    # Determinar si es entrega tardía
    es_tardia = random.random() < estudiante_perfil['probabilidad_entrega_tarde']
    
    return nota, es_tardia

def main():
    print("🚀 Iniciando generación de calificaciones 2023 con distribución realista...")
    
    csv_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Leer estudiantes
    print("📚 Cargando datos de estudiantes...")
    estudiantes = []
    estudiantes_path = os.path.join(csv_dir, "estudiantes.csv")
    with open(estudiantes_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            estudiantes.append({
                "codigo": row["codigo"],
                "nombre": row["nombre"],
                "apellido": row["apellido"],
                "curso": int(row["curso"]),
                "perfil": crear_perfil_estudiante()  # Crear perfil único para cada estudiante
            })
    
    # Leer evaluaciones (solo entregables)
    print("📝 Cargando datos de evaluaciones...")
    evaluaciones = []
    eval_path = os.path.join(csv_dir, "evaluaciones_practicos_2023.csv")
    with open(eval_path, newline='', encoding="utf-8") as f:
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
    output_path = os.path.join(csv_dir, "calificaciones_2023.csv")
    print(f"⚙️ Generando calificaciones y guardando en {output_path}...")
    
    with open(output_path, "w", newline='', encoding="utf-8") as f:
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

        # Variables para estadísticas
        total_registros = 0
        suma_notas = 0
        notas_aprobatorias = 0
        suma_notas_aprobatorias = 0
        notas_80_90 = 0
        notas_90_100 = 0
        total_evaluciones_procesadas = len(evaluaciones)
        
        # Mostrar progreso
        total_combinaciones = len(estudiantes) * len(evaluaciones)
        print(f"🧮 Generando aproximadamente {total_combinaciones:,} calificaciones...")
        
        for i, evaluacion in enumerate(evaluaciones):
            # Reportar progreso cada 10%
            if i % max(1, total_evaluciones_procesadas // 10) == 0:
                porcentaje = (i / total_evaluciones_procesadas) * 100
                print(f"⏳ Progreso: {porcentaje:.1f}% - Procesando evaluación {i+1} de {total_evaluciones_procesadas}")
            
            # Convertir fecha de entrega a objeto datetime
            fecha_entrega = datetime.strptime(evaluacion["fecha_entrega"], "%Y-%m-%d")
            
            # Filtrar estudiantes del curso correspondiente a esta evaluación
            estudiantes_curso = [est for est in estudiantes if est["curso"] == evaluacion["curso_id"]]
            
            for estudiante in estudiantes_curso:
                # Generar nota basada en el perfil del estudiante
                nota, entrega_tardia = generar_nota_para_estudiante(
                    estudiante["perfil"], 
                    evaluacion["materia"],
                    evaluacion["trimestre_id"],
                    fecha_entrega
                )
                
                # Configurar penalización para entregas tardías
                penalizacion = 0.0
                if entrega_tardia:
                    # Penalización basada en perfil
                    if estudiante["perfil"]["tipo"] == 'sobresaliente':
                        penalizacion = random.choice([3, 5])
                    elif estudiante["perfil"]["tipo"] == 'bueno':
                        penalizacion = random.choice([5, 8])
                    elif estudiante["perfil"]["tipo"] in ['medio-alto', 'medio-bajo']:
                        penalizacion = random.choice([8, 12, 15])
                    else:
                        penalizacion = random.choice([15, 20, 25])
                
                # Aplicar penalización si corresponde
                nota_final = round(max(0, nota - (nota * penalizacion / 100)), 2)
                
                # Generar fecha de calificación (1-5 días después de entrega)
                dias_adicionales = random.randint(1, 5)
                fecha_calificacion = fecha_entrega + timedelta(days=dias_adicionales)
                fecha_calificacion_str = fecha_calificacion.strftime("%Y-%m-%d %H:%M:%S")
                
                # Guardar registro
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
                    "entrega_tardia": "SI" if entrega_tardia else "NO",
                    "penalizacion_aplicada": penalizacion,
                    "finalizada": "SI"
                })
                
                # Actualizar estadísticas
                suma_notas += nota
                total_registros += 1
                
                # Contar notas por rangos
                if nota >= evaluacion["nota_minima_aprobacion"]:
                    notas_aprobatorias += 1
                    suma_notas_aprobatorias += nota
                
                if 80 <= nota < 90:
                    notas_80_90 += 1
                elif nota >= 90:
                    notas_90_100 += 1
    
    # Calcular y mostrar estadísticas finales
    promedio_general = suma_notas / total_registros if total_registros > 0 else 0
    promedio_aprobados = suma_notas_aprobatorias / notas_aprobatorias if notas_aprobatorias > 0 else 0
    porcentaje_aprobacion = (notas_aprobatorias / total_registros) * 100 if total_registros > 0 else 0
    porcentaje_80_90 = (notas_80_90 / total_registros) * 100 if total_registros > 0 else 0
    porcentaje_90_100 = (notas_90_100 / total_registros) * 100 if total_registros > 0 else 0
    
    print("\n✅ Generación completada!")
    print(f"📊 ESTADÍSTICAS FINALES:")
    print(f"  • Total de calificaciones generadas: {total_registros:,}")
    print(f"  • Calificaciones aprobatorias (>51): {notas_aprobatorias:,} ({porcentaje_aprobacion:.2f}%)")
    print(f"  • Promedio general: {promedio_general:.2f} puntos")
    print(f"  • Promedio de aprobados: {promedio_aprobados:.2f} puntos")
    print(f"  • Notas entre 80-90: {notas_80_90:,} ({porcentaje_80_90:.2f}%)")
    print(f"  • Notas entre 90-100: {notas_90_100:,} ({porcentaje_90_100:.2f}%)")

if __name__ == "__main__":
    main()