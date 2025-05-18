from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # uses the form with email field
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log in user after signup
            return redirect('home')  # redirect to homepage
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or any other page
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})