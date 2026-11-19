from django.urls import path

from .views import (
    FlyerListView,
    FlyerDetailView,
    FlyerFollowingView,
    FlyerDeleteView,
    FlyerEditView,
    FlyerCreateView,
    PosterDetailView,
    ToggleFollowView,
)

urlpatterns = [
    path('<int:pk>/', FlyerDetailView.as_view(), name='flyer_detail'),
    path('<int:pk>/edit/', FlyerEditView.as_view(), name='flyer_edit'),
    path('<int:pk>/delete/', FlyerDeleteView.as_view(), name='flyer_delete'),
    path('', FlyerListView.as_view(), name='flyer_list'),
    path('following/', FlyerFollowingView.as_view(), name='following_flyer_list'),
    path('ps/<int:pk>/', PosterDetailView.as_view(), name='poster_detail'), ## Remember to change this into str:name
    path('ps/<int:pk>/follow/', ToggleFollowView.as_view(), name='toggle_follow'),
    path('new/',FlyerCreateView.as_view(), name='flyer_new'),
]