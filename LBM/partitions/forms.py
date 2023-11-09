from django import forms

from .partition_globals import *
from .models import Partition


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

class RuleExpressionEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(RuleExpressionEditForm, self).__init__(*args, **kwargs)
        if instance is not None:
            if instance.is_value:
                    self.fields[IS_VAL_OR_REF] = forms.ChoiceField(label="Value or Reference", choices=[(EXPR_TYPE_VALUE, "Value"), (EXPR_TYPE_REF, "Reference")])
                    self.fields[FORM_VALUE_TYPE] = forms.ChoiceField(choices=UNIOP_VALUE_TYPE_CHOICES, required=False)
                    self.fields[FORM_VALUE_INPUT] = forms.CharField(max_length=50, initial=instance.value.get_appropiate_value(), required=False)
                    if instance.partition.owner.id and instance.partition.id:
                        ref_ents = entities_list(instance.partition.owner.userprofile.id, instance.partition.id)
                        ref_attrs = entity_attr_list()
                        self.fields[FORM_REF_ENTS] = forms.ChoiceField(label="Enities", choices=ref_ents, required=False)
                        self.fields[FORM_REF_ATTRS] = forms.ChoiceField(label="Attributes", choices=ref_attrs, required=False)

            else:
                self.fields[FORM_OPERATOR] = forms.ChoiceField(choices=[('', 'Select an Operation')] + BIOPS_CHOICES)

class RuleExpressionAddForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        partition_id = kwargs.pop('partition_id', None)
        is_parent = kwargs.pop('is_parent', False)
        
        super(RuleExpressionAddForm, self).__init__(*args, **kwargs)

        self.fields[FORM_OPERATOR] = forms.ChoiceField(choices=BIOPS_CHOICES, required=False)
        if is_parent:
            self.fields[FORM_CHILD_DIR] = forms.ChoiceField(choices=PARENT_EXPR_DIR_CHOICES, required=False)
        if not is_parent:
            self.fields[FORM_EXPR_TYPE] = forms.ChoiceField(choices=EXPR_TYPE_CHOICES, required=False)
            self.fields[FORM_VALUE_TYPE] = forms.ChoiceField(choices=UNIOP_VALUE_TYPE_CHOICES, required=False)
            self.fields[FORM_VALUE_INPUT] = forms.CharField(required=False)
            if user_id and partition_id:
                ref_ents = entities_list(user_id, partition_id)
                ref_attrs = entity_attr_list()
                self.fields[FORM_REF_ATTRS] = forms.ChoiceField(choices=ref_attrs, required=False)
                # self.fields['ref_type'] = forms.ChoiceField(choices=self.EXPR_REF_TYPES, required=False)
                self.fields[FORM_REF_ENTS] = forms.ChoiceField(choices=ref_ents, required=False)


