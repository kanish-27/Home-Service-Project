from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user_email(user, form.cleaned_data["email"])
        user.save()
