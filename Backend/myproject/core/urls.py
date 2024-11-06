from django.urls import path
from .views import secret_view

urlpatterns = [
    path('secret/', secret_view, name='secret'),
]
