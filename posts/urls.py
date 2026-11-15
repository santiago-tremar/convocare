from django.urls import path

from .views import (
    FlyerListView,
    FlyerDetailView,
    FlyerFollowingView,
    PosterDetailView,
    ToggleFollowView,
)

urlpatterns = [
    path('<int:pk>/', FlyerDetailView.as_view(), name='flyer_detail'),
    path('', FlyerListView.as_view(), name='flyer_list'),
    path('following/', FlyerFollowingView.as_view(), name='following_flyer_list'),
    path('ps/<int:pk>/', PosterDetailView.as_view(), name='poster_detail'), ## Remember to change this into str:name
    path('ps/<int:pk>/follow/', ToggleFollowView.as_view(), name='toggle_follow'),
]