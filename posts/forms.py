from django import forms

from .models import Flyer, Tag

class FlyerForm(forms.ModelForm):
    """ Custom Form when Creating a new Flyer. """
    target_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(category="TARGET").order_by("name"),
        label="Pensado para: ",
        widget=forms.CheckboxSelectMultiple,
    )
    activity_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(category="ACTIVITY").order_by("name"),
        label="Tipo de actividad: ",
        widget=forms.CheckboxSelectMultiple,
    )
    organizer_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(category="ORGANIZER").order_by("name"),
        label="Organizado por: ",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Flyer
        fields = (
            'event_name',
            'posted_by',
            'image',
            'description',
            'event_date',
            'event_start_time',
            'target_tags',
            'activity_tags',
            'organizer_tags',
        )
        labels = {
            'event_name': 'Título: ',
            'posted_by': 'Publicar en nombre de: ',
            'image': 'Imagen: ',
            'description': 'Descripción: ',
            'event_date': 'Fecha del evento: ',
            'event_start_time': 'Hora de inicio: ',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'event_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'},
            ),
            'event_start_time': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
        }

    def _save_m2m(self):
        super()._save_m2m()
        selected_tags = [
            tag
            for field_name in ("target_tags", "activity_tags", "organizer_tags")
            for tag in self.cleaned_data[field_name]
        ]
        self.instance.tags.set(selected_tags)