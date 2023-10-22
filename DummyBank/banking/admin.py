from django.contrib import admin

from .models import AccountHolder, BankAccount

# Register your models here.
admin.site.register(AccountHolder)
admin.site.register(BankAccount)
