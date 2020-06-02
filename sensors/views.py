from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from sensors.models import Sensors
from sensors.serializer import SensorsSerializer, SensorsDataSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_sensors(request, format=None):
    """
    Get list of all sensors, only for authenticated users
    :param request: GET
    :return: list of all sensors if ok http 200 response
    """
    sensors = Sensors.objects.all()
    serializer = SensorsSerializer(sensors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_sensors(request, format=None):
    """
    Add new sensor, only for authenticated users
    :param request: POST: name, category of the sensor
    :returns: instance of created sensor and 201 HTTP response,
             if failed, 400 HTTP response, if sensor with given
             name already exists, 400 HTTP response and expected error
    """

    serializer = SensorsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_detail(request, pk, format=None):
    """
    Retrieve data of sensor
    :return: If sensor doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SensorsSerializer(sensor)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_sensor(request, pk, format=None):
    """
    Update data of sensor
    :param request: PUT
    :param pk: id of sensor
    :return: If sensor doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SensorsSerializer(sensor, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_sensor(request, pk, format=None):
    """
        Delete sensor
        :param request: DELETE
        :param pk: id of sensor
        :return: If sensor doesn't exist return 404,
                if given invalid data, return 400,
                else if succeeded return 200
        """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    sensor.is_active = False
    sensor.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def add_sensor_data(request):
    serializer = SensorsDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
