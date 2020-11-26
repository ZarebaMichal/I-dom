from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from driver.models import Drivers
from driver.serializer import DriversSerializer
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
import requests
from urllib3 import exceptions


# <--------- LIST OF DRIVERS ---------> #


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_drivers(request):
    """
    Get list of all drivers, only for authenticated users
    :param request: GET
    :return: list of all drivers if ok http 200 response
    """
    driver = Drivers.objects.filter(is_active=True)
    serializer = DriversSerializer(driver, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_detail(request, pk):
    """
    Retrieve data of driver
    :return: If driver doesn't exist return 404,
            else if succeeded return 200
    """
    try:
        driver = Drivers.objects.get(pk=pk)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = DriversSerializer(driver)
    return Response(serializer.data)


# <--------- CREATE DRIVER ---------> #


@swagger_auto_schema(methods=["post"], request_body=DriversSerializer())
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_driver(request):
    """
    Add new driver, only for authenticated users
    :param request: POST: name, category of the driver
    :returns: instance of created driver and 201 HTTP response,
             if failed, 400 HTTP response, if driver with given
             name already exists, 400 HTTP response and expected error
    """

    serializer = DriversSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <--------- UPDATE DRIVER ---------> #


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_driver(request, pk):
    """
    Update data of driver
    :param request: PUT
    :param pk: id of driver
    :return: If driver doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        driver = Drivers.objects.get(pk=pk)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = DriversSerializer(driver, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <--------- DELETE DRIVER ---------> #


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_driver(request, pk):
    """
        Delete driver
        :param request: DELETE
        :param pk: id of driver
        :return: If driver doesn't exist return 404,
                if given invalid data, return 400,
                else if succeeded return 200
    """
    try:
        driver = Drivers.objects.get(pk=pk)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    driver.is_active = False
    driver.save()
    return Response(status=status.HTTP_200_OK)


# <--------- IP OF DRIVER ---------> #


@api_view(['POST'])
def add_driver_ip_address(request):
    """
    Endpoint for adding ip address for given driver name
    :param request:
    :param name:
    :return:
    """
    try:
        driver = Drivers.objects.get(name=request.data['name'])
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {
        'ip_address': request.data['ip_address']
    }

    serializer = DriversSerializer(driver, data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


# <--------- SEND ACTION TO DRIVER ---------> #


@api_view(['POST'])
def send_action(request):
    """
    Endpoint to send request for action to driver
    :param request:
    :return:
    """
    try:
        driver = Drivers.objects.get(name=request.data['name'])
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        result = requests.post(f'http://{driver.ip_address}/', data=1)
        result.raise_for_status()
    except exceptions.NewConnectionError:
        print('Service offline')
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(result)
