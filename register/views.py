from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from register.models import CustomUser
from register.serializer import CustomUserSerializer, UpdateCustomUserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated


@api_view(['GET', 'POST'])
def register_list(request, format=None):
    """
    List all users, or create a new user. If user already
    exists, return 409, if invalid data given, return 400,
    else if succeeded return 201
    """
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Perhaps there's a prettier way to check if user exists,
        # if so, please update this method.
        username = request.data['username']
        email = request.data['email']
        telephone = request.data['telephone']

        # Striping spaces from telephone number because it's done in serializer, not before
        if telephone:
            telephone.replace(' ', '')

        user1 = CustomUser.objects.filter(username=username)
        user2 = CustomUser.objects.filter(email=email)
        user3 = CustomUser.objects.filter(telephone=telephone)

        if user1 or user2 or user3:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def register_detail(request, pk, format=None):
    """
    Retrieve or update user. If user doesn't exist return 404,
    if given invalid data, return 400, else if succeeded return 200
    """
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
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
