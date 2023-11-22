from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser, User
from django.db import models, transaction
from django_cryptography.fields import encrypt
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

from users.models import UserProfile
from . import partition_globals as pg


# Create your models here.
class Partition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_unallocated = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label: str = encrypt(models.CharField(max_length=200))
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
            print("Error transfering")
            return False
        elif self.current_amount >= amount:
            self.current_amount -= amount
            other.current_amount += amount
            self.save()
            other.save()
            return True
        return False

    @classmethod
    def get_users_partitions(cls, owner: AbstractBaseUser | AnonymousUser) -> models.QuerySet:
        """Gets a users partitions, doesn't include the unallocated paritition by default"""
        return cls.objects.filter(owner=owner, is_unallocated=False)

    @classmethod
    def get_users_unallocated_partition(cls, owner: AbstractBaseUser | AnonymousUser) -> "Partition|None":
        """Gets a users unallocated partition if it exists."""
        try:
            unalloc = cls.objects.get(owner=owner, is_unallocated=True)
            return unalloc
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_partition_list_html(cls):
        """Returns a the html of a users partition list."""
        return "partition_list.html"

    @classmethod
    def update_unallocated_partition(cls, owner: AbstractBaseUser | AnonymousUser, total_amount: Decimal) -> tuple["Partition|None", models.QuerySet]:
        partitions = Partition.get_users_partitions(owner=owner)
        diff = pg.check_partitions(partitions, total_amount=total_amount)
        unallocated_partition: Partition|None = Partition.get_users_unallocated_partition(owner=owner)

        if diff is None: # Checks if userprof has a total_amount
            if unallocated_partition is not None:
                unallocated_partition.delete()
                unallocated_partition = None
            return (unallocated_partition, partitions)

        if diff >= 0.0: # checking if partition total is the same or lower than user total
            if unallocated_partition is not None:
                unallocated_partition.current_amount = diff
                unallocated_partition.save()
            else:
                Partition.objects.create(
                    is_unallocated = True,
                    owner = owner,
                    label = "Unallocated",
                    init_amount = Decimal(0.00),
                    current_amount = diff,
                    description = ""
                )
        else: # If the partition allocation is bigger than user total
            if unallocated_partition is not None:
                if unallocated_partition.current_amount + diff >= 0.0:
                    unallocated_partition.current_amount += diff
                    unallocated_partition.save()
                else:
                    unallocated_partition.delete()
                    unallocated_partition = None
        return (unallocated_partition, partitions)
UNIOP_REF_TYPE_CONVERT = {
    'Partition': Partition,
    'User': UserProfile,
}
class RuleUniopExpression(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
            return f"{self.value.__str__()}"
        return f"{self.label}: ({self.left_expr.__str__()} {self.operator} {self.right_expr.__str__()}) = {self.evaluate()}"
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
        if not self.is_root or not self.partition:
            return
        if self.preformed_action or not self.evaluate():
            print(f"didn't preform action for {self.label}")
            return

        if self.action == pg.ACTION_TRANSFER and \
            self.transfer_to and self.partition and \
            self.transfer_amount > Decimal(0.00):
                self.partition.frozen = False
                self.partition.transfer(self.transfer_to, self.transfer_amount)
        elif self.action == pg.ACTION_FREEZE and \
            self.partition:
            self.partition.frozen = True
            self.partition.save()
        self.preformed_action = True
        self.partition.save()
        self.save()

def update_rules():
    rules = RuleBiopExpression.objects.filter(is_root=True)
    for r in rules:
        with transaction.atomic():
            r.preform_action()
            r.save()
            if r.partition:
                r.partition.save()

@receiver(post_save, sender=Partition)
def partiton_check(sender, instance, created, **kwargs):
    updated_fields = kwargs.get('update_fields')
    if kwargs.get('update_fields') and "current_amount" in updated_fields:
        update_rules()

@receiver(post_save, sender=RuleBiopExpression)
def rule_check(sender, instance: RuleBiopExpression, created, **kwargs):
    updated_fields = kwargs.get('update_fields')
    if updated_fields is not None:
        target_value = False
        for a in ['operator', 'action', 'transfer_to', 'transfer_amount']:
            target_value |= (a in updated_fields)
        if target_value:
            update_rules()
            if not instance.evaluate():
                instance.preformed_action = False
            instance.save()

@receiver(post_save, sender=RuleUniopExpression)
def rule_uniop_check(sender, instance, created, **kwargs):
    if not kwargs.get('updated_fields'):
        update_rules()
