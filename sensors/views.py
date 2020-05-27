from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from sensors.models import Sensors
from sensors.serializer import SensorsSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def all_sensors(request, format=None):
    """
    Add new sensor or get list of all sensors, only for authenticated users
    :returns: When request method 'POST' instance of created sensor and 201 HTTP response,
             if failed, 400 HTTP response, if sensor with given
             name already exists, 409 HTTP response.
             Or list of sensors when request method 'GET'
    """
    if request.method == 'GET':
        sensors = Sensors.objects.all()
        serializer = SensorsSerializer(sensors, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        sensor_name = request.data['name']
        try:
            sensor = Sensors.objects.get(name=sensor_name)
        except ObjectDoesNotExist:
            serializer = SensorsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_409_CONFLICT)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def sensor_detail(request, pk, format=None):
    """
    Retrieve, update or delete sensor.
    :return: If sensor doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SensorsSerializer(sensor)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SensorsSerializer(sensor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sensor.is_active = False
        sensor.save()
        return Response(status=status.HTTP_200_OK)
