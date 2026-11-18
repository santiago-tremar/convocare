from django.db import models
from django.urls import reverse

from phonenumber_field.modelfields import PhoneNumberField


class Poster(models.Model):
    """ Define Poster 'accounts' to assign to admin users. """
    types = [
        ('PARISH', 'Parroquia'),
        ('GROUP', 'Grupo'),
    ]

    poster_type = models.CharField(max_length=10, choices=types)
    name = models.CharField(max_length=255)
    bio = models.CharField(max_length=300)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField(blank=True)
    avatar = models.ImageField(upload_to='avatars/',blank=True)
    ## Remember to check Serializer documentation.

    @property
    def poster_users(self):
        usernames = self.customuser_set.values_list("username", flat=True)
        return ", ".join(usernames) or "No users assigned"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("poster_detail", kwargs={"pk": self.pk})


class Flyer(models.Model):
    """ A class for the Flyer images to be shared by admin users. """
    event_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images/")
    description = models.CharField()
    upload_date = models.DateTimeField(auto_now_add=True)
    event_date = models.DateField()
    event_start_time = models.TimeField()
    posted_by = models.ForeignKey(
        Poster,
        on_delete=models.CASCADE,
    )
    

    def __str__(self):
        return f"{self.event_name} by {self.posted_by}"

    def get_absolute_url(self):
        return reverse("flyer_detail", kwargs={"pk":self.pk})

class Announcement(models.Model):
    """ A class for the short Announcements to be shared by admin users. """
    title = models.CharField(max_length=255)
    description = models.CharField()
    upload_date = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(
        Poster,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.title} by {self.posted_by}"

    def get_absolute_url(self):
        return reverse("announcement_detail", kwargs={"pk":self.pk})