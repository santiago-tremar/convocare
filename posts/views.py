from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView
from django.views import View

from .models import Poster, Flyer, Announcement

class FlyerListView(ListView):
    """ Shows all Flyers in the database. """
    model = Flyer
    template_name = 'flyer_list_all.html'


class FlyerFollowingView(LoginRequiredMixin, ListView):
    """ Shows Flyers for Posters the User follows. """
    model = Flyer
    template_name = 'flyer_list_following.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        parish = self.request.user.followed_parish
        groups = self.request.user.followed_groups.all() ## Get all data in this M2M field.

        ## Create list of PKs of all followed Posters. Since Groups and Parishes share model,
        ## they will always have unique PKs.
        followed_posters = list(groups.values_list('pk', flat=True))
        if parish is not None:
            followed_posters.append(parish.pk)

        if followed_posters:
            context['flyer_list'] = self.get_queryset().filter(
                posted_by_id__in=followed_posters
            )
        else:
            context['flyer_list'] = self.get_queryset().none()

        return context



class FlyerDetailView(DetailView):
    """ Shows info for a single Flyer. """
    model = Flyer
    template_name = 'flyer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["poster_detail"] = self.object.posted_by # add author to context
        return context


class PosterDetailView(DetailView):
    """ Poster's About Page. """
    model = Poster
    template_name = 'poster_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flyer_list"] = self.object.flyer_set.all() # add list from ManyToMany relationship

        user = self.request.user
        context["is_following"] = False

        ## Behavior change according to Poster Type, due to differing relationship type to User.
        if user.is_authenticated:
            if self.object.poster_type == "PARISH":
                context["is_following"] = user.followed_parish_id == self.object.pk
            elif self.object.poster_type == "GROUP":
                context["is_following"] = user.followed_groups.filter(
                    pk=self.object.pk
                ).exists()

        return context


class ToggleFollowView(LoginRequiredMixin, View):
    """ Allow users to Follow or Unfollow Posters. """
    def post(self, request, pk):
        poster = get_object_or_404(Poster, pk=pk, poster_type__in=('PARISH', 'GROUP'))

        ## Behavior change according to Poster Type, due to differing relationship type to User.
        if poster.poster_type == 'PARISH':
            current_parish = request.user.followed_parish # helper definition

            ## Ask confirmation to follow new Parish if one is already followed.
            if (
                current_parish
                 and current_parish.pk != poster.pk
                 and request.POST.get('confirm') != 'yes'
            ):
               return render(
                   request,
                   'confirm_parish_follow.html',
                   {
                       'current_parish': current_parish,
                       'new_parish': poster,
                   },
               )
            ## Unfollow Parish you already follow, or simply follow.
            if current_parish and current_parish.pk == poster.pk:
               request.user.followed_parish = None
            else:
               request.user.followed_parish = poster
            
            request.user.save(update_fields=['followed_parish'])

        elif poster.poster_type == 'GROUP':
            followed_groups = request.user.followed_groups # helper definition
            if followed_groups.filter(pk=poster.pk).exists():
                followed_groups.remove(poster)
            else:
                followed_groups.add(poster)
        
        return redirect('poster_detail', pk=poster.pk)