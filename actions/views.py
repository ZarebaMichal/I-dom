from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actions.models import Actions
from actions.serializer import ActionsSerializer
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema


# <--------- LIST OF DRIVERS ---------> #


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_actions(request):
    """
    Get list of all actions, only for authenticated users
    :param request: GET
    :return: list of all actions if ok http 200 response
    """
    action = Actions.objects.filter(is_active=True)
    serializer = ActionsSerializer(action, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def action_detail(request, pk):
    """
    Retrieve data of action
    :return: If action doesn't exist return 404,
            else if succeeded return 200
    """
    try:
        action = Actions.objects.get(pk=pk)
    except Actions.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ActionsSerializer(action)
    return Response(serializer.data)


# <--------- CREATE ACTION ---------> #


@swagger_auto_schema(methods=["post"], request_body=ActionsSerializer())
@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def add_action(request):
    """
    Add new action, only for authenticated users
    :param request: POST: name, days, start_event, action and flag of the driver
    :returns: instance of created action and 201 HTTP response,
             if failed, 400 HTTP response, if action with given
             name already exists, 400 HTTP response and expected error
    """

    serializer = ActionsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        if 'sensor' in serializer.errors:
            return Response({'detail': 'Sensor does not exist'}, status=status.HTTP_404_NOT_FOUND)
        elif 'driver' in serializer.errors:
            return Response({'detail': 'Driver does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <--------- UPDATE DRIVER ---------> #


@api_view(['PUT'])
#@permission_classes([IsAuthenticated])
def update_action(request, pk):
    """
    Update data of action
    :param request: PUT
    :param pk: id of action
    :return: If action doesn't exist return 404,
            if given invalid data, return 400,
            else if succeeded return 200
    """
    try:
        action = Actions.objects.get(pk=pk)
    except Actions.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ActionsSerializer(action, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <--------- DELETE DRIVER ---------> #


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_action(request, pk):
    """
        Delete action
        :param request: DELETE
        :param pk: id of action
        :return: If action doesn't exist return 404,
                if given invalid data, return 400,
                else if succeeded return 200
    """
    try:
        action = Actions.objects.get(pk=pk)
    except Actions.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    time = str(datetime.now())
    time = time.replace(" ", "")
    action.name = time
    action.is_active = False
    action.save()
    return Response(status=status.HTTP_200_OK)

