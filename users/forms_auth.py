from django import forms
from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm, LoginForm
from .models import User

class CustomSignupForm(SignupForm):
    """Custom signup form that extends allauth's SignupForm."""
    first_name = forms.CharField(
        max_length=30,
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


class ProviderSignupForm(CustomSignupForm):
    """Custom signup form for service providers."""
    company_name = forms.CharField(
        max_length=100,
        label='Company Name',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Company Name'})
    )
    phone_number = forms.CharField(
        max_length=20,
        label='Phone Number',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
    )

    def save(self, request):
        user = super().save(request)
        user.user_type = 'provider'
        user.save()
        
        # Create provider profile
        from services.models import ProviderProfile
        ProviderProfile.objects.create(
            user=user,
            company_name=self.cleaned_data['company_name'],
            phone_number=self.cleaned_data['phone_number']
        )
        return user


class CustomLoginForm(LoginForm):
    """Custom login form that extends allauth's LoginForm."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autofocus': 'autofocus'
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})
