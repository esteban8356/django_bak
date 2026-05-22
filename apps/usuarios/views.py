'''from django.shortcuts import render

from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
# Create your views here.
'''
## Agrega esto a apps/usuarios/views.py
#CODIGO GENERADO POR CLAUIDA PARA EL ADMIN
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class PerfilView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
        })

class UsuariosListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        usuarios = User.objects.all().values('id', 'username', 'email', 'is_staff')
        return Response(list(usuarios))
