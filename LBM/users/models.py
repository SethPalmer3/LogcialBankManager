import uuid
from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt

#TODO: make description css box bigger

GET_CREDS = 'get_credentials'
GET_ACCS = 'get_accounts'
GET_TRANS = 'transfer'

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank = models.OneToOneField(to="ExternalWebApp", null=True, blank=True, on_delete=models.SET_NULL)
    total_amount = encrypt(models.DecimalField(null=True, blank=True, max_digits=30, decimal_places=2))
    valid_token = models.BooleanField(default=False)
    access_token = encrypt(models.TextField(null=True, blank=True, max_length=30))
    token_type = encrypt(models.TextField(null=True, blank=True, max_length=30))
    last_refreshed = encrypt(models.DateTimeField(null=True, blank=True))
    token_expire_time = encrypt(models.IntegerField(default=0))
    refresh_token = encrypt(models.TextField(null=True, blank=True, max_length=30))


    objects = models.Manager()

    def __str__(self):
        return self.user.username

class ExternalWebApp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    client_key = encrypt(models.CharField(max_length=200))
    secret_key = encrypt(models.CharField(max_length=200))
    get_bank_account = encrypt(models.JSONField(null=True, blank=True))
    objects = models.Manager()

    def __str__(self) -> str:
        return self.name

