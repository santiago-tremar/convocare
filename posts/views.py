from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.utils import timezone
from django.urls import reverse_lazy

from .models import Poster, Flyer, Announcement
from .forms import FlyerForm

from datetime import timedelta

class FlyerListView(ListView):
    """ Shows all Flyers in the database. """
    model = Flyer
    template_name = 'flyer_list_all.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['flyer_list'] = self.get_queryset().order_by('-upload_date')

        return context


class FlyerFollowingView(LoginRequiredMixin, ListView):
    """ Shows Flyers for Posters the User follows. """
    model = Flyer
    template_name = 'flyer_list_following.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        parish = self.request.user.followed_parish
        groups = self.request.user.followed_groups.all() ## Get all data in this M2M field.

        ## Create list for Group-posted Flyers.
        if not groups.exists():
            context['group_message'] = '¡No estás siguiendo algún grupo en este momento!'
        else:
            followed_groups = list(groups.values_list('pk', flat=True)) # Make a list of group's PKs.
            group_flyers = self.get_queryset().filter(posted_by_id__in=followed_groups).order_by('-upload_date')
            if not group_flyers.exists():
                context['group_message'] = 'Los Grupos que sigues aún no publican Flyers.'
                context['group_announcements'] = Announcement.objects.filter(posted_by_id__in=followed_groups
                                                                                             ).order_by('-upload_date')
            else:
                context['group_flyers'] = group_flyers
                last_week = timezone.now() - timedelta(days=7)
                context['group_announcements'] = Announcement.objects.filter(posted_by_id__in=followed_groups,
                                                                             upload_date__gte=last_week,
                                                                            ).order_by('-upload_date')

        ## Check Parish-posted Flyers.
        if parish is None:
            context['parish_message'] = '¡No estás siguiendo una parroquia!'
        else:
            parish_flyers = self.get_queryset().filter(posted_by=parish)
            if not parish_flyers.exists():
                context['parish_message'] = 'Esta Parroquia todavía no publica Flyers.'
                parish_announcements = Announcement.objects.filter(posted_by=parish)
                if parish_announcements.exists():
                    context["parish_announcements"] = parish_announcements.latest("upload_date")
            else:
                context['parish_flyers'] = parish_flyers
                parish_announcements = Announcement.objects.filter(posted_by=parish)
                if parish_announcements.exists():
                    context["parish_announcements"] = parish_announcements.latest("upload_date")

        return context



class FlyerDetailView(DetailView):
    """ Shows info for a single Flyer. """
    model = Flyer
    template_name = 'flyer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["poster_detail"] = self.object.posted_by # add 'author' to context

        context["target_tags"] = self.object.tags.filter(category='TARGET')
        context["activity_tags"] = self.object.tags.filter(category='ACTIVITY')
        context["organizer_tags"] = self.object.tags.filter(category='ORGANIZER')

        return context

class FlyerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Delete an already posted Flyer. """
    model = Flyer
    success_url = reverse_lazy('flyer_list')

    def test_func(self):
        flyer = self.get_object()
        return (
            self.request.user.can_post
            and self.request.user.poster_for.filter(
                pk=flyer.posted_by_id
            ).exists()
        )

class FlyerEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """ Edit an already posted Flyer. """
    model = Flyer
    template_name = 'flyer_edit.html'
    form_class = FlyerForm

    ## Limit access to users with can_post permission.
    def test_func(self):
        flyer = self.get_object()
        return (
            self.request.user.can_post
            and self.request.user.poster_for.filter(
                pk=flyer.posted_by_id
            ).exists()
        )

    ## Parse only poster_for Posters to the Form.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['posted_by'].queryset = self.request.user.poster_for.all()
        return form

class FlyerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """ Post a new Flyer. """
    model = Flyer
    template_name = "flyer_new.html"
    form_class = FlyerForm

    ## Limit access to users with can_post permission.
    def test_func(self):
        return self.request.user.can_post

    ## Parse only poster_for Posters to the Form.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['posted_by'].queryset = self.request.user.poster_for.all()
        return form


class PosterDetailView(DetailView):
    """ Poster's About Page. """
    model = Poster
    template_name = 'poster_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flyer_list"] = self.object.flyer_set.all().order_by('-upload_date') # add list from ManyToMany relationship

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