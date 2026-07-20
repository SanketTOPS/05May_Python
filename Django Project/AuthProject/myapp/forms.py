from django import forms
from .models import *


class SignupForm(forms.ModelForm):
    class Meta:
        model=Usersignup
        fields='__all__'