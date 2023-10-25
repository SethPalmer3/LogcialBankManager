from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AccountHolder, BankAccount

class BankAccoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['account_number', 'balance']

class AccountHolderSerializer(serializers.ModelSerializer):
    bank_accounts = BankAccoutSerializer(many=True, read_only=True)

    class Meta:
        model = AccountHolder
        fields = ['name', 'bank_accounts']
