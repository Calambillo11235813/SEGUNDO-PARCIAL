from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Rol
from ..serializers import RolSerializer

@api_view(['GET'])
def get_roles(request):
    """
    Obtiene todos los roles.
    """
    try:
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_rol(request, id):
    """
    Obtiene un rol específico por su ID.
    """
    try:
        rol = Rol.objects.get(pk=id)
        serializer = RolSerializer(rol)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Rol.DoesNotExist:
        return Response({'error': 'El rol no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_rol(request):
    """
    Crea un nuevo rol.
    """
    try:
        serializer = RolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_rol(request, id):
    """
    Actualiza un rol existente.
    """
    try:
        rol = Rol.objects.get(pk=id)
        serializer = RolSerializer(rol, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Rol.DoesNotExist:
        return Response({'error': 'El rol no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_rol(request, id):
    """
    Elimina un rol existente.
    """
    try:
        rol = Rol.objects.get(pk=id)
        rol.delete()
        return Response({'message': 'Rol eliminado con éxito'}, status=status.HTTP_200_OK)
    except Rol.DoesNotExist:
        return Response({'error': 'El rol no existe'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)