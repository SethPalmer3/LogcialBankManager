from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

def update_rules():
    rules = RuleBiopExpression.objects.filter(is_root=True)
    print("Did a signal")
    for r in rules:
        r.preform_action()

@receiver(post_save, sender=Partition)
def partiton_check(sender, instance, created, **kwargs):
    update_rules()

@receiver(post_save, sender=RuleBiopExpression)
def rule_check(sender, instance, created, **kwargs):
    update_rules()

@receiver(post_save, sender=RuleUniopExpression)
def rule_check(sender, instance, created, **kwargs):
    update_rules()
