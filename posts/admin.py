from django import forms
from django.contrib import admin

from .models import Poster, Flyer, Announcement, Tag


@admin.register(Poster)
class PosterAdminDisplay(admin.ModelAdmin):
    readonly_fields = ("poster_users",)

## Added by AI Agent.
class FlyerAdminForm(forms.ModelForm):
    class Meta:
        model = Flyer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = [
            (
                category_label,
                [
                    (tag.pk, tag.name)
                    for tag in Tag.objects.filter(category=category_value).order_by("name")
                ],
            )
            for category_value, category_label in Tag.category_types
        ]


@admin.register(Flyer)
class FlyerAdmin(admin.ModelAdmin):
    form = FlyerAdminForm


admin.site.register(Announcement)
admin.site.register(Tag)