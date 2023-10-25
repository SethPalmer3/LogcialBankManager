from rest_framework.authtoken.models import Token
from rest_framework.exceptions import status
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .serializers import AccountHolderSerializer

from .models import AccountHolder

from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        has_perms = obj.user == request.user
        print(obj)
        return has_perms

# Create your views here.
class AccountHolderDetail(generics.RetrieveAPIView):
    queryset = AccountHolder.objects.all()
    serializer_class = AccountHolderSerializer
    permission_classes = [IsAuthenticated, IsOwner]

class ObatinAuthToken(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                token = Token.objects.get(user=user)
                token.delete()
            except Token.DoesNotExist:
                pass

            token, created = Token.objects.get_or_create(user=user)
            accholder = user.account_holder

            return Response({
                'token': token.key,
                'user_id': accholder.id
            })

        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
