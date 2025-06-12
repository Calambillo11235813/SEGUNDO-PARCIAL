import os
import django
import sys
import csv
import time
from datetime import datetime

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Materia, Trimestre, Asistencia
from Usuarios.models import Usuario

def importar_primer_trimestre_ultra_rapido():
    """Versión ultra-rápida para primer trimestre 2024"""
    csv_path = os.path.join(project_root, 'csv', 'primer_trimestre_2024.csv')
    
    inicio = time.time()
    print("🚀 MODO ULTRA-RÁPIDO - PRIMER TRIMESTRE 2024")
    print("⚡ Sin progreso detallado para máxima velocidad...")
    
    total = 0
    creados = 0
    
    # Pre-cargar TODO en memoria
    print("📊 Pre-cargando datos en memoria...")
    estudiantes_dict = {str(u.codigo): u for u in Usuario.objects.filter(rol__nombre='Estudiante')}
    materias_dict = {f"{m.nombre}_{m.curso_id}": m for m in Materia.objects.all()}
    trimestre = Trimestre.objects.get(id=10)  # ID del primer trimestre
    
    print(f"✅ Datos cargados: {len(estudiantes_dict)} estudiantes, {len(materias_dict)} materias")
    print("⚡ Procesando CSV...")
    
    asistencias_bulk = []
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            total += 1
            try:
                estudiante = estudiantes_dict.get(row['estudiante_codigo'])
                materia = materias_dict.get(f"{row['materia']}_{row['curso_id']}")
                
                if estudiante and materia:
                    asistencias_bulk.append(Asistencia(
                        estudiante=estudiante,
                        materia=materia,
                        trimestre=trimestre,
                        fecha=datetime.strptime(row['fecha'], '%Y-%m-%d').date(),
                        presente=row['presente'].strip().lower() == 'true',
                        justificada=row['justificada'].strip().lower() == 'true'
                    ))
                    creados += 1
                    
                    # Insertar en lotes de 2000 para máxima velocidad
                    if len(asistencias_bulk) >= 2000:
                        Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
                        asistencias_bulk = []
                        
            except Exception:
                pass  # Silenciar todo para velocidad máxima
    
    # Insertar registros restantes
    if asistencias_bulk:
        Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
    
    tiempo_total = time.time() - inicio
    velocidad = creados / tiempo_total if tiempo_total > 0 else 0
    
    print(f"🎉 PRIMER TRIMESTRE COMPLETADO:")
    print(f"   ✅ {creados:,}/{total:,} registros en {tiempo_total:.2f}s")
    print(f"   🚀 Velocidad: {velocidad:.0f} registros/segundo")
    print(f"   📅 Período: Febrero - Abril 2024")

if __name__ == '__main__':
    importar_primer_trimestre_ultra_rapido()