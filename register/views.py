from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from register.models import CustomUser
from register.serializer import CustomUserSerializer, UpdateCustomUserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import json


@api_view(['GET'])
def users_list(request, format=None):
    """
    List all users if ok http 200 response
    """
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_user(request, format=None):
    """
    List all users, or create a new user. If user already
    exists, return 409, if invalid data given, return 400,
    else if succeeded return 201
    """
    # Perhaps there's a prettier way to check if user exists,
    # if so, please update this method.
    # Check if username was given
    try:
        username = request.data['username']
    except KeyError:
        data = {
            'detail': 'You need to provide username to register'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Check if email was given
    try:
        email = request.data['email']
    except KeyError:
        data = {
            'detail': 'You need to provide email to register'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Check if telephone was given
    try:
        telephone = request.data['telephone']
    except KeyError:
        data = {
            'detail': 'You need to provide telephone '
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Striping spaces from telephone number because it's done in serializer, not before
    if telephone:
        telephone.replace(' ', '')
        user1 = CustomUser.objects.filter(username=username)
        user2 = CustomUser.objects.filter(email=email)
        user3 = CustomUser.objects.filter(telephone=telephone)
    else:
        user1 = CustomUser.objects.filter(username=username)
        user2 = CustomUser.objects.filter(email=email)
        user3 = None

    # Check if user with given username already exists
    if user1:
        data = {
            'detail': 'User with given username already exists'
        }
        return Response(data, status=status.HTTP_409_CONFLICT)
    # Check if user with given email already exists
    elif user2:
        data = {
            'detail': 'User with given email already exists'
        }
        return Response(data, status=status.HTTP_409_CONFLICT)
    # Check if user with given telephone already exists
    elif user3:
        data = {
            'detail': 'User with given telephone number already exists'
        }
        return Response(data, status=status.HTTP_409_CONFLICT)
    else:
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_detail(request, username, format=None):
    """
    Retrieve data of user. If user doesn't exist return 404,
    if given invalid data, return 400, else if succeeded return 200
    """
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


@api_view(['PUT'])
def update_user(request, pk, format=None):
    """
    Update user. If user doesn't exist return 404,
    if given invalid data, return 400, else if succeeded return 200
    """
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if 'email' in request.data and 'telephone' in request.data:
        if request.data['telephone']:
            telephone = request.data['telephone']
            telephone.replace(' ', '')

            user1 = CustomUser.objects.filter(email=request.data['email']).count()
            user2 = CustomUser.objects.filter(telephone=request.data['telephone']).count()

        else:
            user1 = CustomUser.objects.filter(email=request.data['email']).count()
            user2 = 0

        if user1 >= 1:
            data = {
                'detail': 'User with given email already exists'
            }

            return Response(data, status=status.HTTP_409_CONFLICT)
        elif user2 >= 1:
            data = {
                'detail': 'User with given phone number already exists'
            }

            return Response(data, status=status.HTTP_409_CONFLICT)
        else:
            serializer = UpdateCustomUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif 'email' in request.data and 'telephone' not in request.data:
        user1 = CustomUser.objects.filter(email=request.data['email']).count()

        if user1 >= 1:
            data = {
                'detail': 'User with given email already exists'
            }

            return Response(data, status=status.HTTP_409_CONFLICT)
        else:
            serializer = UpdateCustomUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif 'email' not in request.data and 'telephone' in request.data:
        if request.data['telephone']:
            telephone = request.data['telephone']
            telephone.replace(' ', '')

            user = CustomUser.objects.filter(telephone=request.data['telephone']).count()

        if user >= 1:
            data = {
                'detail': 'User with given phone number already exists'
            }

            return Response(data, status=status.HTTP_409_CONFLICT)
        else:
            serializer = UpdateCustomUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        serializer = UpdateCustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, pk, format=None):
    """
    Delete user by his ID. Only for admins. If user doesn't exist return 404,
    else if succeeded return 200.
    """
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user.is_active = False
    user.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_user(request, token):
    """
    Delete user's token. If token doesn't exist return 404,
    else if token deleted, return 200
    """
    try:
        token = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    token.delete()
    return Response(status=status.HTTP_200_OK)
