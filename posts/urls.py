from django.urls import path

from .views import FlyerListView, FlyerDetailView, PosterDetailView

urlpatterns = [
    path('<int:pk>/', FlyerDetailView.as_view(), name='flyer_detail'),
    path('', FlyerListView.as_view(), name='flyer_list'),
    path('ps/<int:pk>/', PosterDetailView.as_view(), name='poster_detail'),
]