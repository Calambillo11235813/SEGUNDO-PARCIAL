import os
import django
import sys

# Configurar entorno Django
sys.path.append('D:/1.CARRERA UNIVERSITARIA/8.NOVENO SEMESTRE/1.SISTEMAS DE INFORMACION 2/SEGUNDO PARCIAL/SEGUNDO-PARCIAL/PROYECTO_BACKEND')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Permisos.models import Rol

def importar_roles():
    """Crea los roles básicos del sistema si no existen"""
    roles = [
        {"id": 1, "nombre": "Administrador"},
        {"id": 2, "nombre": "Estudiante"},
        {"id": 3, "nombre": "Profesor"},
        {"id": 4, "nombre": "Tutor"}
    ]
    
    roles_creados = 0
    
    for rol_data in roles:
        rol, created = Rol.objects.get_or_create(
            id=rol_data["id"],
            defaults={
                "nombre": rol_data["nombre"]
            }
        )
        
        if created:
            roles_creados += 1
    
    print(f"Roles creados: {roles_creados}")
    print(f"Total roles en sistema: {Rol.objects.count()}")

if __name__ == "__main__":
    importar_roles()