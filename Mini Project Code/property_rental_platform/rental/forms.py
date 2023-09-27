from django import forms
from .models import UserProfile
from django.contrib.auth.password_validation import validate_password

import re


class SignupForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['role', 'username', 'email', 'password'] 
        

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Check if a user with the same username or email already exists
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken. Please choose a different one.")

        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered. Please use another email.")
        

        return cleaned_data
    
    
