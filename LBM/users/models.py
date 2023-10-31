import uuid
from django.db import models
from django.contrib.auth.models import User

#TODO: make description css box bigger

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank = models.OneToOneField(to="ExternalWebApp", null=True, on_delete=models.SET_NULL)
    total_amount = models.DecimalField(null=True, max_digits=30, decimal_places=2)
    objects = models.Manager()

    def __str__(self):
        return self.user.username

class Partition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_unallocated = models.BooleanField(default=False)
    # owner = models.ManyToManyField(User)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label = models.CharField(max_length=200)
    current_amount = models.DecimalField(max_digits=20,decimal_places=2, default=0.0)
    description = models.CharField(default="", max_length=1000, blank=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.label}"

class ExternalWebApp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    client_key = models.CharField(max_length=200)
    secret_key = models.CharField(max_length=200)
    get_bank_account = models.JSONField(null=True, blank=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return self.name

