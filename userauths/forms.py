from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Student No./Staff No.', 'class': 'username-validation'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Removed user_type from the fields

    def clean_username(self):
        username = self.cleaned_data['username']

        if ' ' in username:
            raise ValidationError("Username cannot contain spaces.")

        if len(username) < 5 or len(username) > 9:
            raise ValidationError("Username must be 5 or 9 digits.")
            
        return username
