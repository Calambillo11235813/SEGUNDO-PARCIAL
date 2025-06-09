import os
import django
import sys
import csv
import time
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Usuarios.models import Usuario
from Permisos.models import Rol
from Cursos.models import Curso
from django.contrib.auth.hashers import make_password

def importar_estudiantes_csv():
    """
    Importa estudiantes desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    codigo,nombre,apellido,telefono,password,rol_id,curso
    """
    
    tiempo_inicio = time.time()
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/estudiantes.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        # Pre-cargar cursos en memoria para reducir consultas
        cursos_cache = {str(curso.id): curso for curso in Curso.objects.all()}
        
        # Obtener todos los códigos de usuario existentes para optimizar búsquedas
        codigos_existentes = set(Usuario.objects.values_list('codigo', flat=True))
        
        # Preparar listas para operaciones en lote
        usuarios_a_crear = []
        usuarios_a_actualizar = []
        
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Cargar todos los datos en memoria
            rows = list(csv_reader)
            
            # Contador para estadísticas
            total = len(rows)
            creados = 0
            actualizados = 0
            errores = 0
            
            # Procesar en lotes de 100 para balancear memoria y rendimiento
            BATCH_SIZE = 100
            
            # Usar transacción para asegurar que todos los datos se guarden correctamente
            with transaction.atomic():
                for i, row in enumerate(rows):
                    try:
                        codigo = row['codigo']
                        
                        # Preparar datos comunes
                        datos_usuario = {
                            'nombre': row['nombre'],
                            'apellido': row['apellido'],
                            'telefono': row['telefono'],
                            'rol_id': row['rol_id'],
                            'is_active': True,
                            'is_staff': False
                        }
                        
                        # Si existe curso, agregarlo a los datos
                        if row['curso'] and row['curso'] in cursos_cache:
                            datos_usuario['curso'] = cursos_cache[row['curso']]
                        
                        # Si se proporciona contraseña, hashearla
                        if row['password']:
                            datos_usuario['password'] = make_password(row['password'])
                        
                        # Determinar si crear o actualizar
                        if codigo in codigos_existentes:
                            # Actualizar usuario existente
                            usuario = Usuario.objects.get(codigo=codigo)
                            for key, value in datos_usuario.items():
                                setattr(usuario, key, value)
                            usuarios_a_actualizar.append(usuario)
                            actualizados += 1
                            print(f"[{time.time() - tiempo_inicio:.2f}s] ↻ Actualizado usuario {codigo}: {row['nombre']} {row['apellido']}")
                        else:
                            # Crear nuevo usuario
                            datos_usuario['codigo'] = codigo
                            usuario = Usuario(**datos_usuario)
                            usuarios_a_crear.append(usuario)
                            codigos_existentes.add(codigo)  # Actualizar caché
                            creados += 1
                            print(f"[{time.time() - tiempo_inicio:.2f}s] ✓ Creado usuario {codigo}: {row['nombre']} {row['apellido']}")
                        
                        # Procesar en lotes para optimizar
                        if len(usuarios_a_crear) >= BATCH_SIZE:
                            Usuario.objects.bulk_create(usuarios_a_crear)
                            usuarios_a_crear = []
                        
                        if len(usuarios_a_actualizar) >= BATCH_SIZE:
                            Usuario.objects.bulk_update(
                                usuarios_a_actualizar, 
                                ['nombre', 'apellido', 'telefono', 'rol_id', 'curso', 'password', 'is_active', 'is_staff']
                            )
                            usuarios_a_actualizar = []
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {i+1}: {str(e)}")
                        print(f"  Datos: {row}")
                
                # Procesar los lotes finales
                if usuarios_a_crear:
                    Usuario.objects.bulk_create(usuarios_a_crear)
                
                if usuarios_a_actualizar:
                    Usuario.objects.bulk_update(
                        usuarios_a_actualizar, 
                        ['nombre', 'apellido', 'telefono', 'rol_id', 'curso', 'password', 'is_active', 'is_staff']
                    )
            
            tiempo_total = time.time() - tiempo_inicio
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN =====")
            print(f"Total de registros procesados: {total}")
            print(f"Usuarios creados: {creados}")
            print(f"Usuarios actualizados: {actualizados}")
            print(f"Errores: {errores}")
            print(f"Tiempo total: {tiempo_total:.2f} segundos")
            print(f"Promedio: {(total / tiempo_total):.2f} registros/segundo")
            print("=================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_estudiantes_csv()