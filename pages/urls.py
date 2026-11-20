from django.urls import path
from django.views.generic import TemplateView

from .views import HomePageView, UserProfileView, PosterRequestView, ContactAdminView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('poster-request/', PosterRequestView.as_view(), name='poster_request'),
    path('poster-request/sent', TemplateView.as_view(template_name='poster_request_complete.html'),
         name='poster_request_complete',
         ),
    path('contact/', TemplateView.as_view(template_name='contact.html'),
         name='contact',
         ),
    path('contact-admins/', ContactAdminView.as_view(), name='contact_admin'),
    path('contact-admins/sent', TemplateView.as_view(template_name='contact_admin_complete.html'),
         name='contact_admin_complete',
         ),
]
