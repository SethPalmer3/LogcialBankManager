from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    detail_json = models.JSONField(default=dict)

    def __str__(self):
        return self.user.username

