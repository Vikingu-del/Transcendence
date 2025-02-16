from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import RegisterView, LoginView, HomeView, LogoutView, GenerateQRCodeView, VerifyOTPView

urlpatterns = [
	path('register/', RegisterView.as_view() , name="register"),
	path('login/', LoginView.as_view(), name="login"),
	path('logout/', LogoutView.as_view(), name='logout'),
	path('home/', HomeView.as_view(), name='home'),
	path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
	path('2fa/qr/', GenerateQRCodeView.as_view(), name='verify_otp'),
	path('2fa/verify/', VerifyOTPView.as_view(), name="verify_otp")
]

