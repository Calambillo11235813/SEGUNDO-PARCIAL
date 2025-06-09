import csv
import random
import os

# Listas de nombres y apellidos
nombres = [
    "Juan", "Maria", "Carlos", "Patricia", "Luis", "Sandra", "Oscar", "Elena", "David", "Carla",
    "Fernando", "Paola", "Ricardo", "Erika", "Victor", "Yesica", "Freddy", "Julio", "Veronica", "Raul",
    "Lizeth", "Edgar", "Natalia", "Alvaro", "Silvia", "Roberto", "Rebeca", "Marcelo", "Claudia", "Guido",
    "Carolina", "Walter", "Patty", "Angel", "Paula", "Gustavo", "Milton", "Wilma", "Eduardo", "Romina",
    "Ernesto", "Lilian", "Mauricio", "Valeria", "Diego", "Lourdes", "Daniel", "Karen", "Jose", "Javier"
]
apellidos = [
    "Quispe", "Mamani", "Flores", "Choque", "Condori", "Cespedes", "Lopez", "Huanca", "Auza", "Calle",
    "Castro", "Llanque", "Camacho", "Bautista", "Aliaga", "Rojas", "Solis", "Aramayo", "Limachi", "Cardozo",
    "Navarro", "Franco", "Garcia", "Medina", "Arnez", "Marquez", "Torrez", "Vargas", "Alvarez", "Saavedra",
    "Rivera", "Loayza", "Salazar", "Escobar", "Miranda", "Aguilar", "Peñaranda", "Ayala", "Chambi", "Cordero",
    "Paz", "Vega", "Delgado", "Gutierrez", "Quisbert", "Arce", "Marquez", "Choque", "Castillo", "Ortega"
]

def random_telefono():
    # Números de Bolivia empiezan con 6 o 7 y tienen 8 dígitos
    return f"{random.choice([6,7])}{random.randint(1000000, 9999999)}"

# Función para leer los cursos desde el archivo CSV
def leer_cursos_csv(archivo):
    cursos = []
    with open(archivo, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursos.append(int(row['id']))
    return cursos

# Ruta al archivo de cursos
cursos_csv = os.path.join(os.path.dirname(__file__), 'cursos.csv')

# Leer los cursos
cursos = leer_cursos_csv(cursos_csv)

# Generar estudiantes
with open("estudiantes.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["codigo","nombre","apellido","telefono","password","rol_id","curso"])
    
    codigo = 2000  # Código inicial
    
    for curso_id in cursos:
        # Información del curso para el mensaje de salida
        with open(cursos_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['id']) == curso_id:
                    grado = row['grado']
                    paralelo = row['paralelo']
                    nivel = row['nivel']
                    break
        
        print(f"Generando estudiantes para el curso ID {curso_id} (Grado {grado}° {paralelo} - Nivel {nivel})")
        
        # Generar 40 estudiantes para este curso
        for i in range(40):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            telefono = random_telefono()
            password = f"{nombre.lower()}{codigo}"  # Ejemplo: juan2000
            
            writer.writerow([codigo, nombre, apellido, telefono, password, 2, curso_id])
            codigo += 1

total_estudiantes = len(cursos) * 40
print(f"\nArchivo estudiantes.csv generado con {total_estudiantes} estudiantes ({len(cursos)} cursos x 40 estudiantes)")
print("Formato de contraseñas: nombreCÓDIGO (ej: juan2000)")