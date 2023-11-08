from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt
import uuid
from decimal import Decimal

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

class Rule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = encrypt(models.CharField(max_length=50))
    partition= models.ForeignKey(to=Partition, null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)
    entity_id = encrypt(models.CharField(null=True, blank=True, max_length=50))
    entity_type = encrypt(models.CharField(null=True, blank=True, max_length=50))
    entity_name = encrypt(models.CharField(null=True, blank=True, max_length=50))
    attribute = encrypt(models.CharField(null=True, blank=True, max_length=100))
    attribute_type = encrypt(models.CharField(null=True, blank=True, max_length=50))
    operation = encrypt(models.CharField(null=True, blank=True, max_length=10))
    value = encrypt(models.CharField(null=True, blank=True, max_length=50))
    action = encrypt(models.CharField(null=True, blank=True, max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"

class RuleUniopExpression(models.Model):
    UNIOP_TYPES = [
        ('float', 'Float'),
        ('decimal', 'Decimal'),
        ('str', 'String'),
        ('string', 'String'),
        ('int', 'Integer'),
    ]
    value_type = encrypt(models.CharField(choices=UNIOP_TYPES, max_length=20, null=True, blank=True))
    float_value = encrypt(models.FloatField(null=True, blank=True))
    decimal_value = encrypt(models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True))
    string_value = encrypt(models.CharField(max_length=50, null=True, blank=True))
    int_value = encrypt(models.IntegerField(null=True, blank=True))
    def __str__(self):
        return self.get_appropiate_value().__str__()
    def set_appropiate_value(self, value):
        if self.value_type == 'float':
            self.float_value = value
        if self.value_type == 'decimal':
            self.decimal_value = value
        if self.value_type == 'str' or self.value_type == 'string':
            self.string_value = value
        if self.value_type == 'int':
            self.int_value = value
    def get_appropiate_value(self):
        UNIOP_CONVERT = {
            'float': self.float_value,
            'decimal': self.decimal_value,
            'str': self.string_value,
            'string': self.string_value,
            'int': self.int_value
        }
        return UNIOP_CONVERT[self.value_type]
    def get_type(self):
        return self.value_type


class RuleBiopExpression(models.Model):
    OPS = [
        ('lt', "Less Than"),
        ('gt', "Greater Than"),
        ('lte', "Less Than or Equal"),
        ('gte', "Greater Than or Equal"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partition= models.ForeignKey(to=Partition, null=True, blank=True, on_delete=models.CASCADE)
    left_expr = models.ForeignKey(to="RuleBiopExpression", related_name="left_expression", null=True, blank=True, on_delete=models.SET_NULL)
    right_expr = models.ForeignKey(to="RuleBiopExpression", related_name="right_expression", null=True, blank=True, on_delete=models.SET_NULL)
    is_value = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False)
    value = models.ForeignKey(to=RuleUniopExpression, null=True, blank=True, on_delete=models.SET_NULL)
    operator = encrypt(models.CharField(max_length=20, choices=OPS, null=True, blank=True))
    def __str__(self):
        if self.value is not None:
            return self.value.__str__()
        return f"({self.left_expr.__str__()} {self.operator} {self.right_expr.__str__()}) = {self.evaluate()}"
    def evaluate(self):
        if self.value is not None:
            return self.value.get_appropiate_value()
        if self.left_expr is None or self.right_expr is None:
            return None

        lv = self.left_expr.evaluate()
        rv = self.right_expr.evaluate()
        if lv is None or rv is None:
            return None

        if self.operator == "lt":
            return lv < rv
        elif self.operator == "gt":
            return lv > rv
        elif self.operator == "lte":
            return lv <= rv
        elif self.operator == "gte":
            return lv >= rv
        else:
            return None

