from django import forms


class LoginForm(forms.Form):

    login = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    target = forms.CharField()
