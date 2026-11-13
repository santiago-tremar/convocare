from django.views.generic import ListView, DetailView

from .models import Poster, Flyer, Announcement

class FlyerListView(ListView):
    """ Shows all Flyers in the database. """
    model = Flyer
    template_name = 'flyer_list_all.html'

class FlyerDetailView(DetailView):
    """ Shows info for a single Flyer. """
    model = Flyer
    template_name = 'flyer_detail.html'