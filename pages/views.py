from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView

from .forms import PosterRequestForm, ContactAdminForm

from accounts.models import CustomUser


class HomePageView(TemplateView):
    template_name = 'home.html'


class UserProfileView(LoginRequiredMixin, DetailView):
    """ Basic user Profile page. """
    model = CustomUser
    template_name = "page_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

class PosterRequestView(LoginRequiredMixin, FormView):
    """ Allow user to request registry of a new Poster. """
    template_name = "page_can_post_request.html"
    form_class = PosterRequestForm
    success_url = reverse_lazy("poster_request_complete")

    def form_valid(self, form):
        message = render_to_string(
            "emails/create_poster.txt",
            {
                "username": self.request.user.username,
                **form.cleaned_data,
            },
        )
        mail_admins("Solicitud para registrar un nuevo posteador", message)
        return super().form_valid(form)

class ContactAdminView(FormView):
    """ Allow user to contact site admins. """
    template_name = 'contact_admin.html'
    form_class = ContactAdminForm
    success_url = reverse_lazy('contact_admin_complete')

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['username'] = self.request.user.get_username()
            initial['email'] = self.request.user.email
        return initial
    
    def form_valid(self, form):
        message = render_to_string(
            "emails/contact_admins.txt",
            {
                **form.cleaned_data,
            },
        )
        mail_admins(f"Mensaje de {form.cleaned_data['username']}", message)
        return super().form_valid(form)