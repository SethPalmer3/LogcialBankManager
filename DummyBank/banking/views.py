from django.shortcuts import render
from rest_framework import generics

from .serializers import AccountHolderSerializer

from .models import AccountHolder

# Create your views here.
class AccountHolderDetail(generics.RetrieveAPIView):
    queryset = AccountHolder.objects.all()
    serializer_class = AccountHolderSerializer
