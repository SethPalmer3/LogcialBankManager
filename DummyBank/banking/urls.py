from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import AccountHolderDetail, ObatinAuthToken, LoginView, UserDetails, UserList, login_check, login_page

app_name = "banking"
urlpatterns = [
    path('account-holder/<uuid:pk>/', AccountHolderDetail.as_view(), name='account-holder'),
    path('api-token-auth/', ObatinAuthToken.as_view(), name='api_token_auth'),
    path('login/api', LoginView.as_view(), name='api_login'),
    path('login/', login_page, name='login_page'),
    path('login-check/', login_check, name='login_check'),
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetails.as_view(), name='user_primary'),
    path('users/<str:username>/', UserDetails.as_view(), name='user_username'),

]
