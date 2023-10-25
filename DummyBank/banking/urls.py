from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import AccountHolderDetail, ObatinAuthToken

urlpatterns = [
    path('account-holder/<uuid:pk>/', AccountHolderDetail.as_view(), name='account-holder'),
    path('api-token-auth/', ObatinAuthToken.as_view(), name='api_token_auth')
]
