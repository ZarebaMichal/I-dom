from django.views.decorators import gzip
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from django.http.response import StreamingHttpResponse, HttpResponse
from cameras.models import Cameras
from cameras.serializer import CamerasSerializer
from turbojpeg import TurboJPEG
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .camera import VideoCamera


def index(request):
    return render(request, 'cameras/home.html')


def gen_frame(cap):
    """
    Function for rendering camera feed frame by frame.
    :param cap:
    :return:
    """
    jpeg = TurboJPEG()
    while cap:
        frame = cap.read()
        convert = jpeg.encode(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n\r\n')


@gzip.gzip_page
def ip_cam(request, pk):
    """
    Render video stream from IP camera, find IP address and create
    VideoCamera instance. Return 404 if camera with given id doesn't exist.
    :param pk: id of IP camera in database. Check if connected to camera
    if not return 503 status response
    :return:
    """
    try:
        camera = Cameras.objects.get(pk=pk)
    except Cameras.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    cap = VideoCamera(ip=camera.ip_address)

    # DevNote: Ask frontend to create 503/500/404 html file
    if cap is None:
        return HttpResponse(status=503)
    else:
        cap.start()
        return StreamingHttpResponse(gen_frame(cap),
                                     content_type='multipart/x-mixed-replace; boundary=frame')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_cameras(request, format=None):
    """
    Get list of all cameras, only for authenticated users
    :param request: GET
    :return: list of all sensors if ok http 200 response
    """
    cameras = Cameras.objects.filter(is_active=True)
    serializer = CamerasSerializer(cameras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=["post"], request_body=CamerasSerializer())
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cameras(request, format=None):
    """
    Add new camera, only for authenticated users
    :param request: POST: name of the camera
    :returns: instance of created camera and 201 HTTP response,
             if failed, 400 HTTP response, if camera with given
             name already exists, 400 HTTP response and expected error
    """

    serializer = CamerasSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camera_detail(request, pk, format=None):
    """
    Retrieve data of camera
    :return: If camera doesn't exist return 404,
            else if succeeded return 200
    """
    try:
        camera = Cameras.objects.get(pk=pk)
    except Cameras.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CamerasSerializer(camera)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_camera(request, pk, format=None):
    """
    Update data of camera
    :param request: PUT
    :param pk: id of camera
    :return: If camera doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        camera = Cameras.objects.get(pk=pk)
    except Cameras.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CamerasSerializer(camera, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_camera(request, pk, format=None):
    """
        Delete camera, change name of the camera to time when deleted,
        change ip address to none and notifications, is active flag to false
        :param request: DELETE
        :param pk: id of camera
        :return: If camera doesn't exist return 404,
                if given invalid data, return 400,
                else if succeeded return 200
        """
    try:
        camera = Cameras.objects.get(pk=pk)
    except Cameras.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    time = str(datetime.now())
    time = time.replace(" ", "")
    camera.name = time
    camera.ip_address = None
    camera.notifications = False
    camera.is_active = False
    camera.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def add_camera_ip_address(request):
    """
    Endpoint for adding ip address for given camera name
    :param request:
    :param pk:
    :return:
    """
    try:
        camera = Cameras.objects.get(name=request.data['name'])
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {
        'ip_address': request.data['ip_address']
    }

    serializer = CamerasSerializer(camera, data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_200_OK)
