from django import forms
from posts.models import Poster
from django.db import models

communication_choices = (
    ('email', 'Correo electrónico'),
    ('whatsapp', 'Whatsapp'),
)

class PosterRequestForm(forms.Form):
    poster_type = forms.ChoiceField(choices=Poster.types, label="Tipo", required=True)
    poster_name = forms.CharField(max_length=255, label="Nombre de la Parroquia/Grupo", required=True)
    address = forms.CharField(max_length=255, label="Dirección de la Parroquia/Grupo", required=True)
    preferred_media = forms.ChoiceField(choices=communication_choices,label="¿Por qué medio prefieres que nos comuniquemos contigo?", required=True,)
    contact = forms.CharField(max_length=100, label="Correo electrónico/Whatsapp", required=True)

class ContactAdminForm(forms.Form):
    """ For users to contact admins. """
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    