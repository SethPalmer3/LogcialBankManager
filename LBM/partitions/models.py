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

# class RuleExpression(models.Model):
#     OPERATOR_CHOICES=[
#         ('add', 'Add'),
#         ('sub', 'Subtract'),
#         ('eq', 'Equals'),
#         ('lt', 'Less Than'),
#         ('gt', 'Greater Than'),
#         ('and', 'And'),
#         ('or', 'Or'),
#         ('identity', 'Value'),
#     ]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     operator = models.CharField(choices=OPERATOR_CHOICES, max_length=50)
#     left_expression = models.OneToOneField(to="RuleExpression",related_name="left_expr", null=True, blank=True, default=None, on_delete=models.CASCADE)
#     right_expression = models.OneToOneField(to="RuleExpression", related_name="right_expr", null=True, blank=True, default=None, on_delete=models.CASCADE)
#     parent_expression = models.OneToOneField(to="RuleExpression", related_name="parent_expr", null=True, blank=True, default=None, on_delete=models.CASCADE)
#     value = encrypt(models.CharField(max_length=100))

#     def evaluate(self):
#         if self.operator == "identity":
#             return self.value
#         else:
#             lv = self.left_expression.evaluate()
#             rv = self.right_expression.evaluate()
#             if lv is None or rv is None:
#                 return None
#             if self.operator == 'add':
#                 return float(lv) + float(rv)
#             if self.operator == 'sub':
#                 return float(lv) - float(rv)
#             if self.operator == 'eq':
#                 return float(lv) == float(rv)
#             if self.operator == 'lt':
#                 return float(lv) < float(rv)
#             if self.operator == 'gt':
#                 return float(lv) > float(rv)
#             if self.operator == 'and':
#                 return bool(lv) and bool(rv)
#             if self.operator == 'or':
#                 return bool(lv) or bool(rv)
#             else:
#                 return None

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
    name = encrypt(models.CharField(max_length=20))
    # condition_value = models.OneToOneField(to=RuleExpression, null=True, blank=True , on_delete=models.CASCADE)
    condition_value = encrypt(models.CharField(max_length=100))
    condition_type = encrypt(models.CharField(max_length=100, choices=CONDITION_CHOICES))
    condition_value_attribute = encrypt(models.CharField(max_length=50, choices=ATTRIBUTE_CHOICES))
    action_type = encrypt(models.CharField(max_length=50, choices=ACTION_CHOICES))
    action_value = encrypt(models.CharField(max_length=50))

    def __str__(self):
        return f"{self.name}"

    def get_partiton(self):
        part = Partition.objects.get(partitionrule=self)
        return part
