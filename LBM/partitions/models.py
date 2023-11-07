from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt
import uuid

# Create your models here.
class Partition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_unallocated = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label = encrypt(models.CharField(max_length=200))
    # TODO: set init_amount on creation
    init_amount = encrypt(models.DecimalField(max_digits=20,decimal_places=2, default=0.0))
    current_amount = encrypt(models.DecimalField(max_digits=20,decimal_places=2, default=0.0))
    description = encrypt(models.CharField(default="", max_length=1000, blank=True))
    objects = models.Manager()
    def __str__(self):
        return f"{self.label}"
