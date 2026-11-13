from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """ Custom Model's fields for display. """
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)
        # We are not adding 'can_post' because this is determined by site admin.


class CustomUserChangeForm(UserChangeForm):
    # Used in admin.py
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields