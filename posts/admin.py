from django.contrib import admin

from .models import Poster, Flyer, Announcement


@admin.register(Poster)
class PosterAdminDisplay(admin.ModelAdmin):
    readonly_fields = ("poster_users",)


admin.site.register(Flyer)
admin.site.register(Announcement)