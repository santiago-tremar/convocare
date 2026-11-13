from django.urls import path

from .views import FlyerListView, FlyerDetailView

urlpatterns = [
    path('<int:pk>/', FlyerDetailView.as_view(), name='flyer_detail'),
    path('', FlyerListView.as_view(), name='flyer_list'),
]