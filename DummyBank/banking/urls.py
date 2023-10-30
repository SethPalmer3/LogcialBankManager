from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import  UserDetails, UserList, login_page

app_name = "banking"
urlpatterns = [
    # path('api-token-auth/', ObatinAuthToken.as_view(), name='api_token_auth'),
    path('login/', login_page, name='login_page'),
    path('users/', UserList.as_view(), name='user_list'),
    path('users/me/', UserDetails.as_view(), name='user'),
]
