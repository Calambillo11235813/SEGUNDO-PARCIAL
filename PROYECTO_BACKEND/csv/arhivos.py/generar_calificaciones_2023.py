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

def generar_retroalimentacion(nota, tipo_evaluacion_id, materia):
    """Genera retroalimentación realista basada en la nota y tipo de evaluación"""
    retroalimentaciones = {
        'excelente': [
            f"Excelente dominio de {materia}. Trabajo sobresaliente que refleja dedicación.",
            f"Rendimiento excepcional en {materia}. Continúa con esa calidad de trabajo.",
            f"Muy buen manejo de los conceptos de {materia}. Resultado destacado.",
            f"Calidad superior en {materia}. Eres un ejemplo para tus compañeros."
        ],
        'bueno': [
            f"Buen nivel en {materia}. Con algunos ajustes menores alcanzarás la excelencia.",
            f"Desempeño sólido en {materia}. Sigue practicando para perfeccionar.",
            f"Trabajo bien estructurado en {materia}. Demuestra comprensión del tema.",
            f"Buen progreso en {materia}. Continúa con esa dedicación."
        ],
        'regular': [
            f"Nivel básico en {materia}. Es importante reforzar algunos conceptos clave.",
            f"Cumple con lo fundamental en {materia}, pero hay potencial para mejorar.",
            f"Trabajo aceptable en {materia}. Te sugiero dedicar más tiempo al estudio.",
            f"Comprensión básica de {materia}. Busca apoyo para fortalecer áreas débiles."
        ],
        'deficiente': [
            f"Necesitas apoyo adicional en {materia}. No dudes en pedir ayuda.",
            f"Resultado insuficiente en {materia}. Revisemos juntos los conceptos básicos.",
            f"Requiere mayor dedicación al estudio de {materia}. Estoy aquí para apoyarte.",
            f"Es importante que busques tutoría en {materia} para mejorar tu rendimiento."
        ]
    }
    
    if nota >= 85:
        categoria = 'excelente'
    elif nota >= 70:
        categoria = 'bueno'
    elif nota >= 51:
        categoria = 'regular'
    else:
        categoria = 'deficiente'
    
    # Agregar especificidad según tipo de evaluación
    prefijo = ""
    if tipo_evaluacion_id == '1':  # PARCIAL
        prefijo = "En este examen: "
    elif tipo_evaluacion_id == '2':  # PRÁCTICO
        prefijo = "En este trabajo práctico: "
    
    return prefijo + random.choice(retroalimentaciones[categoria])

def generar_observaciones(nota, entrega_tardia, penalizacion):
    """Genera observaciones basadas en el rendimiento"""
    observaciones = []
    
    if entrega_tardia:
        observaciones.append(f"Entrega tardía con penalización del {penalizacion}%")
    
    if nota >= 90:
        observaciones.append("Rendimiento sobresaliente - Felicitaciones")
    elif nota >= 80:
        observaciones.append("Muy buen rendimiento - Sigue así")
    elif nota >= 70:
        observaciones.append("Buen rendimiento - Con potencial de mejora")
    elif nota >= 51:
        observaciones.append("Rendimiento básico - Necesita refuerzo")
    else:
        observaciones.append("Rendimiento insuficiente - Requiere apoyo inmediato")
    
    return "; ".join(observaciones)

def main():
    print("🚀 Iniciando generación de calificaciones 2023 (versión simplificada)...")
    
    csv_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(csv_dir)  # Subir un nivel para acceder a csv/
    csv_path = os.path.join(parent_dir, "csv")
    
    # Leer estudiantes
    print("📚 Cargando datos de estudiantes...")
    estudiantes = []
    estudiantes_path = os.path.join(csv_path, "estudiantes.csv")
    
    if not os.path.exists(estudiantes_path):
        print(f"❌ Error: No se encontró el archivo {estudiantes_path}")
        return
    
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
    
    print(f"✅ Cargados {len(estudiantes)} estudiantes")
    
    # Leer evaluaciones
    print("📝 Cargando datos de evaluaciones...")
    evaluaciones = []
    eval_path = os.path.join(csv_path, "evaluaciones_practicos_2023.csv")
    
    if not os.path.exists(eval_path):
        print(f"❌ Error: No se encontró el archivo {eval_path}")
        return
    
    with open(eval_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            evaluaciones.append({
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
                "permite_entrega_tardia": row["permite_entrega_tardia"].upper() == "TRUE",
                "penalizacion_tardio": float(row["penalizacion_tardio"]) if row["penalizacion_tardio"] else 0.0
            })
    
    print(f"✅ Cargadas {len(evaluaciones)} evaluaciones")
    
    # Generar calificaciones
    output_path = os.path.join(csv_path, "calificaciones_2023.csv")
    print(f"⚙️ Generando calificaciones y guardando en {output_path}...")
    
    with open(output_path, "w", newline='', encoding="utf-8") as f:
        fieldnames = [
            # Campos principales simplificados
            "estudiante_codigo",
            "nota",
            "fecha_entrega",
            "entrega_tardia",
            "penalizacion_aplicada",
            "observaciones",
            "retroalimentacion",
            "finalizada",
            "calificado_por_codigo",
            "fecha_calificacion",
            # Campos de contexto para identificar la evaluación
            "estudiante_nombre",
            "estudiante_apellido",
            "materia",
            "curso_id",
            "titulo_evaluacion",
            "descripcion_evaluacion",
            "tipo_evaluacion_id",
            "trimestre_id",
            "nota_maxima",
            "nota_minima_aprobacion",
            "porcentaje_nota_final",
            "fecha_asignacion",
            "fecha_entrega_limite"
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
        entregas_tardias = 0
        total_evaluaciones_procesadas = len(evaluaciones)
        
        # Mostrar progreso
        total_combinaciones = len(estudiantes) * len(evaluaciones)
        print(f"🧮 Generando aproximadamente {total_combinaciones:,} calificaciones...")
        
        for i, evaluacion in enumerate(evaluaciones):
            # Reportar progreso cada 10%
            if i % max(1, total_evaluaciones_procesadas // 10) == 0:
                porcentaje = (i / total_evaluaciones_procesadas) * 100
                print(f"⏳ Progreso: {porcentaje:.1f}% - Procesando evaluación {i+1} de {total_evaluaciones_procesadas}")
            
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
                
                # Verificar si la evaluación permite entrega tardía
                if entrega_tardia and not evaluacion["permite_entrega_tardia"]:
                    entrega_tardia = False  # Forzar entrega a tiempo si no se permite tardía
                
                # Configurar penalización para entregas tardías
                penalizacion = 0.0
                if entrega_tardia and evaluacion["permite_entrega_tardia"]:
                    # Usar la penalización definida en la evaluación o una basada en perfil
                    if evaluacion["penalizacion_tardio"] > 0:
                        penalizacion = evaluacion["penalizacion_tardio"]
                    else:
                        # Penalización basada en perfil del estudiante
                        if estudiante["perfil"]["tipo"] == 'sobresaliente':
                            penalizacion = random.choice([3, 5])
                        elif estudiante["perfil"]["tipo"] == 'bueno':
                            penalizacion = random.choice([5, 8])
                        elif estudiante["perfil"]["tipo"] in ['medio-alto', 'medio-bajo']:
                            penalizacion = random.choice([8, 12, 15])
                        else:
                            penalizacion = random.choice([15, 20, 25])
                
                # Generar fecha y hora de entrega
                if entrega_tardia:
                    # Entrega 1-3 días después de la fecha límite
                    dias_retraso = random.randint(1, 3)
                    fecha_entrega_estudiante = fecha_entrega + timedelta(days=dias_retraso)
                    entregas_tardias += 1
                else:
                    # Entrega el mismo día o 1-2 días antes
                    dias_adelanto = random.randint(-2, 0)
                    fecha_entrega_estudiante = fecha_entrega + timedelta(days=dias_adelanto)
                
                # Agregar hora aleatoria
                hora = random.randint(8, 22)
                minuto = random.randint(0, 59)
                fecha_entrega_estudiante = fecha_entrega_estudiante.replace(hour=hora, minute=minuto)
                
                # Generar fecha de calificación (1-5 días después de entrega)
                dias_calificacion = random.randint(1, 5)
                fecha_calificacion = fecha_entrega_estudiante + timedelta(days=dias_calificacion)
                hora_calificacion = random.randint(9, 18)
                minuto_calificacion = random.randint(0, 59)
                fecha_calificacion = fecha_calificacion.replace(hour=hora_calificacion, minute=minuto_calificacion)
                
                # Generar código del profesor que califica (diferente para 2023)
                calificado_por_codigo = f"PROF{random.randint(1021, 1040)}"
                
                # Generar retroalimentación y observaciones
                retroalimentacion = generar_retroalimentacion(nota, evaluacion["tipo_evaluacion_id"], evaluacion["materia"])
                observaciones = generar_observaciones(nota, entrega_tardia, penalizacion)
                
                # Guardar registro
                writer.writerow({
                    # Campos principales
                    "estudiante_codigo": estudiante["codigo"],
                    "nota": nota,
                    "fecha_entrega": fecha_entrega_estudiante.strftime("%Y-%m-%d %H:%M:%S"),
                    "entrega_tardia": entrega_tardia,
                    "penalizacion_aplicada": penalizacion,
                    "observaciones": observaciones,
                    "retroalimentacion": retroalimentacion,
                    "finalizada": True,
                    "calificado_por_codigo": calificado_por_codigo,
                    "fecha_calificacion": fecha_calificacion.strftime("%Y-%m-%d %H:%M:%S"),
                    # Campos de contexto
                    "estudiante_nombre": estudiante["nombre"],
                    "estudiante_apellido": estudiante["apellido"],
                    "materia": evaluacion["materia"],
                    "curso_id": evaluacion["curso_id"],
                    "titulo_evaluacion": evaluacion["titulo"],
                    "descripcion_evaluacion": evaluacion["descripcion"],
                    "tipo_evaluacion_id": evaluacion["tipo_evaluacion_id"],
                    "trimestre_id": evaluacion["trimestre_id"],
                    "nota_maxima": evaluacion["nota_maxima"],
                    "nota_minima_aprobacion": evaluacion["nota_minima_aprobacion"],
                    "porcentaje_nota_final": evaluacion["porcentaje_nota_final"],
                    "fecha_asignacion": evaluacion["fecha_asignacion"],
                    "fecha_entrega_limite": evaluacion["fecha_entrega"]
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
    porcentaje_tardias = (entregas_tardias / total_registros) * 100 if total_registros > 0 else 0
    
    print("\n✅ Generación completada!")
    print(f"📊 ESTADÍSTICAS FINALES 2023:")
    print(f"  • Total de calificaciones generadas: {total_registros:,}")
    print(f"  • Total de evaluaciones procesadas: {len(evaluaciones)}")
    print(f"  • Calificaciones aprobatorias (≥51): {notas_aprobatorias:,} ({porcentaje_aprobacion:.2f}%)")
    print(f"  • Promedio general: {promedio_general:.2f} puntos")
    print(f"  • Promedio de aprobados: {promedio_aprobados:.2f} puntos")
    print(f"  • Notas entre 80-90: {notas_80_90:,} ({porcentaje_80_90:.2f}%)")
    print(f"  • Notas entre 90-100: {notas_90_100:,} ({porcentaje_90_100:.2f}%)")
    print(f"  • Entregas tardías: {entregas_tardias:,} ({porcentaje_tardias:.2f}%)")
    print(f"📁 Archivo generado: {output_path}")

if __name__ == "__main__":
    main()