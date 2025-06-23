from django import forms
from captcha.fields import CaptchaField

class LoginCaptchaForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()