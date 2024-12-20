from django.contrib import admin
from django.urls import path, include
from .views import loginView, logoutView, homeView, chatView

urlpatterns = [
    path('', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('home/', homeView, name='home'),
    path('<str:username>/', chatView, name='chat'),
]