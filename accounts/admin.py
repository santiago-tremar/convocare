from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = [
        'email',
        'username',
        'can_post',
        'is_staff',
    ]
    
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('can_post','poster_for',)}),)
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2','can_post','poster_for',),
            },
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)