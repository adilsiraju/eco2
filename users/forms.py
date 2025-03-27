from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username',
                'class': 'form-control',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'class': 'form-control',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Your first name',
                'class': 'form-control',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Your last name',
                'class': 'form-control',
                'autocomplete': 'family-name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the default widgets for password fields
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Confirm password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        
        # Custom help text
        self.fields['email'].help_text = "We'll never share your email with anyone else."
        # Remove default Django help text that will be replaced with our custom UI feedback
        self.fields['password1'].help_text = ""

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'profile_image', 'phone_number', 'address_line1', 'address_line2', 
            'city', 'state', 'postal_code', 'country', 'bio'
        )
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +919876543210'}),
            'address_line1': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, etc. (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Postal/ZIP Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself (max 500 characters)', 'rows': 4}),
        }