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

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from register.models import CustomUser
from register.serializer import CustomUserSerializer

@csrf_exempt
def register_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = CustomUser.objects.all()
        serializer = CustomUserSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
