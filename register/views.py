from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

        return redirect('/admin')
    else:
        form = RegisterForm()

    return render(response, 'register/register.html', {'form': form})


def index(response):
    return HttpResponse('<h1> Great job mate, you logged in</h1>')

