"""
forms.py

Forms for editing/creating/adding partitions, rules, and expressions 

"""

from decimal import Decimal
from django import forms
from django.contrib.auth.models import User

from users.helper_funcs import get_UserProfile
from users.models import UserProfile

from .partition_globals import *
from .models import Partition, RuleBiopExpression

class PartitionEditForm(forms.Form):
    LABEL = 'label'
    CURRENT_AMOUNT = 'current_amount'
    DESCRIPTION = 'description'

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(PartitionEditForm, self).__init__(*args, **kwargs)
        self.fields[self.LABEL] = forms.CharField(max_length=200)
        self.fields[self.CURRENT_AMOUNT] = forms.DecimalField(max_digits=20, decimal_places=2)
        self.fields[self.DESCRIPTION] = forms.CharField(max_length=1000)
        if instance:
            self.fields[self.LABEL].initial = getattr(instance, self.LABEL)
            self.fields[self.CURRENT_AMOUNT].initial = getattr(instance, self.CURRENT_AMOUNT)
            self.fields[self.DESCRIPTION].initial = getattr(instance, self.DESCRIPTION)


class NewPartiton(forms.ModelForm):
    label = forms.CharField(label="Partiton Label", max_length=200)
    current_amount= forms.FloatField(label="Inital Amount")
    description = forms.CharField(label="Partition Description", max_length=1000)
    class Meta:
        model = Partition
        fields = ['label', 'current_amount', 'description']

class RuleExpressionEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        instance: RuleBiopExpression = kwargs.pop('instance', None)
        super(RuleExpressionEditForm, self).__init__(*args, **kwargs)
        if instance is not None and instance.partition is not None:
            if instance.is_root:
                self.fields[FORM_EXPR_NAME] = forms.CharField(label="Rename Rule", initial=instance.label or "", max_length=20)
            elif instance.is_value and instance.value:
                if instance.value.is_reference:
                    init_type = EXPR_TYPE_REF
                else:
                    init_type = EXPR_TYPE_VALUE
                self.fields[IS_VAL_OR_REF] = forms.ChoiceField(label="Value or Reference", initial=init_type, choices=[(EXPR_TYPE_VALUE, "Value"), (EXPR_TYPE_REF, "Reference")])
                self.fields[FORM_VALUE_TYPE] = forms.ChoiceField(choices=UNIOP_VALUE_TYPE_CHOICES, required=False)
                self.fields[FORM_VALUE_INPUT] = forms.CharField(max_length=50, initial=instance.value.get_appropiate_value(), required=False)
                ref_ents = entities_list(get_UserProfile(instance.partition), instance.partition.id)
                ref_attrs = entity_attr_list()
                init_ent = None
                init_attr = None
                if instance.value.is_reference:
                    search_obj = get_type_string(instance.value.reference_id, instance.value.reference_type)
                    if type(search_obj) == UserProfile or type(search_obj) == Partition:
                        init_ent = search_obj.select_string()
                        init_attr = f"{instance.value.reference_type},{instance.value.reference_attr}"
                self.fields[FORM_REF_ENTS] = forms.ChoiceField(label="Enities", initial=init_ent, choices=ref_ents, required=False)
                self.fields[FORM_REF_ATTRS] = forms.ChoiceField(label="Attributes", initial=init_attr, choices=ref_attrs, required=False)

            else:
                self.fields[FORM_OPERATOR] = forms.ChoiceField(choices=[('', 'Select an Operation')] + BIOPS_CHOICES, initial=instance.operator)

class RuleExpressionAddForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        partition_id = kwargs.pop('partition_id', None)
        is_parent = kwargs.pop('is_parent', False)
        
        super(RuleExpressionAddForm, self).__init__(*args, **kwargs)

        self.fields[FORM_OPERATOR] = forms.ChoiceField(choices=BIOPS_CHOICES, required=False)
        if is_parent:
            self.fields[FORM_CHILD_DIR] = forms.ChoiceField(choices=PARENT_EXPR_DIR_CHOICES, required=False)
            self.fields[FORM_EXPR_NAME] = forms.CharField(label="Name Rule", max_length=30, required=False)
        if not is_parent:
            self.fields[FORM_EXPR_TYPE] = forms.ChoiceField(choices=EXPR_TYPE_CHOICES, required=False)
            self.fields[FORM_VALUE_TYPE] = forms.ChoiceField(choices=UNIOP_VALUE_TYPE_CHOICES, required=False)
            self.fields[FORM_VALUE_INPUT] = forms.CharField(required=False)
            if user_id and partition_id:
                ref_ents = entities_list(user_id, partition_id)
                ref_attrs = entity_attr_list()
                self.fields[FORM_REF_ATTRS] = forms.ChoiceField(choices=ref_attrs, required=False)
                self.fields[FORM_REF_ENTS] = forms.ChoiceField(choices=ref_ents, required=False)

def get_transfer_options(part_owner: User) -> list[tuple[str, str]]:
    partitions = Partition.objects.filter(owner=part_owner, is_unallocated=False)
    ret: list[tuple[str, str]] = [('', 'Select a Partiton')]
    for p in partitions:
        ret.append((p.select_string(), p.label))
    return ret

class SetActionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        instance: RuleBiopExpression | None = kwargs.pop('instance', None)
        owner: User | None = kwargs.pop('user', None)

        super(SetActionForm, self).__init__(*args, **kwargs)

        if instance is not None:
            self.fields[FORM_ACTION] = forms.ChoiceField(choices=ACTIONS_CHOICES, initial=instance.action, required=False)
            init_to = execute_or_default(Partition.select_string, "", self=instance.transfer_to)
            self.fields[ACTION_TRANSFER_TO] = forms.ChoiceField(choices=get_transfer_options(instance.partition.owner or owner), initial=init_to, required=False)
            self.fields[ACTION_TRANSFER_AMOUNT] = forms.DecimalField(max_digits=30, decimal_places=2, initial=instance.transfer_amount, required=False)
        else:
            self.fields[FORM_ACTION] = forms.ChoiceField(choices=ACTIONS_CHOICES, required=False)
            if owner:
                self.fields[ACTION_TRANSFER_TO] = forms.ChoiceField(choices=get_transfer_options(owner), required=False)
                self.fields[ACTION_TRANSFER_AMOUNT] = forms.DecimalField(max_digits=30, decimal_places=2, initial=Decimal(0.0), required=False)
