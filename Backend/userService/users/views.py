# Login and registration views
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.decorators import login_required

# Friend model
from django.shortcuts import get_object_or_404
from .models import Friend

# Match model
from .models import Match

# CustomUser model
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created {username}!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Profile view
@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    matches = Match.objects.filter(player1=request.user) | Match.objects.filter(player2=request.user)
    return render(request, 'users/profile.html', {'form': form, 'matches': matches})

# Add friend view
@login_required
def add_friend(request, username):
    user = get_object_or_404(CustomUser, username=username)
    Friend.objects.create(user=request.user, friend=user)
    messages.success(request, f'You are now friends with {user.username}!')
    return redirect('profile')