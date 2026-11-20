from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """ Custom Model's fields for display. """
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)
        # We are not adding 'can_post' because this is determined by site admin.


class CustomUserChangeForm(UserChangeForm):
    # Used in admin.py
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields