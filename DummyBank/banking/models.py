from django.db import models

# Create your models here.

class AccountHolder(models.Model):
    name = models.CharField(max_length=100)

class BankAccount(models.Model):
    holder = models.ForeignKey(AccountHolder, on_delete=models.CASCADE, related_name="bank_accounts")
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
