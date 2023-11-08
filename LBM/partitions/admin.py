from django.contrib import admin

from partitions.models import Rule, RuleBiopExpression, RuleUniopExpression


# Register your models here.
admin.site.register(Rule)
admin.site.register(RuleBiopExpression)
admin.site.register(RuleUniopExpression)
