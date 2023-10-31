from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confrim Passwrd', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords dont\'t match.')
        return cd['password2']

class BankTransferForm(forms.Form):
    def __init__(self, *args, **kwargs):
        bank_accounts = kwargs.pop('bank_accounts', [])
        super().__init__(*args, **kwargs)
        print(bank_accounts)
        CHOICES = [(acc['id'], f"{acc['account_number']} - ${acc['balance']}") for acc in bank_accounts]
        self.fields['from_bank_account'] = forms.ChoiceField(choices=[('', 'Select a Bank Account')] + CHOICES)
        self.fields['to_bank_account'] = forms.ChoiceField(choices=[('', 'Select a Bank Account')] + CHOICES)
        self.fields['amount'] = forms.DecimalField(max_digits=15, decimal_places=2)
