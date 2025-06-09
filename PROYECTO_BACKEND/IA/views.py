from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .predictor import predecir_nota_estado  # Usar importación relativa con punto (.)

@api_view(['POST'])
def predecir_view(request):
    try:
        data = request.data
        
        # Extraer los datos del request
        par1 = float(data.get('parcial1', 0))
        par2 = float(data.get('parcial2', 0))
        par3 = float(data.get('parcial3', 0))
        
        prac1 = float(data.get('practico1', 0))
        prac2 = float(data.get('practico2', 0))
        prac3 = float(data.get('practico3', 0))
        prac4 = float(data.get('practico4', 0))
        prac5 = float(data.get('practico5', 0))
        prac6 = float(data.get('practico6', 0))
        
        part1 = float(data.get('participacion1', 0))
        part2 = float(data.get('participacion2', 0))
        part3 = float(data.get('participacion3', 0))
        part4 = float(data.get('participacion4', 0))
        
        asist = float(data.get('asistencias', 0))
        
        # Llamar a la función de predicción
        nota_predicha, estado = predecir_nota_estado(
            par1, par2, par3,
            prac1, prac2, prac3, prac4, prac5, prac6,
            part1, part2, part3, part4,
            asist
        )
        
        return Response({
            'nota_predicha': nota_predicha,
            'estado': estado,
            'exito': True
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'exito': False
        }, status=400)


