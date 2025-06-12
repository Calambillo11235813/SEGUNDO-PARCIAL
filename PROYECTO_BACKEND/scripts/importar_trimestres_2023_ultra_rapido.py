import os
import django
import sys
import csv
import time
from datetime import datetime
from django.db import transaction
import chardet

# Configuración Django
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Cursos.models import Materia, Trimestre, Asistencia
from Usuarios.models import Usuario

def detectar_codificacion(archivo):
    """Detecta la codificación del archivo CSV"""
    try:
        with open(archivo, 'rb') as f:
            resultado = chardet.detect(f.read())
            return resultado['encoding']
    except Exception as e:
        print(f"⚠️  Error detectando codificación: {e}")
        return 'utf-8'

def importar_trimestres_2023_ultra_rapido():
    """Importa todos los trimestres 2023 en modo ultra-rápido con manejo de codificación"""
    
    trimestres_config = [
        {'archivo': 'primer_trimestre_2023.csv', 'trimestre_id': 7, 'nombre': '1er Trimestre 2023'},
        {'archivo': 'segundo_trimestre_2023.csv', 'trimestre_id': 8, 'nombre': '2do Trimestre 2023'},
        {'archivo': 'tercer_trimestre_2023.csv', 'trimestre_id': 9, 'nombre': '3er Trimestre 2023'},
    ]
    
    inicio_total = time.time()
    print("🚀 IMPORTACIÓN ULTRA-RÁPIDA - TODOS LOS TRIMESTRES 2023")
    print("🔤 Con manejo automático de codificación")
    print("=" * 60)
    
    # Pre-cargar datos UNA VEZ para todos los trimestres
    print("📊 Pre-cargando datos globales...")
    estudiantes_dict = {str(u.codigo): u for u in Usuario.objects.filter(rol__nombre='Estudiante')}
    materias_dict = {f"{m.nombre}_{m.curso_id}": m for m in Materia.objects.all()}
    trimestres_dict = {t.id: t for t in Trimestre.objects.filter(id__in=[7, 8, 9])}
    
    print(f"✅ {len(estudiantes_dict)} estudiantes | {len(materias_dict)} materias | {len(trimestres_dict)} trimestres")
    print()
    
    resumen_total = {'total': 0, 'creados': 0, 'errores': 0}
    
    for config in trimestres_config:
        csv_path = os.path.join(project_root, 'csv', config['archivo'])
        
        if not os.path.isfile(csv_path):
            print(f"⚠️  {config['nombre']}: Archivo no encontrado")
            continue
        
        # Detectar codificación automáticamente
        codificacion = detectar_codificacion(csv_path)
        print(f"🔤 {config['nombre']}: Codificación detectada = {codificacion}")
        
        inicio_trimestre = time.time()
        print(f"⚡ Procesando {config['nombre']}...")
        
        total = 0
        creados = 0
        errores = 0
        trimestre = trimestres_dict.get(config['trimestre_id'])
        
        if not trimestre:
            print(f"❌ Trimestre ID {config['trimestre_id']} no encontrado en BD")
            continue
        
        asistencias_bulk = []
        
        try:
            # Usar codificación detectada
            with open(csv_path, mode='r', encoding=codificacion, errors='replace') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    total += 1
                    try:
                        # Limpiar datos
                        estudiante_codigo = str(row['estudiante_codigo']).strip()
                        materia_nombre = row['materia'].strip()
                        curso_id = str(row['curso_id']).strip()
                        
                        estudiante = estudiantes_dict.get(estudiante_codigo)
                        materia = materias_dict.get(f"{materia_nombre}_{curso_id}")
                        
                        if estudiante and materia:
                            asistencias_bulk.append(Asistencia(
                                estudiante=estudiante,
                                materia=materia,
                                trimestre=trimestre,
                                fecha=datetime.strptime(row['fecha'].strip(), '%Y-%m-%d').date(),
                                presente=row['presente'].strip().lower() == 'true',
                                justificada=row['justificada'].strip().lower() == 'true'
                            ))
                            creados += 1
                            
                            # Insertar en lotes grandes para máxima velocidad
                            if len(asistencias_bulk) >= 3000:
                                with transaction.atomic():
                                    Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
                                asistencias_bulk = []
                        else:
                            errores += 1
                            
                    except Exception as e:
                        errores += 1
                        if errores <= 5:  # Solo mostrar primeros errores
                            print(f"   ⚠️  Error fila {total}: {str(e)[:50]}...")
            
            # Insertar registros restantes
            if asistencias_bulk:
                with transaction.atomic():
                    Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
            
        except UnicodeDecodeError as e:
            print(f"❌ Error de codificación en {config['archivo']}: {e}")
            print("💡 Intentando con codificación alternativa...")
            
            # Intentar con codificaciones alternativas
            codificaciones_alternativas = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
            
            for alt_encoding in codificaciones_alternativas:
                try:
                    print(f"   🔄 Probando codificación: {alt_encoding}")
                    
                    with open(csv_path, mode='r', encoding=alt_encoding, errors='replace') as file:
                        csv_reader = csv.DictReader(file)
                        
                        # Procesar con codificación alternativa
                        for row in csv_reader:
                            total += 1
                            try:
                                estudiante_codigo = str(row['estudiante_codigo']).strip()
                                materia_nombre = row['materia'].strip()
                                curso_id = str(row['curso_id']).strip()
                                
                                estudiante = estudiantes_dict.get(estudiante_codigo)
                                materia = materias_dict.get(f"{materia_nombre}_{curso_id}")
                                
                                if estudiante and materia:
                                    asistencias_bulk.append(Asistencia(
                                        estudiante=estudiante,
                                        materia=materia,
                                        trimestre=trimestre,
                                        fecha=datetime.strptime(row['fecha'].strip(), '%Y-%m-%d').date(),
                                        presente=row['presente'].strip().lower() == 'true',
                                        justificada=row['justificada'].strip().lower() == 'true'
                                    ))
                                    creados += 1
                                    
                                    if len(asistencias_bulk) >= 3000:
                                        with transaction.atomic():
                                            Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
                                        asistencias_bulk = []
                                        
                            except Exception:
                                errores += 1
                    
                    # Si llegamos aquí, la codificación funcionó
                    if asistencias_bulk:
                        with transaction.atomic():
                            Asistencia.objects.bulk_create(asistencias_bulk, ignore_conflicts=True)
                    
                    print(f"   ✅ Codificación {alt_encoding} funcionó correctamente")
                    break
                    
                except UnicodeDecodeError:
                    continue
                    
        except Exception as e:
            print(f"❌ Error general en {config['archivo']}: {e}")
        
        tiempo_trimestre = time.time() - inicio_trimestre
        velocidad = creados / tiempo_trimestre if tiempo_trimestre > 0 else 0
        
        print(f"   ✅ {creados:,}/{total:,} registros | {errores:,} errores | {tiempo_trimestre:.1f}s | {velocidad:.0f} reg/seg")
        
        # Acumular totales
        resumen_total['total'] += total
        resumen_total['creados'] += creados
        resumen_total['errores'] += errores
    
    tiempo_total = time.time() - inicio_total
    velocidad_total = resumen_total['creados'] / tiempo_total if tiempo_total > 0 else 0
    
    print()
    print("🎉 IMPORTACIÓN COMPLETA - TODOS LOS TRIMESTRES 2023")
    print("=" * 60)
    print(f"📊 Total registros procesados: {resumen_total['total']:,}")
    print(f"✅ Total asistencias creadas: {resumen_total['creados']:,}")
    print(f"❌ Total errores: {resumen_total['errores']:,}")
    print(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos")
    print(f"🚀 Velocidad promedio: {velocidad_total:.0f} registros/segundo")
    print(f"📈 Eficiencia: {(resumen_total['creados']/resumen_total['total'])*100:.1f}%")
    print()
    print(f"🎓 AÑO ACADÉMICO 2023 COMPLETO IMPORTADO")
    print("=" * 60)

def verificar_archivos_csv():
    """Verifica y muestra información de los archivos CSV"""
    archivos = [
        'primer_trimestre_2023.csv',
        'segundo_trimestre_2023.csv', 
        'tercer_trimestre_2023.csv'
    ]
    
    print("🔍 VERIFICACIÓN DE ARCHIVOS CSV")
    print("=" * 40)
    
    for archivo in archivos:
        csv_path = os.path.join(project_root, 'csv', archivo)
        if os.path.isfile(csv_path):
            codificacion = detectar_codificacion(csv_path)
            tamaño = os.path.getsize(csv_path)
            
            # Contar líneas
            try:
                with open(csv_path, 'r', encoding=codificacion, errors='replace') as f:
                    lineas = sum(1 for _ in f) - 1  # -1 por header
            except:
                lineas = "Error"
            
            print(f"✅ {archivo}")
            print(f"   📁 Tamaño: {tamaño:,} bytes")
            print(f"   🔤 Codificación: {codificacion}")
            print(f"   📊 Registros: {lineas:,}")
        else:
            print(f"❌ {archivo}: No encontrado")
        print()

if __name__ == '__main__':
    print("🎓 IMPORTADOR ULTRA-RÁPIDO - TRIMESTRES 2023")
    print("🔤 Con detección automática de codificación")
    print()
    
    # Verificar archivos
    verificar_archivos_csv()
    
    respuesta = input("¿Continuar con la importación? (s/n): ").lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        print()
        importar_trimestres_2023_ultra_rapido()
    else:
        print("❌ Importación cancelada")