from django import forms
from django.contrib.auth.models import User
from .models import Partition, UserProfile

class PartitionEditForm(forms.ModelForm):
    class Meta:
        model = Partition
        fields = ['label', 'current_amount']

class NewPartiton(forms.ModelForm):
    label = forms.CharField(label="Partiton Label", max_length=200)
    current_amount= forms.FloatField(label="Inital Amount")
    class Meta:
        model = Partition
        fields = ['label', 'current_amount']


