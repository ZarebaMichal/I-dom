from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from driver.models import Drivers
from driver.serializer import DriversSerializer, DriversReadOnlySerializer
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators import gzip
from yeelight import Bulb
from yeelight import BulbException
from datetime import datetime
import requests
from urllib3 import exceptions


# <--------- LIST OF DRIVERS ---------> #

@gzip.gzip_page
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_drivers(request):
    """
    Get list of all drivers, only for authenticated users
    :param request: GET
    :return: list of all drivers if ok http 200 response
    """
    driver = Drivers.objects.filter(is_active=True)
    #serializer = DriversSerializer(driver, many=True)
    serializer = DriversReadOnlySerializer(driver, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@gzip.gzip_page
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

@gzip.gzip_page
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

@gzip.gzip_page
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
        Delete driver. Change his name for time of deleting,
        remove IP address and set is_active to false.
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

    time = str(datetime.now())
    time = time.replace(" ", "")

    driver.name = time
    driver.ip_address = None
    driver.is_active = False
    driver.save()
    return Response(status=status.HTTP_200_OK)


# <--------- IP OF DRIVER ---------> #

@gzip.gzip_page
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

@gzip.gzip_page
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

    data = {"data": 1}
    try:
        result = requests.post(f'http://{driver.ip_address}:8000/receive', data=data)
        result.raise_for_status()
    except exceptions.NewConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(result)


@gzip.gzip_page
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_bulb_ip(request, pk):
    """
    Add bulb IP address to database. Requires for user to have bulb turned on.
    :param request:
                    ip_address : IP ADDRESS of bulb
    :return:
            503 if bulb is turned off
            400 if incorrect ip address
            200 if ok
    """
    try:
        driver = Drivers.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {
        'ip_address': request.data['ip_address']
    }

    serializer = DriversSerializer(driver, data=data)
    if serializer.is_valid():
        serializer.save()
        try:
            bulb = Bulb(driver.ip_address)
            bulb.get_properties()
        except BulbException:
            driver.data = False
            driver.save()
            return Response('Could not connect to the bulb', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        driver.data = True
        driver.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def turn_bulb(request, pk):
    """
    Turning on/off bulb. Create instance of bulb and control it
    :param request:
                    flag: str value 'on'/'off'

    :param pk:  int value, primary key of driver id (bulb)

    :return: HTTP 404, if driver doesn't exists,
             HTTP 400, if invalid 'flag' key,
             HTTP 400, if driver is not a bulb,
             HTTP 400, if key is not 'flag'
             HTTP 503, if cannot connect to a bulb,
             HTTP 200, if done correctly.
    """

    try:
        driver = Drivers.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if driver.category != 'bulb':
        return Response('This driver is not a bulb!', status=status.HTTP_400_BAD_REQUEST)

    bulb = Bulb(driver.ip_address)

    try:
        if request.data['flag'] == 'on':
            bulb.turn_on()
            driver.data = True
            driver.save()
        elif request.data['flag'] == 'off':
            bulb.turn_off()
            driver.data = False
            driver.save()
        else:
            return Response('You need to pass on/off value', status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError:
        return Response('You need to provide flag as a key', status=status.HTTP_400_BAD_REQUEST)
    except BulbException:
        driver.data = False
        driver.save()
        return Response('Could not connect to the bulb', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulb_color(request, pk):
    """
    Changing color of bulb. Create instance of bulb, and set RGB color
    :param request:
                    red: int value between 0-255,
                    green: int value between 0-255,
                    blue: int value between 0-255,

    :param pk: int value,  primary key of driver id (bulb)

    :return: HTTP 404, if driver not found,
             HTTP 400, if driver category is not bulb,
             HTTP 503, if cannot connect to bulb,
             HTTP 400, if incorrect RGB values,
             HTTP 400, if values are not integers,
             HTTP 400, if 'red', 'green', 'blue' is not key,
             HTTP 200, if done correctly,
    """

    try:
        driver = Drivers.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if driver.category != 'bulb':
        return Response('This driver is not a bulb!', status=status.HTTP_400_BAD_REQUEST)

    bulb = Bulb(driver.ip_address)

    try:
        red, green, blue = int(request.data['red']), int(request.data['green']), int(request.data['blue'])
    except ValueError:
        return Response('Values should be integers', status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError:
        return Response('You need to provide red, green, blue as a key', status=status.HTTP_400_BAD_REQUEST)

    if (red, green, blue) < (0, 0, 0) or (red, green, blue) > (255, 255, 255):
        return Response('Incorrect RGB values', status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            bulb.set_rgb(red, green, blue)
        except BulbException:
            driver.data = False
            driver.save()
            return Response('Could not connect to the bulb', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulb_brightness(request, pk):
    """
    Changing brightness of bulb.
    :param request:
                    brightness: int value between 0-100

    :param pk:  int value of driver primary key

    :return: HTTP 200, if done correctly,
             HTTP 404, if driver not found,
             HTTP 400, if driver category is not bulb,
             HTTP 400, if brightness is not integer,
             HTTP 400, if brightness not in range (0, 100),
             HTTP 400, if 'brightness' is not a key,
             HTTP 503, if cannot connect to bulb,
    """

    try:
        driver = Drivers.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if driver.category != 'bulb':
        return Response('This driver is not a bulb!', status=status.HTTP_400_BAD_REQUEST)

    bulb = Bulb(driver.ip_address)

    try:
        brightness = int(request.data['brightness'])
    except ValueError:
        return Response('Value should be integer', status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError:
        return Response('You need to provide brightness as a key', status=status.HTTP_400_BAD_REQUEST)

    if 0 <= brightness <= 100:
        try:
            bulb.set_brightness(brightness)
        except BulbException:
            return Response('Could not connect to the bulb', status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response('Brightness should be between 0-100', status=status.HTTP_400_BAD_REQUEST)
