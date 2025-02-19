from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages #new code
from .models import ChatModel, UserProfileModel
import json

User = get_user_model()

# def loginView(request):
#     if request.method == "POST":
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             user_profile, created = UserProfileModel.objects.get_or_create(user=user)
#             user_profile.online_status = True
#             user_profile.save()
#             # return redirect('home')
#             return redirect('start_game')
#     form = AuthenticationForm()
#     return render(request, 'chat/login.html', {'form': form})

def loginView(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Get 'next' parameter from the URL (where the user was trying to go)
            next_url = request.GET.get('next', 'start_game')  # Default to 'home' if no next URL
            return redirect(next_url)

    form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})


def homeView(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'chat/home.html', context={'users': users})

import json
from django.shortcuts import render

def chatView(request, username):
    user = request.user
    receiver = get_object_or_404(User, username=username)

    if user.id < receiver.id:
        thread_name = f'chat_{user.id}-{receiver.id}'
    else:
        thread_name = f'chat_{receiver.id}-{user.id}'
    messages = ChatModel.objects.filter(thread_name=thread_name)
    users = User.objects.exclude(username=request.user.username)
    context = {
        'users': users,
        'user': user,
        'receiver': receiver,
        'messages': messages,
        'user_json': json.dumps(user.id),
        'receiver_json': json.dumps(receiver.id),
        'username_json': json.dumps(user.username),
        'receiver_username_json': json.dumps(receiver.username)
    }
    return render(request, 'chat/main_chat.html', context)

def logoutView(request):
    if request.user.is_authenticated:
        user_profile = UserProfileModel.objects.get(user=request.user)
        user_profile.online_status = False
        user_profile.save()
        messages.success(request, "You are now logged out!") #new code
        logout(request)
    return redirect('login')

