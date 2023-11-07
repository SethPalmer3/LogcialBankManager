from django import forms
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
