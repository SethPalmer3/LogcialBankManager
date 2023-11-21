from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt
import uuid

from users.models import UserProfile
from . import partition_globals as pg


# Create your models here.
class Partition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_unallocated = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label: str = encrypt(models.CharField(max_length=200))
    # TODO: set init_amount on creation
    init_amount = encrypt(models.DecimalField(max_digits=20,decimal_places=2, default=Decimal(0.0)))
    current_amount = encrypt(models.DecimalField(max_digits=20,decimal_places=2, default=Decimal(0.0)))
    description = encrypt(models.CharField(default="", max_length=1000, blank=True))
    frozen = models.BooleanField(default=False)
    objects = models.Manager()
    def __str__(self):
        return f"{self.label}"
    def select_string(self):
        return f"{self.id},{pg.REF_TYPE_PART},{self.label}"
    def transfer(self, other: "Partition", amount: Decimal) -> bool:
        """
        Make transfer if both partitions are able to. Return if transfer was successful
        """
        if amount < Decimal(0.0) or self.frozen or other.frozen:
            return False
        elif self.current_amount >= amount:
            self.current_amount -= amount
            other.current_amount += amount
            self.save()
            other.save()
            return True
        return False

UNIOP_REF_TYPE_CONVERT = {
    'Partition': Partition,
    'User': UserProfile,
}
class RuleUniopExpression(models.Model):
    value_type = encrypt(models.CharField(choices=pg.UNIOP_VALUE_TYPE_CHOICES, max_length=20, null=True, blank=True))
    float_value = encrypt(models.FloatField(null=True, blank=True))
    decimal_value = encrypt(models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True))
    string_value = encrypt(models.CharField(max_length=50, null=True, blank=True))
    int_value = encrypt(models.IntegerField(null=True, blank=True))
    is_reference = models.BooleanField(default=False)
    reference_id = encrypt(models.CharField(max_length=30, null=True, blank=True))
    reference_type = encrypt(models.CharField(max_length=50, null=True, blank=True))
    reference_attr = encrypt(models.CharField(max_length=50, null=True, blank=True))

    def __str__(self):
        return self.get_appropiate_value().__str__()

    def reference_name(self):
        return UNIOP_REF_TYPE_CONVERT[self.reference_type].objects.get(id=self.reference_id).__str__()

    def set_appropiate_value(self, value):
        setattr(self, f"{self.value_type}_value", value) # sets correctly typed value

    def get_appropiate_value(self):
        if self.is_reference:
            try:
                return getattr(UNIOP_REF_TYPE_CONVERT[self.reference_type].objects.get(id=self.reference_id),self.reference_attr)
            except UserProfile.DoesNotExist:
                temp = int(self.reference_id)
                return getattr(UNIOP_REF_TYPE_CONVERT[self.reference_type].objects.get(pk=temp),self.reference_attr)
        else:
            return getattr(self, pg.UNIOP_SELF_ATTRIBUTE_CONVERT[self.value_type])

    def get_type(self):
        return self.value_type


class RuleBiopExpression(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = encrypt(models.CharField(max_length=20, null=True, blank=True))
    partition = models.ForeignKey(to=Partition, null=True, blank=True, on_delete=models.CASCADE)
    left_expr = models.ForeignKey(to="RuleBiopExpression", related_name="left_expression", null=True, blank=True, on_delete=models.SET_NULL)
    right_expr = models.ForeignKey(to="RuleBiopExpression", related_name="right_expression", null=True, blank=True, on_delete=models.SET_NULL)
    is_value = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False)
    value = models.ForeignKey(to=RuleUniopExpression, null=True, blank=True, on_delete=models.SET_NULL)
    operator = encrypt(models.CharField(max_length=20, choices=pg.BIOPS_CHOICES, null=True, blank=True))
    action = encrypt(models.CharField(max_length=20, null=True, blank=True))
    preformed_action = models.BooleanField(default=False)
    transfer_to = models.ForeignKey(to=Partition, related_name="transfer_to", null=True, blank=True, on_delete=models.SET_NULL)
    transfer_amount = models.DecimalField(max_digits=30, decimal_places=2, default=Decimal(0.0))
    objects = models.Manager()
    def __str__(self):
        if self.value is not None and self.is_value:
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

        return pg.BIOPS_CHOICE_FUNCS[self.operator](lv, rv)
    def recursive_delete(self):
        if self.is_value and self.value:
            self.value.delete()
            self.delete()
            return
        else:
            if self.left_expr:
                self.left_expr.recursive_delete()
            if self.right_expr:
                self.right_expr.recursive_delete()
            self.delete()
    def get_root(self) -> 'RuleBiopExpression | None':
        if self.is_root:
            return self
        try:
            parent_expr_left = RuleBiopExpression.objects.get(left_expr=self)
            return parent_expr_left.get_root()
        except RuleBiopExpression.DoesNotExist:
            parent_expr_left = None
        try:
            parent_expr_right = RuleBiopExpression.objects.get(right_expr=self)
            return parent_expr_right.get_root()
        except RuleBiopExpression.DoesNotExist:
            parent_expr_right = None
        return None
    def preform_action(self):
        """
        Preform set action if applicable
        """
        if not self.is_root:
            return
        if self.preformed_action or not self.evaluate():
            return

        if self.action == pg.ACTION_TRANSFER and \
            self.transfer_to and self.partition and \
            self.transfer_amount > Decimal(0.00):
                self.partition.transfer(self.transfer_to, self.transfer_amount)
        elif self.action == pg.ACTION_FREEZE and \
            self.partition:
            self.partition.frozen
            self.partition.save()
        self.preformed_action = True
        self.save()
