from django.contrib import admin

from partitions.models import RuleBiopExpression, RuleUniopExpression


# Register your models here.
admin.site.register(RuleBiopExpression)
admin.site.register(RuleUniopExpression)
