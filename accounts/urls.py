from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import login_view, home

urlpatterns = [
	path('register/', views.register , name="register"),
	path('login/', login_view, name="login"),
	path('home/', home, name='home'),
	path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh')
]

