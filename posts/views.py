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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["poster_detail"] = self.object.posted_by
        return context

class PosterDetailView(DetailView):
    """ Poster's About Page. """
    model = Poster
    template_name = 'poster_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flyer_list"] = self.object.flyer_set.all()
        return context