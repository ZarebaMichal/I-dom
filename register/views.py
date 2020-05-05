# from django.shortcuts import render, redirect
# from .forms import RegisterForm
# from django.http import HttpResponse
#
#
# # Create your views here.
# def register(response):
#     if response.method == "POST":
#         form = RegisterForm(response.POST)
#         if form.is_valid():
#             form.save()
#
#         return redirect('/admin')
#     else:
#         form = RegisterForm()
#
#     return render(response, 'register/register.html', {'form': form})
#
#
# def index(response):
#     return HttpResponse('<h1> Great job mate, you logged in</h1>')

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from register.models import CustomUser
from register.serializer import CustomUserSerializer


@api_view(['GET', 'POST'])
def register_list(request, format=None):
    """
    List all users, or create a new user.
    """
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def register_detail(request, pk, format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
