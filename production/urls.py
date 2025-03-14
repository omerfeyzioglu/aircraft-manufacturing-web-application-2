from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('parts/', views.parts_list, name='parts_list'),
    path('teams/', views.teams_list, name='teams_list'),
    path('aircraft/', views.aircraft_list, name='aircraft_list'),
] 