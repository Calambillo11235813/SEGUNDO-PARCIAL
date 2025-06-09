import os
import django
import sys
import csv
from django.db import transaction

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Usuarios.models import Usuario
from Permisos.models import Rol

def importar_profesores_csv():
    """
    Importa profesores desde el archivo CSV a la base de datos.
    
    Formato esperado del CSV:
    codigo,nombre,apellido,telefono,password,rol_id
    """
    
    csv_path = 'D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND/csv/profesores.csv'
    
    try:
        # Verificar que el archivo existe
        if not os.path.isfile(csv_path):
            print(f"Error: El archivo {csv_path} no existe.")
            return
        
        # Verificar que existe el rol de profesor (rol_id=3)
        try:
            rol_profesor = Rol.objects.get(id=3)
        except Rol.DoesNotExist:
            print("Error: No existe el rol de profesor (id=3). Creándolo...")
            rol_profesor = Rol.objects.create(id=3, nombre="Profesor")
            print(f"✓ Rol de profesor creado: {rol_profesor.nombre}")
        
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Contador para estadísticas
            total = 0
            creados = 0
            actualizados = 0
            errores = 0
            
            # Usar transacción para asegurar que todos los datos se guarden correctamente
            with transaction.atomic():
                for row in csv_reader:
                    total += 1
                    try:
                        # Buscar o crear el usuario
                        usuario, created = Usuario.objects.get_or_create(
                            codigo=row['codigo'],
                            defaults={
                                'nombre': row['nombre'],
                                'apellido': row['apellido'],
                                'telefono': row['telefono'],
                                'rol_id': int(row['rol_id']),
                                'is_active': True,
                                'is_staff': False
                            }
                        )
                        
                        # Si el usuario ya existía, actualizar sus datos
                        if not created:
                            usuario.nombre = row['nombre']
                            usuario.apellido = row['apellido']
                            usuario.telefono = row['telefono']
                            usuario.rol_id = int(row['rol_id'])
                        
                        # Establecer contraseña
                        if row['password']:
                            usuario.set_password(row['password'])
                        
                        # Guardar cambios
                        usuario.save()
                        
                        if created:
                            creados += 1
                            print(f"✓ Creado profesor {row['codigo']}: {row['nombre']} {row['apellido']}")
                        else:
                            actualizados += 1
                            print(f"↻ Actualizado profesor {row['codigo']}: {row['nombre']} {row['apellido']}")
                            
                    except Exception as e:
                        errores += 1
                        print(f"✗ Error al procesar la fila {total}: {str(e)}")
                        print(f"  Datos: {row}")
            
            # Mostrar estadísticas finales
            print("\n===== RESUMEN DE IMPORTACIÓN DE PROFESORES =====")
            print(f"Total de registros procesados: {total}")
            print(f"Profesores creados: {creados}")
            print(f"Profesores actualizados: {actualizados}")
            print(f"Errores: {errores}")
            print("===============================================")
    
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    importar_profesores_csv()