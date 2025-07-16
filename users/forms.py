from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from allauth.account.forms import LoginForm, SignupForm

from .models import UserProfile, UserAddress

User = get_user_model()


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your password')
        })


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            label=_('Email'),
            widget=forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your email')
            })
        )
        self.fields['username'] = forms.CharField(
            max_length=150,
            label=_('Username'),
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Choose a username')
            })
        )
        self.fields['first_name'] = forms.CharField(
            max_length=150,
            label=_('First Name'),
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your first name')
            })
        )
        self.fields['last_name'] = forms.CharField(
            max_length=150,
            label=_('Last Name'),
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your last name')
            })
        )
        self.fields['password1'] = forms.CharField(
            label=_('Password'),
            widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Create a password')
            })
        )
        self.fields['password2'] = forms.CharField(
            label=_('Confirm Password'),
            widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Confirm your password')
            })
        )

    def save(self, request):
        user = super().save(request)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user



class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your first name')})
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your last name')})
    )
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Create a password')}),
    )
    password2 = forms.CharField(
        label=_('Password Confirmation'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm your password')}),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user


class ProviderRegistrationForm(UserRegistrationForm):
    """Form for service provider registration."""
    company_name = forms.CharField(
        label=_('Company Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your company name')})
    )
    phone_number = forms.CharField(
        label=_('Phone Number'),
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your phone number')})
    )
    address = forms.CharField(
        label=_('Business Address'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Enter your business address')}),
        required=False
    )

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ('company_name', 'phone_number', 'address')

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.user_type = 'provider'
        
        if commit:
            user.save()
            
            # Create provider profile
            from services.models import ProviderProfile
            ProviderProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form for user profile."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add profile fields
        profile = getattr(self.instance, 'user_profile', None)
        
        self.fields['bio'] = forms.CharField(
            label=_('Bio'),
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            required=False,
            initial=profile.bio if profile else ''
        )
        self.fields['website'] = forms.URLField(
            label=_('Website'),
            widget=forms.URLInput(attrs={'class': 'form-control'}),
            required=False,
            initial=profile.website if profile else ''
        )
        self.fields['location'] = forms.CharField(
            label=_('Location'),
            max_length=100,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            initial=profile.location if profile else ''
        )
        self.fields['profile_picture'] = forms.ImageField(
            label=_('Profile Picture'),
            widget=forms.FileInput(attrs={'class': 'form-control'}),
            required=False
        )
        if profile and profile.profile_picture:
            self.fields['profile_picture'].initial = profile.profile_picture

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Save profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.bio = self.cleaned_data.get('bio', '')
        profile.website = self.cleaned_data.get('website', '')
        profile.location = self.cleaned_data.get('location', '')
        
        if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
            profile.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            profile.save()
        
        return user


class UserAddressForm(forms.ModelForm):
    """Form for user address."""
    class Meta:
        model = UserAddress
        fields = ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'is_default')
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProviderProfileForm(forms.ModelForm):
    """Form for provider profile."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add provider profile fields
        provider_profile = getattr(self.instance, 'provider_profile', None)
        
        self.fields['company_name'] = forms.CharField(
            label=_('Company Name'),
            max_length=200,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            initial=provider_profile.company_name if provider_profile else ''
        )
        self.fields['description'] = forms.CharField(
            label=_('Description'),
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            required=False,
            initial=provider_profile.description if provider_profile else ''
        )
        self.fields['address'] = forms.CharField(
            label=_('Business Address'),
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            required=False,
            initial=provider_profile.address if provider_profile else ''
        )
        self.fields['profile_picture'] = forms.ImageField(
            label=_('Profile Picture'),
            widget=forms.FileInput(attrs={'class': 'form-control'}),
            required=False
        )
        if provider_profile and provider_profile.profile_picture:
            self.fields['profile_picture'].initial = provider_profile.profile_picture
        
        self.fields['banner_image'] = forms.ImageField(
            label=_('Banner Image'),
            widget=forms.FileInput(attrs={'class': 'form-control'}),
            required=False
        )
        if provider_profile and provider_profile.banner_image:
            self.fields['banner_image'].initial = provider_profile.banner_image
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Save provider profile
        if hasattr(user, 'provider_profile'):
            provider_profile = user.provider_profile
        else:
            from services.models import ProviderProfile
            provider_profile = ProviderProfile(user=user)
        
        provider_profile.company_name = self.cleaned_data.get('company_name', '')
        provider_profile.description = self.cleaned_data.get('description', '')
        provider_profile.address = self.cleaned_data.get('address', '')
        
        if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
            provider_profile.profile_picture = self.cleaned_data['profile_picture']
        
        if 'banner_image' in self.cleaned_data and self.cleaned_data['banner_image']:
            provider_profile.banner_image = self.cleaned_data['banner_image']
        
        if commit:
            provider_profile.save()
        
        return user


class ServiceForm(forms.ModelForm):
    """Form for service creation and editing."""
    class Meta:
        from services.models import Service
        model = Service
        fields = ('name', 'category', 'description', 'price', 'duration', 'is_available')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BookingStatusForm(forms.ModelForm):
    """Form for updating booking status."""
    class Meta:
        from services.models import Booking
        model = Booking
        fields = ('status', 'special_instructions')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Any special instructions...')}),
        }


class ProviderScheduleForm(forms.Form):
    """Form for provider schedule."""
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    day = forms.ChoiceField(
        label=_('Day of Week'),
        choices=DAYS_OF_WEEK,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_time = forms.TimeField(
        label=_('Start Time'),
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    end_time = forms.TimeField(
        label=_('End Time'),
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    is_available = forms.BooleanField(
        label=_('Available'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class PasswordChangeCustomForm(PasswordChangeForm):
    """Custom password change form with better styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Current password')})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': _('New password')})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Confirm new password')})
