from rest_framework.authtoken.models import Token
from rest_framework.exceptions import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework import generics, serializers
from rest_framework.views import APIView

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .serializers import AccountHolderSerializer

from .models import AccountHolder

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

default_url = 'http://127.0.0.1:8000'

def get_token(user):
    try:
        token = Token.objects.get(user=user)
        token.delete()
    except Token.DoesNotExist:
        pass

    token, created = Token.objects.get_or_create(user=user)
    return token


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
            token = get_token(user)
            accholder = user.account_holder

            return Response({
                'token': token.key,
                'user_id': accholder.id
            })

        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', "first_name", "last_name")

class UserList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def username_view(self, username):
        pass

class LoginView(APIView):
    '''
    View to handle user login and return an auth token
    '''
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            token = get_token(user)
            accholder = user.account_holder
            return Response({'token': token.key, 'user_id': accholder.id})
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


def login_page(request):
    return render(request, 'login.html')


def login_check(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            token = get_token(user)
            accholder = user.account_holder
            next_url = request.POST.get('next', default_url)
            redirect_url = f"{next_url}/login_success/?token={token.key}&user_id={accholder.id}"
            return redirect(redirect_url)
    return render(request, 'login.html')
