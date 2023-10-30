from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework import generics

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .serializers import  UserSerializer

# from .models import AccountHolder

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope


class UserList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer 

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserSerializer

    def get_object(self):
        if not self.request.user.is_authenticated:
            return None

        obj = get_object_or_404(User, pk=self.request.user.pk)

        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return User.objects.all()

def login_page(request):
    return render(request, 'login.html')
