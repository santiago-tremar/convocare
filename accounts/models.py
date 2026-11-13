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