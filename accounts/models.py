from django.contrib.auth.models import AbstractUser
from django.db import models
from posts.models import Poster


class CustomUser(AbstractUser):
    """ Custom fields for Users. """
    # Posting ability True/False
    can_post = models.BooleanField(default=False)
    poster_for = models.ManyToManyField(
        Poster,
        blank=True,
    )
    followed_parish = models.ForeignKey(
        Poster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="parish_followers",
        limit_choices_to={"poster_type": "PARISH"},
    )
    followed_groups = models.ManyToManyField(
        Poster,
        blank=True,
        related_name="group_followers",
        symmetrical=False,
        limit_choices_to={"poster_type": "GROUP"},
    )