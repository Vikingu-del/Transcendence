from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)
        return Response({"message": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Logout not successful"}, status=status.HTTP_200_OK)