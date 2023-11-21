from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import request_started
from .models import *

def update_rules():
    rules = RuleBiopExpression.objects.filter(is_root=True)
    print("updating rules")
    for r in rules:
        with transaction.atomic():
            r.preform_action(_signal_triggered=True)

@receiver(request_started, sender=Partition)
def partiton_check(sender, **kwargs):
    update_rules()

@receiver(post_save, sender=RuleBiopExpression)
def rule_check(sender, **kwargs):
    update_rules()

@receiver(post_save, sender=RuleUniopExpression)
def rule_check(sender, **kwargs):
    update_rules()
