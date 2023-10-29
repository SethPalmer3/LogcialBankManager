import uuid
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

# Create your models here.


class AccountHolder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(to=User, primary_key=False, on_delete=models.CASCADE, related_name="account_holder", null=True)
    def get_queryset(self):
        return AccountHolder.objects.all()
    def __str__(self) -> str:
        return self.user.username

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    holder = models.ForeignKey(AccountHolder, on_delete=models.CASCADE, related_name="bank_accounts")
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
