from django.contrib import admin
from .models import ExternalWebApp, UserProfile
from partitions.models import Partition

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Partition)
admin.site.register(ExternalWebApp)
