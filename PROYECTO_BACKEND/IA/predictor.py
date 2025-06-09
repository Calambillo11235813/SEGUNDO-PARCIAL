import os
import pandas as pd  # Mover esta importación aquí arriba
import joblib

# Obtener la ruta absoluta del proyecto para cargar el modelo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'IA', 'modelo_regresion_notas.pkl')  # Ruta corregida

# Cargar el modelo una vez
modelo = joblib.load(model_path)

def predecir_nota_estado(par1, par2, par3,
                         prac1, prac2, prac3, prac4, prac5, prac6,
                         part1, part2, part3, part4,
                         asist):
    datos = {
        "Parcial1": [par1],
        "Parcial2": [par2],
        "Parcial3": [par3],
        "Practico1": [prac1],
        "Practico2": [prac2],
        "Practico3": [prac3],
        "Practico4": [prac4],
        "Practico5": [prac5],
        "Practico6": [prac6],
        "Participacion1": [part1],
        "Participacion2": [part2],
        "Participacion3": [part3],
        "Participacion4": [part4],
        "Asistencias": [asist]
    }
    df_in = pd.DataFrame(datos)
    nota_pred = modelo.predict(df_in)[0]
    estado = "Aprobado" if nota_pred >= 51 else "Reprobado"
    return round(nota_pred, 2), estado
