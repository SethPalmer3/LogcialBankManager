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
