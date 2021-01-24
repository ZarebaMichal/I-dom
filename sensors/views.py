from django.views.decorators import gzip
from djqscsv import render_to_csv_response
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from sensors import models
from sensors.models import Sensors, SensorsData
from sensors.serializer import SensorsSerializer, SensorsDataSerializer, SensorsReadOnlySerializer, \
    SensorsDataReadOnlySerializer
from rest_framework.permissions import IsAuthenticated
import requests
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta
from django.utils import timezone


@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_sensors(request, format=None):
    """
    Get list of all sensors, only for authenticated users
    :param request: GET
    :return: list of all sensors if ok http 200 response
    """
    sensors = Sensors.objects.filter(is_active=True)
   #serializer = SensorsSerializer(sensors, many=True)
    serializer = SensorsReadOnlySerializer(sensors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@gzip.gzip_page
@swagger_auto_schema(methods=["post"], request_body=SensorsSerializer())
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


@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_detail(request, pk, format=None):
    """
    Retrieve data of sensor
    :return: If sensor doesn't exist return 404,
            else if succeeded return 200
    """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SensorsSerializer(sensor)
    return Response(serializer.data)


@gzip.gzip_page
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
    time = str(datetime.now())
    time = time.replace(" ", "")
    sensor.name = time
    sensor.notifications = False
    sensor.ip_address = None
    sensor.is_active = False
    sensor.save()
    return Response(status=status.HTTP_200_OK)


@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_sensors_data(request, format=None):
    """
    Get list of all sensors data, only for authenticated users
    :param request: GET
    :return: list of all sensors if ok http 200 response
    """
    sensors_data = SensorsData.objects.select_related('sensor')
    #serializer = SensorsDataSerializer(sensors_data, many=True)
    serializer = SensorsDataReadOnlySerializer(sensors_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_sensors_data_from_one_sensor(request, pk, format=None):
    """
    Get list of all sensors data, only for authenticated users
    :param request: GET
    :return: list of all sensors if ok http 200 response
    """
    sensors_data = SensorsData.objects.filter(sensor=pk)
    serializer = SensorsDataSerializer(sensors_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=["post"], request_body=SensorsDataSerializer())
@api_view(['POST'])
def add_sensor_data(request):
    """
    Endpoint for adding sensor data for sensor requests
    :param request:
    :return:
    """
    serializer = SensorsDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        if 'sensor' in serializer.errors:
            return Response({'detail': 'Sensor does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@gzip.gzip_page
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_frequency_data(request, pk):
    """
    Endpoint for changing frequency in sensor
    :param request:
    :param pk:
    :return:
    """
    try:
        sensor = Sensors.objects.get(pk=pk)
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SensorsSerializer(sensor, data=request.data)

    if serializer.is_valid():
        serializer.save()
    else:
        if 'sensor' in serializer.errors:
            return Response({'detail': 'Sensors does not exists'}, status=status.HTTP_404_NOT_FOUND)
        elif 'frequency' in serializer.errors:
            return Response({'detail': 'Frequency must be between 1 and 21474836'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_data(request, pk):
    """
    Endpoint returning last data from chosen sensor
    :param request:
    :param pk:
    :return:
    """
    try:
        sensor_data = SensorsData.objects.filter(sensor_id=pk).latest('delivery_time')
    except SensorsData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(sensor_data.sensor_data, status=status.HTTP_200_OK)


@gzip.gzip_page
@api_view(['POST'])
def add_sensor_ip_address(request):
    """
    Endpoint for adding ip address for given sensor name
    :param request:
    :param pk:
    :return:
    """
    try:
        sensor = Sensors.objects.get(name=request.data['name'])
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {
        'ip_address': request.data['ip_address']
    }

    serializer = SensorsSerializer(sensor, data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def csv_view(request):
    qs = SensorsData.objects.all()
    return render_to_csv_response(qs, filename='test.csv')


@gzip.gzip_page
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def data_to_csv(request):
    """
    Endpoint for returning csv file with chosen sensor, time and category.
    There are different DB columns returned, depends on provided data
    :param request: {
                        "sensors_ids": list with id of sensor (null if empty),
                        "categories": list of sensor categories (null if empty),
                        "days": data in provided days (always required, max 30)
                    }
    :return: CSV file "sensors_data" and Http response code 200
    """

    params = ['sensors_ids', 'categories', 'days']

    # Validation
    for par in params:
        if par not in request.data:
            return Response(f'You have to provide {par}', status=status.HTTP_400_BAD_REQUEST)

    if int(request.data['days']) not in range(0, 31):
        return Response('Choose between 1-30 days', status=status.HTTP_400_BAD_REQUEST)

    # User provides only sensor categories
    if request.data['categories'] is not None:
        sensors_data = (models.SensorsData
                        .objects
                        .select_related('sensor')
                        .filter(sensor__category__in=request.data['categories'],
                                delivery_time__gte=datetime.now(tz=timezone.utc) - timedelta(
                                    days=int(request.data['days'])))
                        .values('delivery_time', 'sensor_data').
                        annotate(sensor_name=F('sensor__name')))
        return render_to_csv_response(sensors_data, filename='sensor_data.csv',  streaming=True)

    # User provides only 1 sensor with time
    elif request.data['sensors_ids'] is not None and len(request.data['sensors_ids']) == 1:
        sensors_data = (models.SensorsData
                        .objects.select_related('sensor')
                        .filter(sensor__id=request.data['sensors_ids'][0],
                                delivery_time__gte=datetime.now(tz=timezone.utc) - timedelta(
                                    days=int(request.data['days'])))
                        .values('delivery_time', 'sensor_data'))
        return render_to_csv_response(sensors_data, filename='sensor_data.csv',  streaming=True)


    # User provides more than 1 sensor with time
    elif request.data['sensors_ids'] is not None and len(request.data['sensors_ids']) > 1:
        sensors_data = (models.SensorsData
                        .objects.
                        select_related('sensor')
                        .filter(sensor__id__in=request.data['sensors_ids'],
                                delivery_time__gte=datetime.now(tz=timezone.utc) - timedelta(
                                    days=int(request.data['days'])))
                        .values('delivery_time', 'sensor_data').
                        annotate(sensor_name=F('sensor__name')))
        return render_to_csv_response(sensors_data, filename='sensor_data.csv',  streaming=True)

    # User request all sensor with all categories in given time
    elif request.data['sensors_ids'] is None and request.data['categories'] is None:
        sensors_data = (models.SensorsData
                        .objects
                        .select_related('sensor').
                        filter(
            delivery_time__gte=datetime.now(tz=timezone.utc) - timedelta(days=int(request.data['days'])))
                        .values('delivery_time', 'sensor_data').
                        annotate(sensor_name=F('sensor__name'), sensor_category=F('sensor__category')))
        return render_to_csv_response(sensors_data, filename='sensor_data.csv', streaming=True)


@gzip.gzip_page
@api_view(['POST'])
def update_battery_sensor(request, format=None):
    """
    Update battery level of sensor
    :param request: PUT
    :param pk: id of sensor
    :return: If sensor doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        sensor = Sensors.objects.get(name=request.data['name'])
    except Sensors.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = {
        "battery_level": request.data['battery_level']
        }

    serializer = SensorsSerializer(sensor, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
