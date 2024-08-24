from django.shortcuts import render
from .models import CustomUser
from .serializers import UserSerializer, UserRegistrationSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
