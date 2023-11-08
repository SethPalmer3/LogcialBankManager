from django import forms
from django.contrib.admin import display
from django.contrib.auth.models import User
from django.db.models import fields

from users.models import UserProfile
from .models import Partition, Rule, RuleBiopExpression

def rule_entity_stringify(ent_id, ent_type, ent_name, is_current=False):
    value = f"{ent_id},{ent_type},{ent_name}"
    if is_current:
        disp = f"[{ent_type}]: {ent_name}(current)"
    else:
        disp = f"[{ent_type}]: {ent_name}"

    return (value,disp)

def entities_list(user_id, partition_id):
    ret = []
    for p in Partition.objects.filter(owner=user_id): # Get all partitons
        ret.append(rule_entity_stringify(p.id, "Partition", p.label, p.id==partition_id))
    user = User.objects.get(id=user_id)
    userprof = UserProfile.objects.get(user=user)
    ret.append(rule_entity_stringify(userprof.pk, "User", user.username))
    return ret

def operations_list(type_s):
    ret = []
    if type_s == "float":
        ret.append(('eq', 'Equals'))
        ret.append(('lt', 'Less Than'))
        ret.append(('gt', 'Greater Than'))
        ret.append(('lte', 'Less Than or Equal'))
        ret.append(('gte', 'Greater Than or Equal'))
    return ret


def entity_attr_list(ent_type):
    ret = []
    if ent_type == "Partition":
        ret.append(('init_amount', 'Inital Amount'))
        ret.append(('current_amount', 'Current Amount'))
    elif ent_type == "User":
        ret.append(('total_amount', 'Total Amount'))

    return ret

class PartitionEditForm(forms.ModelForm):
    class Meta:
        model = Partition
        fields = ['label', 'current_amount', 'description']

class NewPartiton(forms.ModelForm):
    label = forms.CharField(label="Partiton Label", max_length=200)
    current_amount= forms.FloatField(label="Inital Amount")
    description = forms.CharField(label="Partition Description", max_length=1000)
    class Meta:
        model = Partition
        fields = ['label', 'current_amount', 'description']

class RuleNameAndEntitySelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop("user_id")
        partition_id = kwargs.pop("partition_id")
        entities = entities_list(user_id, partition_id)
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(label="Rule Name", max_length=50)
        self.fields['entity'] = forms.ChoiceField(choices=[('','Select a Entity')] + entities)

class RuleAttributeSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        entity_type = kwargs.pop("ent_type")
        super().__init__(*args, **kwargs)
        entity_attr = entity_attr_list(entity_type)
        self.fields['attribute'] = forms.ChoiceField(choices=[('','Select an Attribute')] + entity_attr)

class RuleOperatorSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        attr_type = kwargs.pop("attr_type")
        super().__init__(*args, **kwargs)
        operations = operations_list(attr_type)
        self.fields['operators'] = forms.ChoiceField(choices=[('', 'Select an Operator')] + operations)

class RuleValueSetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        type_s = kwargs.pop("type_s")
        super().__init__(*args, **kwargs)
        if type_s == "float":
            self.fields['value'] = forms.DecimalField(label="Value", max_digits=15, decimal_places=2)
        if type_s == "str":
            self.fields['value'] = forms.CharField(label="Value", max_length=50)

class RuleExpressionEditForm(forms.Form):
    OPS = [
        ('lt', "Less Than"),
        ('gt', "Greater Than"),
        ('lte', "Less Than or Equal"),
        ('gte', "Greater Than or Equal"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
    ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(RuleExpressionEditForm, self).__init__(*args, **kwargs)
        if instance is not None:
            if instance.is_value:
                if instance.value.value_type == 'float':
                    self.fields['value_input'] = forms.FloatField(initial=instance.value.get_appropiate_value())
                elif instance.value.value_type == 'decimal':
                    self.fields['value_input'] = forms.DecimalField(max_digits=15, decimal_places=2, initial=instance.value.get_appropiate_value())
                elif instance.value.value_type == 'str' or instance.value.value_type == 'string':
                    self.fields['value_input'] = forms.CharField(max_length=50, initial=instance.value.get_appropiate_value())
                elif instance.value.value_type == 'int':
                    self.fields['value_input'] = forms.IntegerField()
                else:
                    self.fields['value_input'] = forms.CharField(max_length=50, initial=instance.value.get_appropiate_value())
            else:
                self.fields['operator'] = forms.ChoiceField(choices=[('', 'Select an Operation')] + self.OPS)

class RuleExpressionAddForm(forms.Form):
    OPS = [
        ('lt', "Less Than"),
        ('gt', "Greater Than"),
        ('lte', "Less Than or Equal"),
        ('gte', "Greater Than or Equal"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
        # ('lt', "Less Than"),
    ]
    UNIOP_TYPES = [
        ('float', 'Float'),
        ('decimal', 'Decimal'),
        ('str', 'String'),
        ('string', 'String'),
        ('int', 'Integer'),
    ]
    expr_type_choices = [
        ('value', 'Value'),
        ('operation', 'Operation'),
    ]
    
    expr_type = forms.ChoiceField(choices=expr_type_choices, required=False)
    value_type = forms.ChoiceField(choices=UNIOP_TYPES, required=False)
    value_input = forms.CharField(required=False)
    operator = forms.ChoiceField(choices=OPS, required=False)

