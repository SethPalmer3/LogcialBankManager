from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(null=True, max_digits=30, decimal_places=2)
    get_bank_account = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class Partition(models.Model):
    owner = models.ManyToManyField(User)
    label = models.CharField(max_length=200)
    current_amount = models.DecimalField(max_digits=20,decimal_places=2, default=0.0)
    def __str__(self):
        return self.label
