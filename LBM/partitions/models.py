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

class PartitionRule(models.Model):
    ATTRIBUTE_CHOICES = [
        ('init_amount', 'Inital Amount'),
        ('current_amount', 'Current Amount'),
    ]
    CONDITION_CHOICES = [
        ('eq', 'Equals'),
        ('lt', 'Less Than'),
        ('gt', 'Greater Than'),
        ('and', 'And'),
        ('or', 'Or')
    ]
    ACTION_CHOICES = [
        ('fix', 'Fix Amount'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partition = models.ForeignKey(to=Partition, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    condition_type = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    condition_value = models.CharField(max_length=255)
    condition_value_attribute = models.CharField(max_length=50, choices=ATTRIBUTE_CHOICES)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    action_value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"

    def get_partiton(self):
        part = Partition.objects.get(partitionrule=self)
        return part
