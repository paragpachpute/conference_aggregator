from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list', views.list_venues, name='venues list'),
    path('venue/<str:venue_id>/', views.venue, name='venue'),
]