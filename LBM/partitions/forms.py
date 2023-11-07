from django import forms
from .models import Partition, PartitionRule

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

class EditRule(forms.ModelForm):
    ATTRIBUTE_CHOICES = [
        ('', 'Choose an Attribute'),
        ('init_amount', 'Inital Amount'),
        ('current_amount', 'Current Amount'),
    ]
    CONDITION_CHOICES = [
        ('', 'Choose a choice'),
        ('eq', 'Equals'),
        ('lt', 'Less Than'),
        ('gt', 'Greater Than'),
        ('and', 'And'),
        ('or', 'Or')
    ]
    ACTION_CHOICES = [
        ('', 'Choose an Action'),
        ('fix', 'Fix Amount'),
    ]
    name = forms.CharField(label="Name", max_length=20)
    condition_type = forms.ChoiceField(choices=CONDITION_CHOICES)
    condition_value = forms.CharField(max_length=255)
    condition_value_attribute = forms.ChoiceField(choices=ATTRIBUTE_CHOICES)
    action_type = forms.ChoiceField(choices=ACTION_CHOICES)
    action_value = forms.CharField(label="Action Value", max_length=50)
    class Meta:
        model = PartitionRule
        fields = ['name', 'condition_type', 'condition_value', 'condition_value_attribute', 'action_type', 'action_value']
