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
    bank = models.OneToOneField(to="ExternalWebApp", null=True, on_delete=models.SET_NULL)
    total_amount = encrypt(models.DecimalField(null=True, max_digits=30, decimal_places=2))
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

    def get_auth_url(self):
        '''
        WIP
        '''
        return self.get_bank_account[GET_CREDS]['url']

    def get_bank_account_url(self):
        '''
        WIP
        '''
        return self.get_bank_account[GET_ACCS]['url']

    def get_transfer_url(self):
        '''
        WIP
        '''
        return self.get_bank_account[GET_TRANS]['url']

    def construct_credentials_headers(self, username, password):
        '''
        WIP
        '''
        tmp = self.get_bank_account[GET_CREDS]['headers'].copy()
        tmp['grant_type']['username'] = username
        tmp['grant_type']['password'] = password
        tmp['creds']['client'] = self.client_key
        tmp['creds']['secret'] = self.secret_key
        return tmp


